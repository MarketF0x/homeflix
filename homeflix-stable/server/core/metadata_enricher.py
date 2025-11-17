"""
Module pour enrichir les métadonnées des vidéos via l'API TMDb
Récupère : titre, année, genre, description, note, poster
"""

import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from core.logger import logger, log_exception

from .models import Video
from .config_manager import load_settings
from .title_utils import clean_title_and_year, extract_collection_info


def clean_title_from_filename(filename: str):
    """
    Compat: fonction attendue par les tests.
    Nettoie un nom de fichier et extrait (titre, année) en s'appuyant sur
    `title_utils.clean_title_and_year`.

    Args:
        filename: Nom de fichier ou base name (avec ou sans extension)

    Returns:
        Tuple (titre_nettoyé, année_ou_None)
    """
    try:
        stem = Path(filename).stem
    except Exception:
        stem = str(filename)
    return clean_title_and_year(stem)


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
        
        # Cast (acteurs) - récupérer les 5 premiers acteurs principaux
        cast_names = []
        if media_type in ["movie", "tv"]:
            credits_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}/credits"
            credits_params = {"api_key": api_key}
            
            try:
                cr = requests.get(credits_url, params=credits_params, timeout=8)
                if cr.status_code == 200:
                    credits = cr.json()
                    cast_data = credits.get("cast", [])
                    # Prendre les 5 premiers acteurs
                    cast_names = [actor.get("name") for actor in cast_data[:5] if actor.get("name")]
            except Exception:
                pass  # Si échec, continuer sans les acteurs
        
        # Collection/Saga (uniquement pour les films)
        collection_name = None
        if media_type == "movie":
            belongs_to_collection = details.get("belongs_to_collection")
            if belongs_to_collection:
                collection_name = belongs_to_collection.get("name")
        
        return {
            "title": result_title,
            "year": result_year,
            "genres": genres,
            "overview": overview,
            "vote_average": vote_average,
            "poster_path": poster_path,
            "cast": cast_names,  # Liste des noms d'acteurs
            "media_type": media_type,
            "collection": collection_name  # Nom de la collection TMDb
        }
        
    except Exception as e:
        logger.error(f"Erreur TMDb pour '{title}': {e}")
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
    logger.info(f"🔄 Enrichissement de: {video.title or video.path} (force={force})")
    
    settings = load_settings()
    api_key = getattr(settings, "tmdb_api_key", None)
    
    if not api_key:
        logger.warning("❌ Clé API TMDb manquante")
        return False
    
    # Skip seulement si TOUTES les métadonnées importantes sont présentes ET le poster
    # Ne pas skipper si un seul champ manque (genre, année, résumé, note, acteurs, poster)
    has_all_metadata = (
        video.genre and 
        video.year and 
        video.overview and 
        video.vote_average and 
        video.cast and
        video.poster_path  # Ajouté: vérifier aussi le poster
    )
    
    if not force and has_all_metadata:
        logger.info(f"⏭️ Déjà complet, skip (force={force})")
        return False
    
    # Utiliser le titre et l'année de la BDD s'ils existent (déjà nettoyés),
    # sinon extraire depuis le nom de fichier
    if video.title and video.title.strip():
        # Utiliser le titre déjà nettoyé dans la BDD
        search_title = video.title
        search_year = video.year
        logger.info(f"🔍 Recherche TMDb: '{search_title}' ({search_year}) [depuis BDD]")
    else:
        # Nettoyer depuis le nom de fichier
        video_path = Path(video.path)
        search_title, extracted_year = clean_title_and_year(video_path.stem)
        search_year = video.year or extracted_year
        logger.info(f"🔍 Recherche TMDb: '{search_title}' ({search_year}) [depuis fichier]")
    
    # Recherche sur TMDb avec le titre le plus propre possible
    metadata = search_tmdb(search_title, search_year, api_key)
    
    if not metadata:
        logger.warning(f"❌ Aucune métadonnée trouvée pour: {search_title}")
        return False
    
    # Met à jour les champs
    video.title = metadata["title"]
    
    if metadata["year"]:
        video.year = metadata["year"]
    
    # Prend le premier genre (principal)
    if metadata["genres"]:
        video.genre = metadata["genres"][0].lower()
    
    # Métadonnées TMDb étendues
    if metadata.get("overview"):
        video.overview = metadata["overview"]
    
    if metadata.get("vote_average"):
        video.vote_average = metadata["vote_average"]
    
    if metadata.get("poster_path"):
        video.poster_path = metadata["poster_path"]
    
    if metadata.get("cast"):
        # Stocker les acteurs séparés par des virgules
        video.cast = ", ".join(metadata["cast"])
    
    # Collection/Saga - Priorité à TMDb, sinon détection automatique
    if metadata.get("collection"):
        # Collection depuis TMDb (ex: "The Matrix Collection")
        video.collection = metadata["collection"]
        # Essayer d'extraire le numéro depuis le titre
        collection_info = extract_collection_info(video.title)
        if collection_info['episode']:
            video.episode_number = collection_info['episode']
    else:
        # Détection automatique depuis le titre de la vidéo ou le nom du fichier
        video_path = Path(video.path)
        collection_info = extract_collection_info(video.title if video.title else video_path.stem)
        if collection_info['collection']:
            video.collection = collection_info['collection']
            video.episode_number = collection_info['episode']
    
    session.commit()
    
    # Log détaillé pour debug
    cast_info = f" | Acteurs: {video.cast[:50]}..." if video.cast else ""
    rating_info = f" | Note: {video.vote_average}/10" if video.vote_average else ""
    collection_info_log = f" | Collection: {video.collection} #{video.episode_number}" if video.collection else ""
    logger.info(f"✅ Enrichi: {video.title} ({video.year}) - {video.genre}{rating_info}{cast_info}{collection_info_log}")
    
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
    
    logger.info(f"\nEnrichissement de {stats['total']} vidéos via TMDb...")
    
    for video in videos:
        try:
            # Skip seulement si TOUTES les métadonnées importantes sont présentes ET le poster
            has_all_metadata = (
                video.genre and 
                video.year and 
                video.overview and 
                video.vote_average and 
                video.cast and
                video.poster_path  # Ajouté: vérifier aussi le poster
            )
            
            if not force and has_all_metadata:
                stats["skipped"] += 1
                logger.debug(f"⏭️  Ignoré (déjà complet): {video.title}")
                continue
            
            # Log des champs manquants pour debug
            missing = []
            if not video.genre: missing.append("genre")
            if not video.year: missing.append("année")
            if not video.overview: missing.append("résumé")
            if not video.vote_average: missing.append("note")
            if not video.cast: missing.append("acteurs")
            if not video.poster_path: missing.append("poster")  # Ajouté dans le log
            
            if missing:
                logger.info(f"🔄 Enrichissement de '{video.title}' (manque: {', '.join(missing)})")
            
            success = enrich_video_metadata(video, session, force=force)
            
            if success:
                stats["enriched"] += 1
            else:
                stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"Erreur pour {video.path}: {e}")
            stats["failed"] += 1
    
    logger.info(f"\nEnrichissement terminé:")
    logger.info(f"   - Enrichis: {stats['enriched']}")
    logger.warning(f"   - Ignorés: {stats['skipped']}")
    logger.error(f"   - Échecs: {stats['failed']}")
    
    return stats
