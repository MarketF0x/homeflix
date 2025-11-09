"""
Configuration pytest pour les tests HomeOne
Fixtures partagées pour tous les tests
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from core.db import Base, get_session
from core.models import Video
from core.config_manager import Settings
from main import app


@pytest.fixture(scope="function")
def test_db():
    """Crée une base de données SQLite en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_session():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_session] = override_get_session
    
    yield TestingSessionLocal
    
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Retourne une session de base de données pour les tests."""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Client de test FastAPI."""
    return TestClient(app)


@pytest.fixture(scope="function")
def temp_video_dir():
    """Crée un répertoire temporaire avec des fichiers vidéo de test."""
    temp_dir = tempfile.mkdtemp()
    video_dir = Path(temp_dir) / "videos"
    video_dir.mkdir()
    
    # Créer des fichiers vidéo fictifs
    test_videos = [
        "Matrix.1999.1080p.BluRay.x264.mp4",
        "Inception.2010.720p.WEB-DL.mp4",
        "The.Godfather.1972.mkv",
        "Breaking.Bad.S01E01.Pilot.720p.mkv",
        "Friends.S01E01.The.One.Where.Monica.Gets.a.Roommate.avi",
    ]
    
    for video_name in test_videos:
        video_path = video_dir / video_name
        video_path.write_bytes(b"fake video content")
    
    yield video_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def sample_settings(temp_video_dir):
    """Settings de test avec un répertoire temporaire."""
    return Settings(
        video_directories=[str(temp_video_dir)],
        min_film_minutes=75,
        max_series_minutes=55,
        session_mode="mixed",
        tmdb_api_key="test_api_key",
        auto_clean_filenames=True,
        language="fr"
    )


@pytest.fixture(scope="function")
def sample_videos(db_session):
    """Crée des vidéos de test dans la base de données."""
    videos = [
        Video(
            path="C:/Videos/Matrix.1999.mp4",
            title="Matrix",
            size=1500000000,
            mtime=1234567890,
            duration_seconds=8100,
            year=1999,
            genre="Science-Fiction",
            watched=False,
            last_position=0
        ),
        Video(
            path="C:/Videos/Inception.2010.mp4",
            title="Inception",
            size=2000000000,
            mtime=1234567890,
            duration_seconds=8880,
            year=2010,
            genre="Action",
            watched=True,
            last_position=3000
        ),
        Video(
            path="C:/Videos/Breaking.Bad.S01E01.mp4",
            title="Breaking Bad S01E01",
            size=500000000,
            mtime=1234567890,
            duration_seconds=2700,
            year=2008,
            genre="Drame",
            watched=False,
            last_position=0
        ),
    ]
    
    for video in videos:
        db_session.add(video)
    db_session.commit()
    
    return videos
