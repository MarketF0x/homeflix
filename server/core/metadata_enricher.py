"""
Module pour enrichir les métadonnées des vidéos via l'API TMDb
Récupère : titre, année, genre, description, note, poster
"""

import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import Video
from .config_manager import load_settings
from .title_utils import clean_title_and_year

# Regex pour nettoyer les titres
_RES_TAGS = re.compile(
    r"(?:\b(?:480|720|1080|2160|4k)p?\b|"
    r"\b(?:x264|x265|hevc|h264|h265|avc)\b|"
    r"\b(?:WEBrip|WEB-DL|BluRay|BRRip|HDRip|DVDRip|HDTV|PDTV)\b|"
    r"\b(?:AAC|AC3|DTS|DD5\.1|DD51)\b|"
    r"\b(?:\d+CD)\b|"  # Retire 1CD, 2CD, etc.
    r"\[.*?\]|\(.*?\))",
    re.I
)
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\b")
_LANGUAGE_TAGS = re.compile(r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|MULTI|ENGLISH)\b", re.I)
_EPISODE = re.compile(r"\b(?:S\d{1,2}E\d{1,2}|[Ss]aison\s*\d+|[Ee]pisode\s*\d+)\b", re.I)


def clean_title_from_filename(stem: str) -> tuple[str, Optional[int]]:
    """Conserve la signature publique, délègue vers l'utilitaire partagé."""
    title, year = clean_title_and_year(stem)
    return title, year


def search_tmdb(title: str, year: Optional[int] = None, api_key: str = "") -> Optional[Dict[str, Any]]:
    """
    Recherche un film/série sur TMDb et retourne les métadonnées complètes.
    
    Returns:
        Dict avec: title, year, genres (list), overview, vote_average, poster_path, media_type
        None si aucun résultat
    """
    if not api_key or not title or len(title) < 2:
        return None
    
    try:
        # Recherche multi (films + séries)
        params = {"api_key": api_key, "query": title, "language": "fr-FR"}
        if year:
            params["year"] = year
        
        url = "https://api.themoviedb.org/3/search/multi"
        r = requests.get(url, params=params, timeout=8)
        
        if r.status_code != 200:
            return None
        
        data = r.json()
        results = data.get("results") or []
        
        # Si aucun résultat avec l'année, réessaye sans
        if not results and year:
            params.pop("year", None)
            r = requests.get(url, params=params, timeout=8)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results") or []
        
        if not results:
            return None
        
        # Fonction de scoring pour trouver le meilleur résultat
        def score_result(item):
            s = 0
            media_type = item.get("media_type", "")
            
            # Priorité aux films et séries
            if media_type == "movie":
                s += 3
            elif media_type == "tv":
                s += 2
            
            # Popularité
            popularity = item.get("popularity", 0)
            s += min(popularity / 10, 2)
            
            # Boost si année correspond
            item_year = None
            date = item.get("release_date") or item.get("first_air_date")
            if date and len(date) >= 4:
                try:
                    item_year = int(date[:4])
                except Exception:
                    pass
            
            if year and item_year == year:
                s += 5
            elif year and item_year and abs(item_year - year) <= 1:
                s += 2
            
            return s
        
        best = max(results, key=score_result)
        
        # Récupère les détails complets
        media_type = best.get("media_type")
        media_id = best.get("id")
        
        if not media_id or media_type not in ["movie", "tv"]:
            return None
        
        # Endpoint de détails
        detail_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}"
        detail_params = {"api_key": api_key, "language": "fr-FR"}
        
        dr = requests.get(detail_url, params=detail_params, timeout=8)
        if dr.status_code != 200:
            return None
        
        details = dr.json()
        
        # Extraction des données
        result_title = details.get("title") or details.get("name") or title
        
        # Année
        result_year = None
        date = details.get("release_date") or details.get("first_air_date")
        if date and len(date) >= 4:
            try:
                result_year = int(date[:4])
            except Exception:
                pass
        
        # Genres (liste de noms)
        genres_data = details.get("genres") or []
        genres = [g.get("name") for g in genres_data if g.get("name")]
        
        # Description
        overview = details.get("overview") or ""
        
        # Note
        vote_average = details.get("vote_average") or 0.0
        
        # Poster
        poster_path = details.get("poster_path")
        
        return {
            "title": result_title,
            "year": result_year,
            "genres": genres,
            "overview": overview,
            "vote_average": vote_average,
            "poster_path": poster_path,
            "media_type": media_type
        }
        
    except Exception as e:
        print(f"⚠️ Erreur TMDb pour '{title}': {e}")
        return None


def enrich_video_metadata(video: Video, session: Session, force: bool = False) -> bool:
    """
    Enrichit les métadonnées d'une vidéo via TMDb.
    
    Args:
        video: Instance Video à enrichir
        session: Session SQLAlchemy
        force: Force la mise à jour même si déjà enrichi
    
    Returns:
        True si enrichissement réussi, False sinon
    """
    settings = load_settings()
    api_key = getattr(settings, "tmdb_api_key", None)
    
    if not api_key:
        return False
    
    # Si déjà enrichi (a un genre et une année), skip sauf si force
    if not force and video.genre and video.year:
        return False
    
    # Nettoie le titre
    video_path = Path(video.path)
    clean_title, extracted_year = clean_title_from_filename(video_path.stem)
    
    # Utilise l'année du fichier si déjà présente en BDD, sinon celle extraite
    search_year = video.year or extracted_year
    
    # Recherche sur TMDb
    metadata = search_tmdb(clean_title, search_year, api_key)
    
    if not metadata:
        return False
    
    # Met à jour les champs
    video.title = metadata["title"]
    
    if metadata["year"]:
        video.year = metadata["year"]
    
    # Prend le premier genre (principal)
    if metadata["genres"]:
        video.genre = metadata["genres"][0].lower()
    
    # On pourrait ajouter d'autres champs comme overview, vote_average
    # si on les ajoute au modèle Video
    
    session.commit()
    print(f"✅ Métadonnées enrichies pour: {video.title} ({video.year}) - {video.genre}")
    
    return True


def enrich_all_videos(session: Session, force: bool = False) -> Dict[str, int]:
    """
    Enrichit toutes les vidéos de la base avec les métadonnées TMDb.
    
    Returns:
        Statistiques: total, enriched, skipped, failed
    """
    stats = {"total": 0, "enriched": 0, "skipped": 0, "failed": 0}
    
    videos = session.query(Video).all()
    stats["total"] = len(videos)
    
    print(f"\n🔍 Enrichissement de {stats['total']} vidéos via TMDb...")
    
    for video in videos:
        try:
            # Si déjà enrichi et pas de force, skip
            if not force and video.genre and video.year:
                stats["skipped"] += 1
                continue
            
            success = enrich_video_metadata(video, session, force=force)
            
            if success:
                stats["enriched"] += 1
            else:
                stats["failed"] += 1
                
        except Exception as e:
            print(f"❌ Erreur pour {video.path}: {e}")
            stats["failed"] += 1
    
    print(f"\n✅ Enrichissement terminé:")
    print(f"   - Enrichis: {stats['enriched']}")
    print(f"   - Ignorés: {stats['skipped']}")
    print(f"   - Échecs: {stats['failed']}")
    
    return stats
