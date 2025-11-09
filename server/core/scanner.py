import os
import re
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from core.models import Video
from core.db import get_session
from core.config_manager import load_settings

# Formats vidéo pris en charge
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}

def is_video_file(path: Path) -> bool:
    """Vérifie si un fichier est une vidéo."""
    return path.suffix.lower() in VIDEO_EXTENSIONS

def extract_year(title: str) -> int | None:
    """Extrait l'année d'un titre de film (format: 1900-2099)."""
    match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
    return int(match.group(1)) if match else None

def extract_genre(title: str) -> str | None:
    """Tente d'extraire le genre depuis le titre ou le chemin."""
    # Liste de genres communs (à enrichir)
    genres = {
        'action': ['action'],
        'science-fiction': ['sci-fi', 'science.fiction', 'sf'],
        'horreur': ['horror', 'horreur'],
        'comédie': ['comedy', 'comedie', 'comique'],
        'drame': ['drama', 'drame'],
        'thriller': ['thriller'],
        'policier': ['police', 'policier', 'crime'],
        'romance': ['romance', 'romantique'],
        'animation': ['animation', 'anime'],
        'fantastique': ['fantasy', 'fantastique'],
        'documentaire': ['documentary', 'docu']
    }
    
    title_lower = title.lower()
    for genre, keywords in genres.items():
        if any(kw in title_lower for kw in keywords):
            return genre
    return None

def scan_directory(root: Path) -> List[Path]:
    """Scanne récursivement un répertoire et renvoie la liste de tous les fichiers vidéo."""
    found = []
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            full_path = Path(dirpath) / file
            if is_video_file(full_path):
                found.append(full_path)
    return found

def scan_all(settings=None) -> dict:
    """
    Scanne tous les répertoires listés dans settings.yaml
    et met à jour la base de données dynamiquement :
    - Ajoute les nouvelles vidéos
    - Supprime les vidéos dont les fichiers n'existent plus
    
    Retourne un dict avec les statistiques.
    """
    if settings is None:
        settings = load_settings()

    stats = {
        "indexed": 0,
        "removed": 0,
        "total": 0
    }
    
    paths_to_scan = settings.video_directories if hasattr(settings, "video_directories") else []

    if not paths_to_scan:
        print("⚠️ Aucun répertoire défini dans settings.yaml (clé: video_directories).")
        return stats

    with get_session() as session:
        # 1. Nettoyer les fichiers manquants
        all_videos = session.query(Video).all()
        for video in all_videos:
            video_path = Path(video.path)
            if not video_path.exists():
                print(f"🗑️ Suppression : {video.title} (fichier introuvable)")
                session.delete(video)
                stats["removed"] += 1
        
        session.commit()
        
        # 2. Scanner et ajouter les nouveaux fichiers
        found_files = set()
        for root in paths_to_scan:
            root_path = Path(root).expanduser().resolve()
            if not root_path.exists():
                print(f"🚫 Dossier introuvable : {root_path}")
                continue

            print(f"🔍 Scan du dossier : {root_path}")
            for file_path in scan_directory(root_path):
                found_files.add(str(file_path))
                
                # Vérifie si déjà en base
                existing = session.query(Video).filter_by(path=str(file_path)).first()
                if existing:
                    continue

                title = file_path.stem
                full_path_str = str(file_path)
                
                video = Video(
                    title=title,
                    path=full_path_str,
                    duration_seconds=None,
                    year=extract_year(full_path_str),
                    genre=extract_genre(full_path_str),
                    watched=False,
                    last_position=0
                )
                session.add(video)
                stats["indexed"] += 1

        session.commit()
        
        # 3. Compter le total
        stats["total"] = session.query(Video).count()

    print(f"✅ {stats['indexed']} nouvelles vidéos indexées.")
    print(f"🗑️ {stats['removed']} vidéos supprimées (fichiers manquants).")
    print(f"📊 Total : {stats['total']} vidéos en base.")
    
    return stats
