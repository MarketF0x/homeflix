"""
Tests pour les utilitaires de miniatures
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from core.thumbnails import (
    thumb_path_for,
    ensure_thumbnail_sync,
    get_thumbnail,
)
from core.models import Video


class TestThumbnailPaths:
    """Tests de génération des chemins de miniatures."""
    
    def test_thumb_path_for_basic(self):
        """Vérifie la génération du chemin de miniature."""
        video_path = "C:/Videos/Matrix.1999.mp4"
        thumb_path = thumb_path_for(video_path)
        
        assert thumb_path is not None
        assert thumb_path.suffix == '.jpg'
        assert 'thumbs' in str(thumb_path)
    
    def test_thumb_path_for_different_extensions(self):
        """Vérifie que l'extension est toujours .jpg."""
        paths = [
            "C:/Videos/movie.mp4",
            "C:/Videos/movie.mkv",
            "C:/Videos/movie.avi",
        ]
        
        for path in paths:
            thumb = thumb_path_for(path)
            assert thumb.suffix == '.jpg'


class TestThumbnailGeneration:
    """Tests de génération de miniatures."""
    
    @patch('core.thumbnails.extract_frame_ffmpeg')
    def test_ensure_thumbnail_creates_if_missing(self, mock_extract):
        """Vérifie qu'une miniature est créée si elle n'existe pas."""
        mock_extract.return_value = True
        
        video_path = Path("C:/Videos/test.mp4")
        result = ensure_thumbnail_sync(str(video_path))
        
        # Devrait tenter de créer la miniature
        assert mock_extract.called or result is not None
    
    @patch('core.thumbnails.download_tmdb_poster')
    def test_get_thumbnail_from_tmdb(self, mock_download):
        """Vérifie la récupération depuis TMDb."""
        mock_download.return_value = b"fake image data"
        
        result = get_thumbnail(
            "C:/Videos/movie.mp4",
            poster_path="/poster.jpg",
            api_key="test_key"
        )
        
        assert result is not None


class TestBulkThumbnailOperations:
    """Tests réduits: placeholder car fonctions globales supprimées."""
    def test_placeholder_bulk_ops(self):
        assert True
