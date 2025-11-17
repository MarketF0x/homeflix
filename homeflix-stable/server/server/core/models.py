from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Float, Text, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
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
    last_position_updated = Column(DateTime, nullable=True)  # Date de dernière mise à jour de la position
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Métadonnées TMDb
    overview = Column(Text, nullable=True)  # Synopsis/Description du film
    vote_average = Column(Float, nullable=True)  # Note moyenne TMDb (sur 10)
    cast = Column(String, nullable=True)  # Acteurs principaux (séparés par virgules)
    poster_path = Column(String, nullable=True)  # Chemin de l'affiche TMDb
    
    # Collections et épisodes (pour sagas et séries)
    collection = Column(String, nullable=True, index=True)  # Nom de la saga/série (ex: "Harry Potter", "Matrix")
    episode_number = Column(Integer, nullable=True)  # Numéro dans la saga/série (1, 2, 3...)
    
    # Index composites pour optimiser les requêtes fréquentes
    __table_args__ = (
        Index('idx_year_genre', 'year', 'genre'),
        Index('idx_watched_year', 'watched', 'year'),
        Index('idx_collection_episode', 'collection', 'episode_number'),  # Pour tri des sagas
    )

    def __repr__(self):
        return f"<Video(title='{self.title}', path='{self.path}')>"


class Profile(Base):
    """Profils utilisateurs pour gestion multi-comptes"""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    is_main = Column(Boolean, default=False, nullable=False, index=True)
    restrictions = Column(Text, nullable=True)  # JSON des restrictions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    password_hash = Column(String, nullable=True)
    security_question = Column(String, nullable=True)
    security_answer = Column(String, nullable=True)

    def __repr__(self):
        return f"<Profile(name='{self.name}', is_main={self.is_main})>"


class WatchProgress(Base):
    """Gestion de la progression de lecture par profil utilisateur"""
    __tablename__ = "watch_progress"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)  # Position en secondes
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    
    # Index composite pour la contrainte d'unicité et les requêtes
    __table_args__ = (
        UniqueConstraint('profile_id', 'video_id', name='uq_profile_video'),
        Index('idx_watch_progress_profile', 'profile_id'),
        Index('idx_watch_progress_video', 'video_id'),
        Index('idx_watch_progress_updated', 'updated_at'),
    )

    def __repr__(self):
        return f"<WatchProgress(profile_id={self.profile_id}, video_id={self.video_id}, position={self.position})>"
