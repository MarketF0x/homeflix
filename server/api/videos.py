"""Routeur vidéo: listing, recherche, random, update, progress, stream."""
from fastapi import APIRouter, HTTPException, Query, Body, BackgroundTasks
from pathlib import Path
from typing import Literal, List
from datetime import datetime
from urllib.parse import quote
import random
import subprocess
import sys
import requests
import sqlite3
import os
import re
import base64
import shutil
import traceback

from core.db import get_session
from core.models import Video, WatchProgress
from core.config_manager import load_settings, save_settings
from core.player import open_with_default
from core.thumbnails import get_thumbnail, ensure_thumbnail_sync, thumb_path_for, THUMB_DIR
from core.subprocess_helper import popen_hidden
from core.scanner import auto_detect_video_directories
from core.metadata_enricher import enrich_video_metadata
from core.logger import logger, log_exception

SessionMode = Literal["mixed", "films", "series"]

router = APIRouter(prefix="/api", tags=["videos"])


def _filter_by_mode(videos: List[Video], mode: SessionMode, min_film=75, max_series=55):
    """
    Filtre les vidéos selon le mode de session.
    
    Logique:
    - Si duration_seconds disponible: utilise la durée
      * films: durée >= min_film minutes
      * series: durée <= max_series minutes
    - Sinon: utilise le chemin du fichier
      * films: chemin contient "film" (case insensitive)
      * series: chemin contient "serie" ou "series" (case insensitive)
    - mixed: tout afficher
    """
    if mode == "mixed":
        return videos
    
    result = []
    for v in videos:
        # Si on a la durée, on l'utilise
        if v.duration_seconds and v.duration_seconds > 0:
            duration_minutes = v.duration_seconds / 60
            if mode == "films" and duration_minutes >= min_film:
                result.append(v)
            elif mode == "series" and duration_minutes <= max_series:
                result.append(v)
        else:
            # Sinon on utilise le chemin
            path_lower = v.path.lower()
            if mode == "films" and "film" in path_lower:
                result.append(v)
            elif mode == "series" and ("serie" in path_lower or "series" in path_lower):
                result.append(v)
    
    return result


@router.get("/videos")
def list_videos(
    mode: SessionMode = Query("mixed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    profile_id: int | None = Query(None)
):
    with get_session() as s:
        query = s.query(Video).order_by(Video.title.asc())
        if search:
            query = query.filter(Video.title.ilike(f"%{search}%"))
        items = query.all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        # Exclure les vidéos masquées pour ce profil
        if profile_id is not None:
            
            DB_PATH = Path(__file__).parent.parent / "homeflix.db"
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT video_id FROM hidden_videos WHERE profile_id = ?
                """, (profile_id,))
                hidden_ids = {row[0] for row in cursor.fetchall()}
                
                # Filtrer les vidéos masquées
                filtered = [v for v in filtered if v.id not in hidden_ids]
            finally:
                conn.close()
        
        total = len(filtered)
        paginated = filtered[skip:skip + limit]
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "videos": [
                {
                    "id": v.id,
                    "title": v.title,
                    "path": v.path,
                    "duration_seconds": v.duration_seconds,
                    "size": v.size,
                    "year": v.year,
                    "genre": v.genre,
                    "watched": v.watched,
                    "last_position": v.last_position,
                    "overview": v.overview,
                    "vote_average": v.vote_average,
                    "cast": v.cast,
                    "poster_path": v.poster_path,
                }
                for v in paginated
            ],
        }


@router.get("/random")
def random_video(mode: SessionMode = Query("mixed")):
    with get_session() as s:
        items = s.query(Video).all()
        if not items:
            raise HTTPException(status_code=404, detail="Aucune vidéo dans la bibliothèque")
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        if not filtered:
            raise HTTPException(status_code=404, detail=f"Aucune vidéo trouvée pour le mode '{mode}'")
        video = random.choice(filtered)
        return {
            "id": video.id,
            "title": video.title,
            "path": video.path,
            "duration_seconds": video.duration_seconds,
            "size": video.size,
            "year": video.year,
            "genre": video.genre,
            "watched": video.watched,
            "last_position": video.last_position,
            "overview": video.overview,
            "vote_average": video.vote_average,
            "cast": video.cast,
            "poster_path": video.poster_path,
        }


@router.post("/open")
def open_video(payload: dict = Body(...)):
    path = payload.get("path")
    video_id = payload.get("id")
    if not path:
        raise HTTPException(status_code=400, detail="Le champ 'path' est requis.")
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Le fichier est introuvable : {p}")
    if video_id:
        with get_session() as s:
            video = s.query(Video).filter(Video.id == video_id).first()
            if video:
                video.watched = True
                s.commit()
    open_with_default(p)
    return {"ok": True}


@router.post("/progress")
def save_progress(payload: dict = Body(...)):
    """Sauvegarde la progression de lecture pour un profil spécifique"""
    video_id = payload.get("id")
    position = payload.get("position", 0)
    profile_id = payload.get("profile_id")
    
    if not video_id:
        raise HTTPException(status_code=400, detail="ID de la vidéo requis")
    if profile_id is None:
        raise HTTPException(status_code=400, detail="ID du profil requis")
    
    s = get_session()
    try:
        
        # Note: On ne vérifie pas l'existence de la vidéo car le système
        # scanne les vidéos dynamiquement sans table de cache
        
        # Chercher ou créer l'entrée de progression pour ce profil
        progress = s.query(WatchProgress).filter(
            WatchProgress.profile_id == profile_id,
            WatchProgress.video_id == video_id
        ).first()
        
        # Sauvegarder ou mettre à jour la progression
        if progress:
            progress.position = position
            progress.updated_at = datetime.utcnow()
        else:
            progress = WatchProgress(
                profile_id=profile_id,
                video_id=video_id,
                position=position,
                updated_at=datetime.utcnow()
            )
            s.add(progress)
        
        # Limiter à 10 vidéos en reprise par profil
        all_progress = s.query(WatchProgress).filter(
            WatchProgress.profile_id == profile_id
        ).order_by(WatchProgress.updated_at.desc()).all()
        
        # Si on vient d'ajouter, on a len(all_progress) entrées
        # On garde les 10 plus récentes
        if len(all_progress) > 10:
            # Supprimer les plus anciennes (au-delà de 10)
            to_remove = all_progress[10:]
            for old_progress in to_remove:
                s.delete(old_progress)
        
        s.commit()
        return {"ok": True, "position": position}
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


@router.get("/progress/{video_id}")
def get_progress(video_id: int, profile_id: int = Query(...)):
    """Récupère la progression de lecture d'une vidéo pour un profil"""
    s = get_session()
    try:
        
        progress = s.query(WatchProgress).filter(
            WatchProgress.profile_id == profile_id,
            WatchProgress.video_id == video_id
        ).first()
        
        if progress:
            return {"position": progress.position, "updated_at": progress.updated_at}
        
        return {"position": 0, "updated_at": None}
    finally:
        s.close()



@router.delete("/videos/{video_id}")
def delete_video(
    video_id: int, 
    delete_file: bool = False,
    profile_id: int | None = Query(None)
):
    """
    Supprime ou masque une vidéo selon le type de profil.
    - Profil principal (is_main=1): supprime réellement la vidéo
    - Profil secondaire: masque la vidéo pour ce profil uniquement
    """
    # Si un profil est spécifié, vérifier s'il est principal ou secondaire
    if profile_id is not None:
        
        DB_PATH = Path(__file__).parent.parent / "homeflix.db"
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT is_main FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            
            if row and not row[0]:  # Profil secondaire (is_main = 0)
                # Masquer la vidéo au lieu de la supprimer
                cursor.execute("""
                    INSERT OR IGNORE INTO hidden_videos (profile_id, video_id)
                    VALUES (?, ?)
                """, (profile_id, video_id))
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Vidéo #{video_id} masquée pour le profil #{profile_id}")
                return {"ok": True, "message": "Vidéo masquée pour ce profil", "hidden": True}
        finally:
            conn.close()
    
    # Profil principal ou pas de profil spécifié: suppression réelle
    with get_session() as s:
        video = s.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo introuvable.")
        
        video_path = video.path
        video_title = video.title
        
        # Supprimer de la base de données
        s.delete(video)
        s.commit()
        
        # Supprimer le fichier physique si demandé
        if delete_file and video_path:
            try:
                p = Path(video_path)
                if p.exists():
                    p.unlink()
                    return {"ok": True, "message": f"Vidéo '{video_title}' supprimée (base de données + fichier)."}
            except Exception as e:
                return {"ok": True, "warning": f"Vidéo supprimée de la base de données mais impossible de supprimer le fichier: {str(e)}"}
        
        return {"ok": True, "message": f"Vidéo '{video_title}' supprimée de la base de données."}


@router.post("/video/update")
def update_video(payload: dict = Body(...)):
    try:
        logger.info(f"📝 Mise à jour vidéo - Payload reçu: {list(payload.keys())}")
        if "copy_poster" in payload:
            logger.info(f"🖼️ copy_poster détecté dans payload: {payload.get('copy_poster')}")
        
        video_id = payload.get("id")
        if not video_id:
            raise HTTPException(status_code=400, detail="Le champ 'id' est requis.")
        
        with get_session() as s:
            video = s.query(Video).filter(Video.id == video_id).first()
            if not video:
                raise HTTPException(status_code=404, detail="Vidéo introuvable.")
            
            # Champs de progression
            if "watched" in payload:
                video.watched = bool(payload["watched"])
            if "last_position" in payload:
                video.last_position = int(payload["last_position"])
            
            # Métadonnées éditables
            if "title" in payload:
                video.title = payload["title"]
            if "year" in payload:
                video.year = payload["year"]
            if "genre" in payload:
                video.genre = payload["genre"]
            if "overview" in payload:
                video.overview = payload["overview"]
            if "cast" in payload:
                video.cast = payload["cast"]
            if "collection_name" in payload:
                video.collection = payload["collection_name"]
            
            # Copie d'une affiche existante
            if "copy_poster" in payload and payload["copy_poster"]:
                try:
                    source_path = Path(payload["copy_poster"])
                    logger.info(f"🔍 Demande de copie d'affiche reçue")
                    logger.info(f"📂 Source: {source_path}")
                    logger.info(f"📂 Source existe: {source_path.exists()}")
                    
                    if not source_path.exists():
                        logger.warning(f"❌ Affiche source introuvable: {source_path}")
                    else:
                        logger.info(f"✅ Copie de l'affiche: {source_path}")
                        
                        # Destination
                        thumb_file = thumb_path_for(Path(video.path))
                        logger.info(f"📂 Destination: {thumb_file}")
                        thumb_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Lire et réécrire le fichier (comme pour poster_url)
                        logger.info(f"📖 Lecture du fichier source...")
                        with open(source_path, 'rb') as src:
                            image_data = src.read()
                        logger.info(f"📖 Taille lue: {len(image_data)} octets")
                        
                        logger.info(f"💾 Écriture vers destination...")
                        with open(thumb_file, 'wb') as dest:
                            dest.write(image_data)
                        
                        # Créer un fichier marqueur pour identifier les affiches personnalisées
                        marker_file = thumb_file.with_suffix('.jpg.manual')
                        marker_file.touch()
                        
                        logger.info(f"✅ Affiche copiée et sauvegardée: {thumb_file}")
                        
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la copie d'affiche: {e}")
                    log_exception(e, "copie affiche")
            
            # Téléchargement de l'affiche depuis une URL
            if "poster_url" in payload and payload["poster_url"]:
                try:
                    poster_url = payload["poster_url"]
                    logger.info(f"Téléchargement affiche: {poster_url[:100]}...")
                    
                    thumb_file = thumb_path_for(Path(video.path))
                    thumb_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Vérifier si c'est une data URL en base64
                    if poster_url.startswith('data:image'):
                        # Extraire le base64 de la data URL
                        match = re.match(r'data:image/\w+;base64,(.+)', poster_url)
                        if match:
                            image_data = base64.b64decode(match.group(1))
                            with open(thumb_file, 'wb') as f:
                                f.write(image_data)
                            logger.info("Image base64 décodée et sauvegardée")
                        else:
                            raise ValueError("Format data URL invalide")
                    else:
                        # Télécharger l'image HTTP avec retry et timeout augmenté
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                response = requests.get(poster_url, timeout=30, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                })
                                response.raise_for_status()
                                break
                            except requests.exceptions.Timeout:
                                if attempt < max_retries - 1:
                                    logger.warning(f"Timeout, retry {attempt + 1}/{max_retries}...")
                                    continue
                                raise
                        
                        # Sauvegarder l'image
                        with open(thumb_file, 'wb') as f:
                            f.write(response.content)
                    
                    # Créer un fichier marqueur pour identifier les affiches personnalisées
                    marker_file = thumb_file.with_suffix('.jpg.manual')
                    marker_file.touch()
                    
                    logger.info(f"Affiche sauvegardée: {thumb_file}")
                    
                except Exception as e:
                    log_exception(e, "téléchargement affiche")
                    # Ne pas bloquer la sauvegarde si l'affiche échoue
            
            s.commit()
            logger.info(f"✅ Vidéo {video.id} mise à jour avec succès")
            return {
                "ok": True,
                "id": video.id,
                "path": video.path,  # IMPORTANT : le path ne doit jamais être perdu
                "title": video.title,
                "watched": video.watched,
                "last_position": video.last_position,
                "year": video.year,
                "genre": video.genre,
                "overview": video.overview,
                "cast": video.cast,
                "collection_name": video.collection,
                "poster_path": video.poster_path,
            }
    
    except HTTPException:
        raise  # Re-lancer les HTTPException
    except Exception as e:
        log_exception(e, context="update_video")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.post("/video/{video_id}/enrich")
def enrich_single_video(video_id: int):
    """
    Force l'enrichissement TMDb pour une vidéo spécifique.
    Utilise le titre et l'année actuellement dans la BDD.
    """
    with get_session() as s:
        video = s.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo introuvable.")
        
        # Force l'enrichissement (ATTENTION: ordre des paramètres = video, session, force)
        success = enrich_video_metadata(video, s, force=True)
        
        if not success:
            return {
                "ok": False,
                "message": "Aucune métadonnée trouvée sur TMDb pour ce titre/année."
            }
        
        # Recharge les données depuis la BDD
        s.refresh(video)
        
        return {
            "ok": True,
            "message": f"Métadonnées enrichies depuis TMDb pour '{video.title}'",
            "video": {
                "id": video.id,
                "path": video.path,  # IMPORTANT : le path ne doit jamais être perdu
                "title": video.title,
                "year": video.year,
                "genre": video.genre,
                "overview": video.overview,
                "cast": video.cast,
                "vote_average": video.vote_average,
                "poster_path": video.poster_path,
                "collection_name": video.collection,
            }
        }


@router.post("/video/{video_id}/enrich-from-url")
def enrich_from_tmdb_url(video_id: int, payload: dict = Body(...)):
    """
    Enrichit une vidéo depuis une URL TMDb spécifique.
    Exemple: https://www.themoviedb.org/movie/550 ou https://www.themoviedb.org/tv/1399
    """
    
    tmdb_url = payload.get("tmdb_url")
    if not tmdb_url:
        raise HTTPException(status_code=400, detail="Le champ 'tmdb_url' est requis.")
    
    with get_session() as s:
        video = s.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo introuvable.")
        
        # Extraire le type (movie/tv) et l'ID depuis l'URL
        match = re.search(r'themoviedb\.org/(movie|tv)/(\d+)', tmdb_url)
        if not match:
            raise HTTPException(status_code=400, detail="URL TMDb invalide. Format attendu: https://www.themoviedb.org/movie/123 ou /tv/456")
        
        media_type = match.group(1)
        tmdb_id = match.group(2)
        
        logger.info(f"Enrichissement depuis TMDb URL: {media_type}/{tmdb_id}")
        
        settings = load_settings()
        api_key = getattr(settings, "tmdb_api_key", None)
        
        # DEBUG: Logger les paramètres chargés
        logger.info(f"DEBUG: Settings chargés = {settings}")
        logger.info(f"DEBUG: api_key = {api_key}")
        logger.info(f"DEBUG: type(api_key) = {type(api_key)}")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="Clé API TMDb non configurée dans les paramètres")
        
        # Récupérer les détails depuis TMDb
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            params = {"api_key": api_key, "language": "fr-FR"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Mettre à jour les métadonnées
            if media_type == "movie":
                video.title = data.get("title", video.title)
                video.year = data.get("release_date", "")[:4] if data.get("release_date") else video.year
            else:  # tv
                video.title = data.get("name", video.title)
                video.year = data.get("first_air_date", "")[:4] if data.get("first_air_date") else video.year
            
            video.overview = data.get("overview", video.overview)
            video.vote_average = data.get("vote_average", video.vote_average)
            
            # Genres
            genres = data.get("genres", [])
            if genres:
                video.genre = ", ".join([g["name"] for g in genres[:3]])
            
            # Cast (récupérer les crédits)
            credits_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits"
            credits_response = requests.get(credits_url, params=params, timeout=10)
            if credits_response.ok:
                credits_data = credits_response.json()
                cast = credits_data.get("cast", [])[:5]
                if cast:
                    video.cast = ", ".join([actor["name"] for actor in cast])
            
            # Collection (uniquement pour les films)
            if media_type == "movie":
                belongs_to_collection = data.get("belongs_to_collection")
                if belongs_to_collection:
                    video.collection = belongs_to_collection.get("name")
                    logger.info(f"Collection trouvée: {video.collection}")
            
            # Télécharger le poster
            poster_path = data.get("poster_path")
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                thumb_file = thumb_path_for(Path(video.path))
                thumb_file.parent.mkdir(parents=True, exist_ok=True)
                
                img_response = requests.get(poster_url, timeout=30)
                if img_response.ok:
                    with open(thumb_file, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Créer le marqueur .manual
                    marker_file = thumb_file.with_suffix('.jpg.manual')
                    marker_file.touch()
                    
                    logger.info(f"Poster téléchargé: {thumb_file}")
            
            s.commit()
            s.refresh(video)
            
            return {
                "ok": True,
                "message": f"Métadonnées enrichies depuis TMDb ({media_type}/{tmdb_id})",
                "video": {
                    "id": video.id,
                    "path": video.path,
                    "title": video.title,
                    "year": video.year,
                    "genre": video.genre,
                    "overview": video.overview,
                    "cast": video.cast,
                    "vote_average": video.vote_average,
                    "poster_path": video.poster_path,
                    "collection_name": video.collection,
                }
            }
            
        except requests.RequestException as e:
            logger.error(f"Erreur TMDb API: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération depuis TMDb: {str(e)}")


def compress_video_background(video_path: str):
    """Compresse une vidéo en arrière-plan avec FFmpeg.
    
    Note: La compression préserve TOUTES les pistes audio et sous-titres.
    Vous pourrez choisir la piste audio après compression comme avant.
    """
    try:
        script_path = Path(__file__).parent.parent.parent / 'compress_one_video.py'
        if not script_path.exists():
            logger.error(f'Script de compression introuvable: {script_path}')
            return
        
        # Lancer le script de compression en arrière-plan
        popen_hidden(
            [sys.executable, str(script_path), video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info(f'Compression lancée en arrière-plan pour: {video_path}')
    except Exception as e:
        logger.error(f'Erreur lancement compression: {e}')


@router.post('/compress-video')
def compress_video(payload: dict = Body(...), background_tasks: BackgroundTasks = None):
    """Lance la compression d'une vidéo volumineuse.
    
    La compression:
    - Préserve TOUTES les pistes audio (vous pourrez toujours choisir après)
    - Préserve tous les sous-titres
    - Réduit la taille de ~65% en moyenne
    - Garde l'original (.original)
    - Fonctionne en arrière-plan
    """
    video_path = payload.get('path')
    if not video_path:
        raise HTTPException(status_code=400, detail='Le champ path est requis.')
    
    path = Path(video_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail='Fichier vidéo introuvable.')
    
    # Vérifier que c'est bien un gros fichier
    size_gb = path.stat().st_size / (1024**3)
    if size_gb < 1.0:
        raise HTTPException(status_code=400, detail='Fichier trop petit, compression non nécessaire.')
    
    # Vérifier qu'il n'y a pas déjà une version compressée
    mp4_path = path.with_suffix('.mp4')
    if mp4_path.exists() and path.suffix.lower() != '.mp4':
        return {'ok': True, 'message': 'Une version compressée existe déjà.'}
    
    # Lancer la compression en arrière-plan
    if background_tasks:
        background_tasks.add_task(compress_video_background, str(path))
    else:
        compress_video_background(str(path))
    
    return {
        'ok': True,
        'message': f'Compression lancée pour {path.name} ({size_gb:.1f} GB). La vidéo sera optimisée en arrière-plan. TOUTES les pistes audio seront préservées.'
    }


@router.post("/detect-video-directories")
def detect_video_directories():
    """Détecte automatiquement les répertoires contenant des vidéos."""
    try:
        detected = auto_detect_video_directories(max_depth=3, min_videos=3)
        
        if not detected:
            return {
                'ok': False,
                'message': 'Aucun répertoire vidéo détecté automatiquement.',
                'directories': []
            }
        
        # Sauvegarder dans settings.yaml
        settings = load_settings()
        settings.video_directories = detected
        save_settings(settings)
        
        return {
            'ok': True,
            'message': f'{len(detected)} répertoire(s) vidéo détecté(s) et sauvegardé(s).',
            'directories': detected
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la détection: {str(e)}")


@router.get("/recent-posters")
def get_recent_posters(limit: int = 20):
    """Retourne uniquement les affiches personnalisées (téléchargées manuellement)."""
    
    thumb_dir = THUMB_DIR
    if not thumb_dir.exists():
        logger.warning("Dossier thumbs n'existe pas")
        return {"posters": []}
    
    # Ne chercher que les JPG qui ont un fichier .manual associé
    posters = []
    marker_files = list(thumb_dir.glob("*.jpg.manual"))
    logger.info(f"Trouvé {len(marker_files)} fichiers .jpg.manual")
    
    for marker_file in marker_files:
        # Enlève .manual pour avoir le fichier .jpg
        jpg_file = Path(str(marker_file).replace('.jpg.manual', '.jpg'))
        logger.info(f"  📂 Marker: {marker_file.name} → JPG: {jpg_file.name}")
        
        if jpg_file.exists():
            logger.info(f"    ✓ Fichier JPG existe")
            logger.info(f"    ✓ Fichier JPG existe")
            try:
                mtime = os.path.getmtime(jpg_file)
                posters.append({
                    "path": str(jpg_file),
                    "mtime": mtime,
                    "filename": jpg_file.name
                })
                logger.info(f"    ✓ Ajouté à la liste: {jpg_file.name}")
            except Exception as e:
                logger.error(f"    ✗ Erreur: {e}")
                continue
        else:
            logger.error(f"    ✗ Fichier JPG introuvable: {jpg_file}")
    
    logger.info(f"📊 Total affiches trouvées: {len(posters)}")
    
    # Trier par date de modification (plus récent en premier)
    posters.sort(key=lambda x: x["mtime"], reverse=True)
    
    # Limiter et construire le résultat
    result = []
    for poster in posters[:limit]:
        result.append({
            "path": poster["path"],  # Chemin absolu pour copy_poster
            "url": f"/api/thumbnail?path={quote(poster['filename'])}&direct=1",  # URL encodée pour affichage
            "filename": poster["filename"],
            "date": datetime.fromtimestamp(poster["mtime"]).strftime("%Y-%m-%d %H:%M")
        })
    
    logger.info(f"Retour de {len(result)} affiche(s) sur {len(posters)}")
    return {"posters": result}


@router.post("/delete-poster")
def delete_poster(payload: dict = Body(...)):
    """Supprime une affiche personnalisée et son marqueur .manual."""
    
    poster_path = payload.get("poster_path")
    if not poster_path:
        raise HTTPException(status_code=400, detail="Le champ 'poster_path' est requis.")
    
    try:
        logger.info(f"🗑️ Demande suppression: {poster_path}")
        logger.info(f"📂 THUMB_DIR: {THUMB_DIR}")
        
        poster_file = Path(poster_path)
        logger.info(f"📂 Poster file (Path): {poster_file}")
        logger.info(f"📂 Poster file (resolved): {poster_file.resolve()}")
        
        # Normaliser les chemins pour la comparaison
        poster_resolved = poster_file.resolve()
        thumb_resolved = THUMB_DIR.resolve()
        
        logger.info(f"Vérification: {str(poster_resolved).startswith(str(thumb_resolved))}")
        
        # Vérifier que le fichier est bien dans le dossier thumbs
        if not str(poster_resolved).startswith(str(thumb_resolved)):
            logger.error(f"Chemin refusé: {poster_resolved} pas dans {thumb_resolved}")
            raise HTTPException(status_code=403, detail="Chemin non autorisé")
        
        if not poster_file.exists():
            logger.error(f"Fichier introuvable: {poster_file}")
            raise HTTPException(status_code=404, detail="Affiche non trouvée")
        
        # Supprimer le fichier .jpg
        poster_file.unlink()
        logger.info(f"Fichier supprimé: {poster_file}")
        
        # Supprimer le marqueur .manual
        marker_file = Path(str(poster_file) + '.manual')
        if marker_file.exists():
            marker_file.unlink()
            logger.info(f"Marqueur supprimé: {marker_file}")
        
        return {"ok": True, "message": "Affiche supprimée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression affiche: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/copy-poster")
def copy_poster(video_id: int = Body(...), source_poster: str = Body(...)):
    """Copie une affiche existante vers une autre vidéo."""
    
    session = get_session()
    try:
        video = session.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo non trouvée")
        
        source_path = Path(source_poster)
        if not source_path.exists():
            raise HTTPException(status_code=404, detail="Affiche source non trouvée")
        
        # Destination
        dest_path = thumb_path_for(Path(video.path))
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copier
        shutil.copy2(source_path, dest_path)
        logger.info(f"Affiche copiée: {source_path} → {dest_path}")
        
        return {"ok": True, "poster_path": str(dest_path)}
        
    except Exception as e:
        logger.error(f"Erreur copie affiche: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


