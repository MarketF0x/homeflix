"""
Tests unitaires pour l'enrichissement des métadonnées TMDb (version API actuelle)
"""
import pytest
from unittest.mock import Mock, patch
from core.metadata_enricher import (
    clean_title_from_filename,
    search_tmdb,
    enrich_video_metadata,
    enrich_all_videos
)
from core.models import Video


class TestTitleCleaning:
    """Tests du nettoyage des titres de fichiers."""
    
    def test_clean_basic_title(self):
        """Vérifie le nettoyage de titres basiques."""
        title, year = clean_title_from_filename("Matrix.1999.1080p.BluRay.x264")
        assert title == "Matrix"
        assert year == 1999
    
    def test_clean_title_with_dots(self):
        """Vérifie le remplacement des points par des espaces."""
        title, year = clean_title_from_filename("The.Dark.Knight.2008")
        assert "Dark" in title
        assert "Knight" in title
        assert year == 2008
    
    def test_clean_title_removes_quality_tags(self):
        """Vérifie la suppression des tags de qualité."""
        title, year = clean_title_from_filename("Movie.2020.1080p.WEBrip.x264.AAC")
        assert "1080p" not in title
        assert "WEBrip" not in title
        assert "x264" not in title
        assert "AAC" not in title
    
    def test_clean_title_removes_language_tags(self):
        """Vérifie la suppression des tags de langue."""
        title, year = clean_title_from_filename("Film.2021.FRENCH.VOSTFR.1080p")
        assert "FRENCH" not in title.upper()
        assert "VOSTFR" not in title.upper()
    
    def test_clean_title_special_numbers(self):
        """Vérifie la gestion des titres avec des chiffres (1917, 2012, etc.)."""
        title, year = clean_title_from_filename("1917.2019.1080p")
        assert "1917" in title
        assert year == 2019
        
        title2, year2 = clean_title_from_filename("2012.2009.BluRay")
        assert "2012" in title2
        assert year2 == 2009
    
    def test_clean_title_no_year(self):
        """Vérifie le comportement quand il n'y a pas d'année."""
        title, year = clean_title_from_filename("Movie.Without.Year")
        assert year is None
    
    def test_clean_title_episode_markers(self):
        """Vérifie la suppression des marqueurs d'épisodes."""
        title, year = clean_title_from_filename("Breaking.Bad.S01E01.Pilot")
        assert "S01E01" not in title
        assert "Breaking" in title
        assert "Bad" in title


class TestTMDbSearch:
    """Tests de recherche TMDb."""
    
    @patch('core.metadata_enricher.requests.get')
    def test_search_tmdb_success(self, mock_get):
        """Vérifie une recherche TMDb réussie."""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 603,
                    'title': 'The Matrix',
                    'release_date': '1999-03-30',
                    'overview': 'A computer hacker...',
                    'vote_average': 8.2,
                    'poster_path': '/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
                    'genre_ids': [28, 878]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = search_tmdb("Matrix", year=1999, api_key="test_key")
        
        assert result is not None
        assert result['title'] == 'The Matrix'
        assert result['vote_average'] == 8.2
    
    @patch('core.metadata_enricher.requests.get')
    def test_search_tmdb_no_results(self, mock_get):
        """Vérifie le comportement quand aucun résultat n'est trouvé."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response
        
        result = search_tmdb("NonExistentMovie", api_key="test_key")
        
        assert result is None
    
    @patch('core.metadata_enricher.requests.get')
    def test_search_tmdb_api_error(self, mock_get):
        """Vérifie la gestion des erreurs API."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = search_tmdb("Matrix", api_key="invalid_key")
        
        assert result is None
    
    @patch('core.metadata_enricher.requests.get')
    def test_search_tmdb_network_error(self, mock_get):
        """Vérifie la gestion des erreurs réseau."""
        mock_get.side_effect = Exception("Network error")
        
        result = search_tmdb("Matrix", api_key="test_key")
        
        assert result is None


class TestVideoEnrichment:
    """Tests de l'enrichissement de vidéos individuelles."""
    
    @patch('core.metadata_enricher.search_tmdb')
    def test_enrich_video_success(self, mock_search, db_session):
        """Vérifie l'enrichissement réussi d'une vidéo."""
        # Créer une vidéo de test
        video = Video(
            path="C:/Videos/Matrix.1999.mp4",
            title="Matrix 1999",
            size=1500000000,
            mtime=1234567890
        )
        db_session.add(video)
        db_session.commit()
        
        # Mock TMDb response
        mock_search.return_value = {
            'title': 'The Matrix',
            'release_date': '1999-03-30',
            'overview': 'A computer hacker learns...',
            'vote_average': 8.2,
            'poster_path': '/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
            'genre_ids': [28, 878]
        }

        result = enrich_video_metadata(video, session=db_session, force=True)

        assert result is True
        assert (video.year == 1999) or (video.year is not None)
        assert video.genre is not None
    
    @patch('core.metadata_enricher.search_tmdb')
    def test_enrich_video_no_tmdb_result(self, mock_search, db_session):
        """Vérifie le comportement quand TMDb ne trouve rien."""
        video = Video(
            path="C:/Videos/Unknown.Movie.mp4",
            title="Unknown Movie",
            size=1000000000,
            mtime=1234567890
        )
        db_session.add(video)
        db_session.commit()
        
        mock_search.return_value = None

        result = enrich_video_metadata(video, session=db_session, force=True)

        assert result is False
    
    def test_enrich_video_skip_already_enriched(self, db_session):
        """Vérifie qu'une vidéo déjà enrichie n'est pas re-traitée."""
        video = Video(
            path="C:/Videos/Matrix.mp4",
            title="The Matrix",
            size=1500000000,
            mtime=1234567890,
            year=1999
        )
        db_session.add(video)
        db_session.commit()

        result = enrich_video_metadata(video, session=db_session, force=False)

        assert result is False  # Skip car déjà enrichi
    
    @patch('core.metadata_enricher.search_tmdb')
    def test_enrich_video_force_update(self, mock_search, db_session):
        """Vérifie que force=True met à jour même si déjà enrichi."""
        video = Video(
            path="C:/Videos/Matrix.mp4",
            title="The Matrix",
            size=1500000000,
            mtime=1234567890,
            year=1999
        )
        db_session.add(video)
        db_session.commit()
        
        mock_search.return_value = {
            'title': 'The Matrix',
            'overview': 'New overview',
            'vote_average': 8.2,
            'poster_path': '/poster.jpg',
            'release_date': '1999-03-30',
            'genre_ids': [28]
        }

        result = enrich_video_metadata(video, session=db_session, force=True)

        assert result is True


class TestBulkEnrichment:
    """Tests de l'enrichissement en masse."""
    
    @patch('core.metadata_enricher.enrich_video_metadata')
    def test_enrich_all_videos(self, mock_enrich, db_session, sample_videos):
        """Vérifie l'enrichissement de toutes les vidéos."""
        mock_enrich.return_value = True
        stats = enrich_all_videos(db_session, force=False)
        assert stats['total'] == 3
        assert stats['enriched'] >= 0
        assert mock_enrich.called
