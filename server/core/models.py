from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Index
from .db import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False, index=True)  # Index pour recherche rapide
    size = Column(BigInteger)
    mtime = Column(BigInteger)
    duration_seconds = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True, index=True)  # Index pour filtrage par année
    genre = Column(String, nullable=True, index=True)  # Index pour filtrage par genre
    watched = Column(Boolean, default=False, index=True)  # Index pour filtrage films vus
    last_position = Column(Integer, default=0)  # Position de reprise (en secondes)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Index composites pour optimiser les requêtes fréquentes
    __table_args__ = (
        Index('idx_year_genre', 'year', 'genre'),
        Index('idx_watched_year', 'watched', 'year'),
    )

    def __repr__(self):
        return f"<Video(title='{self.title}', path='{self.path}')>"
