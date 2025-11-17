import os
import re
from pathlib import Path
from typing import List
from core.logger import logger, log_exception
import string
from sqlalchemy.orm import Session
from core.models import Video
from core.db import get_session
from core.config_manager import load_settings

# Formats vidéo pris en charge
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}

# Dossiers à ignorer lors de la détection automatique
IGNORED_DIRS = {
    'windows', 'program files', 'program files (x86)', 'programdata',
    'appdata', 'system32', 'temp', '$recycle.bin', 'recovery',
    'node_modules', '.git', '.venv', '__pycache__', 'cache'
}

def auto_detect_video_directories(max_depth: int = 3, min_videos: int = 5) -> List[str]:
    """
    Détecte automatiquement les répertoires contenant des vidéos.
    
    Args:
        max_depth: Profondeur maximale de recherche dans les dossiers
        min_videos: Nombre minimum de vidéos pour qu'un dossier soit considéré
    
    Returns:
        Liste des chemins de répertoires contenant des vidéos
    """
    detected_dirs = []
    
    # 1. Scanner tous les lecteurs disponibles (Windows)
    available_drives = []
    if os.name == 'nt':  # Windows
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                available_drives.append(drive)
                logger.info(f"📀 Lecteur détecté : {drive}")
    else:  # Linux/Mac
        available_drives = ['/home', '/media', '/mnt']
    
    # 2. Dossiers communs à vérifier
    common_video_dirs = [
        'Videos', 'Vidéos', 'Movies', 'Films', 'Media', 'Multimédia',
        'Download', 'Downloads', 'Téléchargements', 'Documents'
    ]
    
    # 3. Parcourir chaque lecteur
    for drive in available_drives:
        try:
            # Vérifier les dossiers utilisateur
            if os.name == 'nt':
                users_path = Path(drive) / 'Users'
                if users_path.exists():
                    for user_dir in users_path.iterdir():
                        if user_dir.is_dir():
                            for common_dir in common_video_dirs:
                                video_dir = user_dir / common_dir
                                if video_dir.exists() and video_dir.is_dir():
                                    video_count = count_videos_in_dir(video_dir, max_depth=2)
                                    if video_count >= min_videos:
                                        detected_dirs.append(str(video_dir))
                                        logger.info(f"Répertoire trouvé : {video_dir} ({video_count} vidéos)")
            
            # Vérifier la racine du lecteur pour les dossiers courants
            drive_path = Path(drive)
            for item in drive_path.iterdir():
                if not item.is_dir():
                    continue
                
                dir_name_lower = item.name.lower()
                
                # Ignorer les dossiers système
                if dir_name_lower in IGNORED_DIRS:
                    continue
                
                # Vérifier si le nom ressemble à un dossier vidéo
                if any(keyword in dir_name_lower for keyword in ['video', 'film', 'movie', 'media', 'série', 'series']):
                    video_count = count_videos_in_dir(item, max_depth=max_depth)
                    if video_count >= min_videos:
                        detected_dirs.append(str(item))
                        logger.info(f"Répertoire trouvé : {item} ({video_count} vidéos)")
        
        except (PermissionError, OSError) as e:
            logger.warning(f"Impossible d'accéder à {drive}: {e}")
            continue
    
    return detected_dirs

def count_videos_in_dir(path: Path, max_depth: int = 2, current_depth: int = 0) -> int:
    """
    Compte le nombre de fichiers vidéo dans un répertoire (recherche limitée en profondeur).
    """
    if current_depth > max_depth:
        return 0
    
    count = 0
    try:
        for item in path.iterdir():
            if item.is_file() and is_video_file(item):
                count += 1
            elif item.is_dir() and item.name.lower() not in IGNORED_DIRS:
                count += count_videos_in_dir(item, max_depth, current_depth + 1)
    except (PermissionError, OSError):
        pass
    
    return count

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

def scan_all(settings=None, auto_detect: bool = True) -> dict:
    """
    Scanne tous les répertoires listés dans settings.yaml
    et met à jour la base de données dynamiquement :
    - Ajoute les nouvelles vidéos
    - Supprime les vidéos dont les fichiers n'existent plus
    
    Args:
        settings: Configuration (chargée automatiquement si None)
        auto_detect: Si True, détecte automatiquement les répertoires vidéo
    
    Retourne un dict avec les statistiques.
    """
    if settings is None:
        settings = load_settings()

    stats = {
        "indexed": 0,
        "removed": 0,
        "total": 0
    }
    
    # Récupérer les répertoires configurés
    paths_to_scan = settings.video_directories if hasattr(settings, "video_directories") else []
    
    # Si auto_detect est activé et aucun répertoire configuré, détecter automatiquement
    if auto_detect and not paths_to_scan:
        logger.info("Aucun répertoire configuré. Détection automatique en cours...")
        paths_to_scan = auto_detect_video_directories()
        
        if paths_to_scan:
            logger.info(f"\n📁 {len(paths_to_scan)} répertoire(s) détecté(s):")
            for path in paths_to_scan:
                logger.info(f"   - {path}")
            
            # Sauvegarder les répertoires détectés dans settings.yaml
            from core.config_manager import save_settings
            settings.video_directories = paths_to_scan
            save_settings(settings)
            logger.info(f"\nRépertoires sauvegardés dans settings.yaml")

    if not paths_to_scan:
        logger.warning("Aucun répertoire vidéo trouvé.")
        return stats

    with get_session() as session:
        # 1. Nettoyer les fichiers manquants
        all_videos = session.query(Video).all()
        for video in all_videos:
            video_path = Path(video.path)
            if not video_path.exists():
                logger.info(f"🗑️ Suppression : {video.title} (fichier introuvable)")
                session.delete(video)
                stats["removed"] += 1
        
        session.commit()
        
        # 2. Scanner et ajouter les nouveaux fichiers
        found_files = set()
        for root in paths_to_scan:
            root_path = Path(root).expanduser().resolve()
            if not root_path.exists():
                logger.info(f"🚫 Dossier introuvable : {root_path}")
                continue

            logger.info(f"Scan du dossier : {root_path}")
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

    logger.info(f"{stats['indexed']} nouvelles vidéos indexées.")
    logger.info(f"🗑️ {stats['removed']} vidéos supprimées (fichiers manquants).")
    logger.info(f"📊 Total : {stats['total']} vidéos en base.")
    
    return stats
