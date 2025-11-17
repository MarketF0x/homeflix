"""
Tests unitaires pour le scanner de fichiers vidéo
"""
import pytest
from pathlib import Path
from core.scanner import (
    is_video_file,
    extract_year,
    extract_genre,
    scan_directory,
    scan_all
)
from core.models import Video


class TestVideoFileDetection:
    """Tests de détection des fichiers vidéo."""
    
    def test_is_video_file_valid_extensions(self):
        """Vérifie que les extensions vidéo valides sont reconnues."""
        valid_files = [
            Path("movie.mp4"),
            Path("movie.mkv"),
            Path("movie.avi"),
            Path("movie.mov"),
            Path("movie.wmv"),
            Path("movie.flv"),
            Path("movie.webm"),
        ]
        for file in valid_files:
            assert is_video_file(file), f"{file.suffix} devrait être reconnu comme vidéo"
    
    def test_is_video_file_invalid_extensions(self):
        """Vérifie que les extensions non-vidéo sont rejetées."""
        invalid_files = [
            Path("document.txt"),
            Path("image.jpg"),
            Path("audio.mp3"),
            Path("subtitle.srt"),
        ]
        for file in invalid_files:
            assert not is_video_file(file), f"{file.suffix} ne devrait pas être une vidéo"
    
    def test_is_video_file_case_insensitive(self):
        """Vérifie que la détection est insensible à la casse."""
        assert is_video_file(Path("movie.MP4"))
        assert is_video_file(Path("movie.MKV"))
        assert is_video_file(Path("movie.AVI"))


class TestYearExtraction:
    """Tests d'extraction de l'année."""
    
    def test_extract_year_valid(self):
        """Vérifie l'extraction d'années valides."""
        assert extract_year("Matrix 1999") == 1999
        assert extract_year("Inception 2010") == 2010
        assert extract_year("The Godfather 1972") == 1972
        assert extract_year("2001 A Space Odyssey") == 2001
    
    def test_extract_year_no_year(self):
        """Vérifie le comportement quand il n'y a pas d'année."""
        assert extract_year("Matrix") is None
        assert extract_year("No Year Here") is None
    
    def test_extract_year_invalid_range(self):
        """Vérifie que les années invalides ne sont pas extraites."""
        assert extract_year("Movie 1080p") is None  # 1080 n'est pas une année valide
        assert extract_year("Movie 720p") is None


class TestGenreExtraction:
    """Tests d'extraction du genre."""
    
    def test_extract_genre_known_genres(self):
        """Vérifie l'extraction de genres connus."""
        assert extract_genre("Action Movie") == "action"
        assert extract_genre("Horror Film") == "horreur"
        assert extract_genre("Comedy Show") == "comédie"
        assert extract_genre("Sci-Fi Adventure") == "science-fiction"
    
    def test_extract_genre_unknown(self):
        """Vérifie le comportement pour les genres inconnus."""
        assert extract_genre("Unknown Genre") is None
        assert extract_genre("Random Title") is None
    
    def test_extract_genre_case_insensitive(self):
        """Vérifie que l'extraction est insensible à la casse."""
        assert extract_genre("ACTION MOVIE") == "action"
        assert extract_genre("comedy show") == "comédie"


class TestDirectoryScanning:
    """Tests du scan de répertoires."""
    
    def test_scan_directory_finds_videos(self, temp_video_dir):
        """Vérifie que le scan trouve les fichiers vidéo."""
        videos = scan_directory(temp_video_dir)
        assert len(videos) == 5  # 5 fichiers vidéo créés dans le fixture
    
    def test_scan_directory_returns_paths(self, temp_video_dir):
        """Vérifie que le scan retourne des objets Path."""
        videos = scan_directory(temp_video_dir)
        assert all(isinstance(v, Path) for v in videos)
    
    def test_scan_directory_empty_dir(self):
        """Vérifie le comportement avec un répertoire vide."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            videos = scan_directory(Path(temp_dir))
            assert len(videos) == 0


class TestFullScan:
    """Tests du scan complet avec base de données."""
    
    def test_scan_all_adds_new_videos(self, db_session, sample_settings, temp_video_dir):
        """Vérifie que le scan ajoute de nouvelles vidéos."""
        stats = scan_all(sample_settings)
        
        assert stats['indexed'] == 5  # 5 vidéos dans temp_video_dir
        assert stats['total'] == 5
        
        # Vérifie que les vidéos sont en base
        videos = db_session.query(Video).all()
        assert len(videos) == 5
    
    def test_scan_all_removes_missing_files(self, db_session, sample_videos, sample_settings):
        """Vérifie que le scan supprime les fichiers manquants."""
        # Les sample_videos ont des chemins qui n'existent pas
        initial_count = db_session.query(Video).count()
        assert initial_count == 3
        
        stats = scan_all(sample_settings)
        
        # Tous les anciens fichiers devraient être supprimés
        assert stats['removed'] == 3
    
    def test_scan_all_no_directories(self, db_session):
        """Vérifie le comportement quand aucun répertoire n'est configuré."""
        from core.config_manager import Settings
        settings = Settings(video_directories=[])
        
        stats = scan_all(settings)
        
        assert stats['indexed'] == 0
        assert stats['removed'] == 0
        assert stats['total'] == 0
    
    def test_scan_all_nonexistent_directory(self, db_session):
        """Vérifie le comportement avec un répertoire inexistant."""
        from core.config_manager import Settings
        settings = Settings(video_directories=["C:/NonExistent/Path"])
        
        stats = scan_all(settings)
        
        assert stats['indexed'] == 0
        assert stats['total'] == 0
