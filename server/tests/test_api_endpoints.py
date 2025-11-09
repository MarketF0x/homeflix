"""
Tests d'intégration pour les endpoints de l'API FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from core.models import Video
from unittest.mock import patch


class TestVideoEndpoints:
    """Tests des endpoints vidéo."""

    def test_get_all_videos(self, client, sample_videos):
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert 'videos' in data
        assert len(data['videos']) == 3
    
    def test_get_videos_filter_by_mode_films(self, client, sample_videos):
        """Test filtrage par mode films."""
        response = client.get("/api/videos?mode=films")
        assert response.status_code == 200
        data = response.json()
        # Les films ont duration > 75 minutes
        for video in data['videos']:
            assert (video.get('duration_seconds') or 0) > 75 * 60
    
    def test_get_videos_filter_by_mode_series(self, client, sample_videos):
        """Test filtrage par mode séries."""
        response = client.get("/api/videos?mode=series")
        assert response.status_code == 200
        data = response.json()
        # Les séries ont 20 < duration < 55 minutes
        for video in data['videos']:
            if video.get('duration_seconds'):
                duration_min = video['duration_seconds'] / 60
                assert 20 < duration_min < 55
    
    def test_get_random_video(self, client, sample_videos):
        response = client.get("/api/random")
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'title' in data
    
    def test_get_random_video_empty_db(self, client):
        # Pas de sample_videos => DB vide
        response = client.get("/api/random")
        assert response.status_code == 404
    
    def test_update_video_metadata(self, client, sample_videos):
        """Test POST /api/video/update."""
        video_id = sample_videos[0].id
        response = client.post(
            "/api/video/update",
            json={"id": video_id, "watched": True, "last_position": 5000}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert data['watched'] is True
        assert data['last_position'] == 5000
    
    def test_update_video_not_found(self, client):
        """Test mise à jour d'une vidéo inexistante."""
        response = client.post(
            "/api/video/update",
            json={
                "id": 99999,
                "watched": True
            }
        )
        assert response.status_code == 404


class TestCategoryEndpoints:
    """Tests des endpoints de catégories."""

    def test_get_categories(self, client, sample_videos):
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert 'carousel' in data
        assert 'by_year' in data
        assert 'by_genre' in data
        assert 'to_resume' in data
        assert 'watched' in data
    
    def test_get_categories_filter_mode(self, client, sample_videos):
        """Test filtrage des catégories par mode."""
        response = client.get("/api/categories?mode=films")
        assert response.status_code == 200
        data = response.json()
        
        # Vérifie que seuls les films sont retournés
        for category_videos in data.values():
            if isinstance(category_videos, list):
                for video in category_videos:
                    if video.get('duration_seconds'):
                        assert video['duration_seconds'] > 75 * 60
    
    def test_years_present_in_categories(self, client, sample_videos):
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        years = set(map(int, data.get('by_year', {}).keys()))
        assert any(y in years for y in [1999, 2010, 2008])
    
    def test_genres_present_in_categories(self, client, sample_videos):
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        genres = set(g.lower() for g in data.get('by_genre', {}).keys())
        assert any(g in genres for g in ["science-fiction", "action", "drame"])


class TestScanEndpoints:
    """Tests des endpoints de scan."""
    
    def test_scan_trigger(self, client, sample_settings):
        """Test POST /api/scan."""
        with patch('core.scanner.scan_all') as mock_scan:
            mock_scan.return_value = {
                'indexed': 5,
                'removed': 0,
                'total': 5
            }
            
            response = client.post("/api/scan")
            assert response.status_code == 200
            data = response.json()
            assert data['indexed'] == 5
            assert data['total'] == 5


class TestThumbnailEndpoints:
    """Tests des endpoints de miniatures."""
    
    def test_get_thumbnail_missing_path(self, client):
        """Test GET /api/thumbnail sans paramètre path."""
        response = client.get("/api/thumbnail")
        assert response.status_code == 422  # Validation error
    
    def test_get_thumbnail_nonexistent_file(self, client):
        """Test miniature pour un fichier inexistant."""
        response = client.get("/api/thumbnail?path=C:/Nonexistent/file.mp4")
        # Devrait retourner une image par défaut ou 404
        assert response.status_code in [200, 404]
    
    def test_generate_all_thumbnails(self, client):
        """Test POST /api/thumbnails/generate."""
        response = client.post("/api/thumbnails/generate", json={"force": False})
        assert response.status_code == 200
        data = response.json()
        assert 'generated' in data
    
    def test_repair_thumbnails(self, client):
        """Test POST /api/thumbnails/repair."""
        response = client.post("/api/thumbnails/repair")
        assert response.status_code == 200
        data = response.json()
        assert 'generated' in data or 'missing' in data


class TestSettingsEndpoints:
    """Tests des endpoints de configuration."""
    
    def test_get_settings(self, client):
        """Test GET /api/settings."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert 'video_directories' in data
        assert 'session_mode' in data
        assert 'language' in data
    
    def test_update_settings(self, client):
        """Test POST /api/settings."""
        new_settings = {
            'video_directories': ['C:/NewPath'],
            'language': 'en'
        }
        
        response = client.post("/api/settings", json=new_settings)
        assert response.status_code == 200
        data = response.json()
        assert data['language'] == 'en'


class TestMetadataEndpoints:
    """Tests des endpoints d'enrichissement métadonnées."""
    
    def test_enrich_metadata(self, client):
        """Test POST /api/metadata/enrich."""
        with patch('core.metadata_enricher.enrich_all_videos') as mock_enrich:
            mock_enrich.return_value = {'total': 10, 'enriched': 8, 'failed': 2}
            
            response = client.post("/api/metadata/enrich")
            assert response.status_code == 200
            data = response.json()
            assert data['enriched'] == 8
    
    def test_enrich_metadata_force(self, client):
        """Test enrichissement forcé."""
        with patch('core.metadata_enricher.enrich_all_videos') as mock_enrich:
            mock_enrich.return_value = {'total': 10, 'enriched': 10, 'failed': 0}
            
            response = client.post("/api/metadata/enrich?force=true")
            assert response.status_code == 200
            data = response.json()
            assert data['enriched'] == 10
