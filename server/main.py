from fastapi import FastAPI, HTTPException, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import uuid
from typing import Literal, List, Optional
from contextlib import asynccontextmanager
from collections import defaultdict
import threading
import time
import shutil
import requests
import json
import socket
import subprocess
import os
import re
import random
import sqlite3
import uvicorn

from core.db import init_db, get_session
from core.models import Video, WatchProgress
from core.scanner import scan_all
from core.config_manager import load_settings
from core.thumbnails import ensure_thumbnail_sync, thumb_path_for
from core.file_cleaner import clean_database_filenames
from core.metadata_enricher import enrich_all_videos
from core.logger import logger, log_exception
from core.subprocess_helper import popen_hidden
from core.title_utils import extract_base_title
from api.videos import router as videos_router
from api.thumbnails import router as thumbnails_router
from api.settings import router as settings_router
from api.duplicates import router as duplicates_router
from api.filesystem import router as filesystem_router
from api.profiles import router as profiles_router

# Event global pour arrêter proprement le thread auto-scan
_shutdown_event = threading.Event()

# Sessions HLS (prototype)
HLS_BASE_DIR = (Path(__file__).parent / "static" / "hls").resolve()
HLS_BASE_DIR.mkdir(parents=True, exist_ok=True)
_hls_sessions: dict[str, dict] = {}
_hls_lock = threading.Lock()


# -------------------------------------------------------------------
# [START] Initialisation de l'application avec lifespan
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application (startup/shutdown)."""
    # Startup
    settings = load_settings()

    # 1. Nettoyage initial DÉSACTIVÉ pour démarrage rapide
    # Utilisez l'endpoint /api/clean ou les paramètres pour nettoyer manuellement
    logger.info("[INFO] Nettoyage automatique au demarrage desactive (demarrage rapide)")
    
    # 2. Validation TMDb (non-bloquante, en arrière-plan)
    if settings.tmdb_api_key:
        def _validate_tmdb():
            try:
                test_url = f"https://api.themoviedb.org/3/configuration?api_key={settings.tmdb_api_key}"
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    logger.info("[OK] Cle API TMDb validee")
                else:
                    logger.warning(f"[WARN] Cle API TMDb invalide (code {response.status_code})")
            except Exception as e:
                log_exception(e, context="lifespan - validation TMDb")
        
        threading.Thread(target=_validate_tmdb, daemon=True).start()
        logger.info("🔑 Validation de la cle TMDb en cours (arriere-plan)...")
    else:
        logger.warning("[WARN] Aucune cle API TMDb configuree - etape 2 limitee")

    # 3. Détection FFmpeg
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    if ffmpeg_installed:
        logger.info("[VIDEO] FFmpeg detecte - generation locale de miniatures activee")
    else:
        logger.warning("[WARN] FFmpeg non detecte - fallback TMDb uniquement (installer: python check_and_install_ffmpeg.py)")

    # 4. Thread périodique
    threading.Thread(target=auto_scan_worker, daemon=True).start()
    # GC sessions HLS
    threading.Thread(target=_hls_gc_worker, daemon=True).start()
    logger.info("[AUTO] Scan automatique active (toutes les 24 heures)")
    
    yield
    
    # Shutdown - Arrêt propre du thread auto-scan
    logger.info("👋 Arret de l'application...")
    _shutdown_event.set()  # Signal le thread de s'arrêter


app = FastAPI(title="HomeOne Lite", version="2.4", lifespan=lifespan)

# Création / vérification de la base SQLite
init_db()

# Gestionnaire d'exceptions global pour retourner du JSON au lieu de HTML
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Capture toutes les exceptions non gérées et retourne du JSON."""
    log_exception(exc, context=f"Erreur globale sur {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": str(exc),
            "detail": "Erreur interne du serveur"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Assure que les HTTPException retournent du JSON."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.detail,
        }
    )

# [START] MIDDLEWARE OPTIMISATIONS

# Compression GZip pour réduire taille des réponses (>500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges", "Content-Length"],
)

# Inclusion des routeurs modularisés
app.include_router(videos_router)
app.include_router(thumbnails_router)
app.include_router(settings_router)
app.include_router(duplicates_router, prefix="/api", tags=["duplicates"])
app.include_router(filesystem_router, prefix="/api/filesystem", tags=["filesystem"])

# Import du routeur profiles
app.include_router(profiles_router, prefix="/api", tags=["profiles"])

# -------------------------------------------------------------------
# [STATIC FILES] Servir le client React build
# -------------------------------------------------------------------
# Detecter le dossier client/dist (dev vs empaqueté)
if os.path.exists(Path(__file__).parent.parent / "client" / "dist"):
    # Mode dev : homeflix/client/dist
    CLIENT_DIR = Path(__file__).parent.parent / "client" / "dist"
else:
    # Mode empaqueté : resources/client/dist
    CLIENT_DIR = Path(__file__).parent.parent / "client" / "dist"

print(f"[STATIC] Dossier client: {CLIENT_DIR}")
print(f"[STATIC] Existe: {CLIENT_DIR.exists()}")

if CLIENT_DIR.exists():
    # Monter les assets statiques (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(CLIENT_DIR / "assets")), name="assets")
    print("[STATIC] Assets montes sur /assets")
    
    # NE PAS monter /avatars via StaticFiles - on va servir via une route explicite
    AVATARS_DIR = CLIENT_DIR / "avatars"
    if AVATARS_DIR.exists():
        print(f"[STATIC] Dossier avatars detecte: {AVATARS_DIR}")
    
    # Monter les autres fichiers publics (favicon, etc.)
    # On ne peut pas monter le dossier racine directement, donc on sert les fichiers individuellement


# -------------------------------------------------------------------
# [STATIC FILES] Servir les sessions HLS (prototype)
# -------------------------------------------------------------------
@app.get("/api/stream/hls/{sid}/{filename}")
def serve_hls_file(sid: str, filename: str):
    """Servez les fichiers HLS (m3u8/ts) d'une session spécifique."""
    with _hls_lock:
        sess = _hls_sessions.get(sid)
    if not sess:
        raise HTTPException(status_code=404, detail="Session HLS inconnue")
    file_path = (sess["dir"] / filename).resolve()
    # Sécurité de chemin
    if not str(file_path).startswith(str(sess["dir"])):
        raise HTTPException(status_code=400, detail="Chemin invalide")
    if not file_path.exists():
        # Pas encore prêt: laissez le player re-essayer
        raise HTTPException(status_code=404, detail="Fichier non prêt")
    # Mise à jour dernier accès
    sess["last_access"] = time.time()
    return FileResponse(str(file_path), headers={
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": "*",
    })


# -------------------------------------------------------------------
# [HTTP] Route pour servir le Service Worker avec les bons headers
# -------------------------------------------------------------------
@app.get("/sw.js")
async def serve_service_worker():
    """Sert le Service Worker avec le bon Content-Type et headers de cache."""
    sw_path = CLIENT_DIR / "sw.js"
    if not sw_path.exists():
        raise HTTPException(status_code=404, detail="Service Worker non trouvé")
    
    return FileResponse(
        sw_path,
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Service-Worker-Allowed": "/"
        }
    )


# -------------------------------------------------------------------
# [HTTP] Route pour servir version.json (versioning automatique)
# -------------------------------------------------------------------
@app.get("/version.json")
async def serve_version():
    """Sert le fichier de version pour détection de mise à jour."""
    version_path = CLIENT_DIR / "version.json"
    if not version_path.exists():
        # Si pas de fichier, retourner une version par défaut
        return {
            "version": int(time.time()),
            "buildDate": "unknown"
        }
    
    return FileResponse(
        version_path,
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


# -------------------------------------------------------------------
# [HTTP] Route pour servir les avatars avec CORS et bons en-têtes
# -------------------------------------------------------------------
@app.get("/avatars/{filename}")
async def serve_avatar(filename: str):
    """Sert les fichiers avatar (SVG) avec les bons en-têtes"""
    avatar_path = CLIENT_DIR / "avatars" / filename
    
    if not avatar_path.exists():
        raise HTTPException(status_code=404, detail=f"Avatar non trouve: {filename}")
    
    # Vérifier que c'est bien un fichier SVG autorisé
    if not filename.endswith('.svg'):
        raise HTTPException(status_code=403, detail="Seuls les fichiers SVG sont autorises")
    
    return FileResponse(
        avatar_path,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        }
    )


# -------------------------------------------------------------------
# 🧰 Helper partagé pour sérialiser Video → dict
# -------------------------------------------------------------------
def video_to_dict(v: Video) -> dict:
    """Convertit une instance Video en dictionnaire pour l'API."""
    
    # Vérifier si une affiche manuelle existe
    thumb_file = thumb_path_for(Path(v.path))
    marker_file = Path(str(thumb_file) + '.manual')
    has_manual_poster = marker_file.exists()
    
    # Convertir poster_path TMDb en URL complète
    poster_url = None
    if v.poster_path:
        if v.poster_path.startswith('/'):
            # C'est un chemin TMDb, le transformer en URL complète
            poster_url = f"https://image.tmdb.org/t/p/w500{v.poster_path}"
        else:
            # C'est déjà une URL complète
            poster_url = v.poster_path
    
    return {
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
        "poster_path": poster_url,
        "has_manual_poster": has_manual_poster,
        "collection": v.collection,  # Nom de la saga/série
        "episode_number": v.episode_number,  # Numéro dans la saga
    }


# -------------------------------------------------------------------
# [TIME] Scan automatique toutes les 24 heures
# -------------------------------------------------------------------
def auto_scan_worker():
    """Thread en arrière-plan qui scanne et nettoie automatiquement toutes les 24 heures."""
    while not _shutdown_event.is_set():
        try:
            # Attente interruptible (vérifie l'event toutes les secondes)
            if _shutdown_event.wait(timeout=86400):  # 24 heures = 86400 secondes
                break  # Arrêt demandé
            
            logger.info("[SYNC] Scan automatique en cours...")
            settings = load_settings()
            
            # 1. Nettoyer les noms de fichiers pour améliorer la reconnaissance TMDB (si activé)
            auto_clean_enabled = getattr(settings, 'auto_clean_filenames', True)
            if auto_clean_enabled:
                logger.info("🧹 Nettoyage des noms de fichiers...")
                try:
                    clean_stats = clean_database_filenames(dry_run=False, update_titles=True)
                    if clean_stats['renamed'] > 0:
                        logger.info(f"[OK] Nettoyage : {clean_stats['renamed']} fichiers renommes")
                    else:
                        logger.info("[INFO] Aucun fichier a nettoyer")
                except Exception as e:
                    log_exception(e, context="auto_scan_worker - nettoyage")
            
            # 2. Scanner les dossiers vidéos (avec détection automatique si nécessaire)
            stats = scan_all(settings, auto_detect=True)
            logger.info(f"[OK] Scan auto termine : {stats['indexed']} ajoutes, {stats['removed']} supprimes, {stats['total']} total")
        except Exception as e:
            log_exception(e, context="auto_scan_worker - scan")


SessionMode = Literal["mixed", "films", "series"]


# -------------------------------------------------------------------
# [SCAN] Filtrage selon le mode
# -------------------------------------------------------------------
def _filter_by_mode(videos: List[Video], mode: SessionMode, min_film=75, max_series=55):
    """
    Filtre les vidéos selon le mode de session.
    
    Logique:
    - Si duration_seconds disponible: utilise la durée
      * films: durée >= min_film minutes
      * series: durée <= max_series minutes
    - Sinon: utilise le chemin du fichier
      * films: chemin contient "film" (case insensitive)
      * series: chemin contient "serie" ou "series" (case insensitive, avec ou sans accents)
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
            # Sinon on utilise le chemin (normaliser les accents)
            import unicodedata
            path_normalized = unicodedata.normalize('NFD', v.path.lower())
            path_normalized = ''.join(c for c in path_normalized if unicodedata.category(c) != 'Mn')
            
            if mode == "films" and "film" in path_normalized:
                result.append(v)
            elif mode == "series" and ("serie" in path_normalized or "series" in path_normalized):
                result.append(v)
    
    return result


# -------------------------------------------------------------------
# [FILE] API : Liste des vidéos
# -------------------------------------------------------------------
# � API : Health check
# -------------------------------------------------------------------
@app.get("/api/ping")
def ping():
    """Endpoint simple pour vérifier que le serveur est en ligne."""
    return {"ok": True, "status": "running"}

# �[HTTP] API : Configuration réseau
# -------------------------------------------------------------------
@app.get("/api/network-config")
def get_network_config():
    """Retourne la configuration réseau pour que le client détecte l'URL appropriée."""
    config_path = Path(__file__).parent / "static" / "network-config.json"
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return JSONResponse(content=config)
        except Exception as e:
            logger.error(f"Erreur lecture network-config.json: {e}")
    
    # Fallback: générer la config à la volée
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    return {
        "LastUpdate": time.strftime("%Y-%m-%d %H:%M:%S"),
        "LocalURL": "http://localhost:5173",
        "WiFiURL": f"http://{local_ip}:5173" if local_ip and not local_ip.startswith("127.") else None,
        "TailscaleURL": None
    }


# -------------------------------------------------------------------
# [SYNC] API : Scan complet
# -------------------------------------------------------------------
@app.post("/api/scan")
def trigger_scan():
    """Lance un scan complet des dossiers de vidéos avec nettoyage automatique."""
    settings = load_settings()
    stats = scan_all(settings)

    # Lance l'enrichissement des métadonnées et la génération des miniatures en arrière-plan
    def _background_worker():
        try:
            with get_session() as s:
                # 1. Enrichir les métadonnées TMDb
                logger.info("[SCAN] Enrichissement des metadonnees TMDb...")
                enrich_all_videos(s, force=False)
                
                # 2. Générer les miniatures
                videos = s.query(Video).all()
                for v in videos:
                    try:
                        ensure_thumbnail_sync(v.path, force=False)
                    except Exception as e:
                        log_exception(e, context="background_worker - miniature")
        except Exception as e:
            log_exception(e, context="background_worker")

    threading.Thread(target=_background_worker, daemon=True).start()

    return {
        "ok": True, 
        "indexed": stats["indexed"], 
        "removed": stats["removed"],
        "total": stats["total"],
        "metadata": "enriching",
        "thumbnails": "generating"
    }


# -------------------------------------------------------------------
# 🧹 API : Nettoyage des noms de fichiers
# -------------------------------------------------------------------
@app.post("/api/clean-filenames")
def clean_filenames_endpoint(payload: dict | None = Body(None)):
    """
    Nettoie les noms de fichiers pour améliorer la reconnaissance TMDB.
    
    Payload optionnel:
        dry_run (bool): Si true, simulation uniquement (défaut: false)
        update_titles (bool): Met à jour les titres en BDD (défaut: true)
    """
    dry_run = payload.get("dry_run", False) if payload else False
    update_titles = payload.get("update_titles", True) if payload else True
    
    logger.info(f"🧹 Nettoyage des noms de fichiers {'(simulation)' if dry_run else '(réel)'}...")
    
    try:
        stats = clean_database_filenames(dry_run=dry_run, update_titles=update_titles)
        
        return {
            "ok": True,
            "dry_run": dry_run,
            "total": stats["total"],
            "renamed": stats["renamed"],
            "skipped": stats["skipped"],
            "errors": stats["errors"]
        }
    except Exception as e:
        log_exception(e, context="clean_filenames_endpoint")
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage : {str(e)}")


# -------------------------------------------------------------------
# ▶️ API : Ouvrir une vidéo
# -------------------------------------------------------------------
## ancien endpoint open_video supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# 🎲 API : Vidéo aléatoire
# -------------------------------------------------------------------
## ancien endpoint random_video supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# [IMAGE] API : Miniature
# -------------------------------------------------------------------
## ancien endpoint thumbnail supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# [VIDEO] API : Stream vidéo
# -------------------------------------------------------------------
@app.get("/api/stream")
def stream_video(path: str, range: Optional[str] = Header(None)):
    """
    Streaming vidéo avec support du Range (permet le seek).
    """
    logger.info(f"📹 Stream demande: {path}")
    video_path = Path(path)
    logger.info(f"📹 Chemin resolu: {video_path.absolute()}")
    logger.info(f"📹 Fichier existe: {video_path.exists()}")
    if not video_path.exists():
        logger.error(f"[ERROR] ERREUR: Fichier introuvable!")
        raise HTTPException(status_code=404, detail=f"Fichier vidéo introuvable: {path}")
    
    file_size = video_path.stat().st_size
    
    # Support du Range header pour le seek
    if range:
        # Parse le range header (format: "bytes=start-end")
        range_match = range.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
    else:
        # Par défaut, envoyer tout le fichier
        start = 0
        end = file_size - 1
    
    chunk_size = end - start + 1
    
    # Générateur de chunks optimisé pour grosses vidéos (stratégie progressive agressive)
    def iter_file():
        with open(video_path, 'rb') as video_file:
            video_file.seek(start)
            remaining = chunk_size
            chunk_count = 0
            while remaining > 0:
                # Stratégie de chunking ultra-optimisée pour grosses vidéos :
                # - Premier chunk : plus large pour MP4/MOV (moov/ftyp en tête)
                #                    sinon 128 KB pour démarrage instantané
                # - Chunks 2-3 : 1 MB pour buffer initial rapide
                # - Chunks 4-10 : 4 MB pour montée en charge
                # - Chunks suivants : 16 MB pour débit maximal (grosses vidéos)
                if chunk_count == 0:
                    # Pour les conteneurs MP4/M4V/MOV, on envoie un premier chunk
                    # plus grand afin d'inclure les boxes ftyp/moov et permettre
                    # une lecture immédiate même sur fichiers volumineux.
                    if extension in ('.mp4', '.m4v', '.mov'):
                        read_size = min(512 * 1024, remaining)  # 512 KB - init segment probable
                    else:
                        read_size = min(128 * 1024, remaining)  # 128 KB - démarrage ultra-rapide
                elif chunk_count < 3:
                    read_size = min(1 * 1024 * 1024, remaining)  # 1 MB - buffer initial
                elif chunk_count < 10:
                    read_size = min(4 * 1024 * 1024, remaining)  # 4 MB - montée progressive
                else:
                    read_size = min(16 * 1024 * 1024, remaining)  # 16 MB - streaming haute performance
                
                data = video_file.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                chunk_count += 1
                yield data
    
    # Détecter le type MIME
    extension = video_path.suffix.lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.webm': 'video/webm',
        '.flv': 'video/x-flv',
        '.wmv': 'video/x-ms-wmv'
    }
    media_type = mime_types.get(extension, 'video/mp4')
    
    # Headers optimisés pour streaming vidéo performant
    if range:
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': media_type,
            'Cache-Control': 'public, max-age=7200, immutable',  # Cache 2h, contenu immuable
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=60, max=100',  # Maintenir connexion 60s, max 100 requêtes
            'X-Content-Type-Options': 'nosniff',
            'Access-Control-Expose-Headers': 'Content-Range, Content-Length',
        }
        status_code = 206
    else:
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': media_type,
            'Cache-Control': 'public, max-age=7200, immutable',  # Cache 2h, contenu immuable
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=60, max=100',
            'X-Content-Type-Options': 'nosniff',
        }
        status_code = 200
    
    return StreamingResponse(
        iter_file(),
        status_code=status_code,
        headers=headers,
        media_type=media_type
    )


# -------------------------------------------------------------------
# � API : Lister les pistes audio/sous-titres disponibles
# -------------------------------------------------------------------
@app.get("/api/stream/tracks")
def get_video_tracks(path: str):
    """
    Retourne la liste des pistes audio et sous-titres d'une vidéo avec ffprobe.
    """
    video_path = Path(path)
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Fichier introuvable: {path}")
    
    probe_cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", str(video_path)
    ]
    
    try:
        # Certaines sources réseaux/USB peuvent nécessiter plus de 10s
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=25)
        if result.returncode != 0 or not result.stdout:
            logger.warning(f"[TRACKS] ffprobe rc={result.returncode} | stderr={result.stderr[:200] if result.stderr else ''}")
            return { 'audio': [], 'subtitles': [] }
        data = json.loads(result.stdout)
        
        streams = data.get('streams', [])
        
        audio_tracks = []
        subtitle_tracks = []
        
        for stream in streams:
            if stream.get('codec_type') == 'audio':
                audio_tracks.append({
                    'index': stream.get('index'),
                    'codec': stream.get('codec_name'),
                    'channels': stream.get('channels', 2),
                    'language': stream.get('tags', {}).get('language', 'unknown'),
                    'title': stream.get('tags', {}).get('title', f"Audio {len(audio_tracks) + 1}")
                })
            elif stream.get('codec_type') == 'subtitle':
                subtitle_tracks.append({
                    'index': stream.get('index'),
                    'codec': stream.get('codec_name'),
                    'language': stream.get('tags', {}).get('language', 'unknown'),
                    'title': stream.get('tags', {}).get('title', f"Subtitle {len(subtitle_tracks) + 1}")
                })
        
        return {
            'audio': audio_tracks,
            'subtitles': subtitle_tracks
        }
        
    except Exception as e:
        logger.error(f"[TRACKS] Erreur ffprobe: {e}")
        # Fallback gracieux: ne pas bloquer l'UI si l'analyse échoue
        return { 'audio': [], 'subtitles': [] }


# -------------------------------------------------------------------
# [NOTE] API : Extraire sous-titres en WebVTT
# -------------------------------------------------------------------
@app.get("/api/stream/subtitle")
def get_subtitle(path: str, subtitle_track: int):
    """
    Extrait une piste de sous-titres en format WebVTT pour affichage HTML5.
    """
    video_path = Path(path)
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    
    if not shutil.which("ffmpeg"):
        raise HTTPException(status_code=500, detail="FFmpeg non installé")
    
    logger.info(f"[NOTE] Extraction sous-titre piste {subtitle_track} depuis: {video_path.name}")
    
    # Commande FFmpeg pour extraire le sous-titre en WebVTT
    ffmpeg_cmd = [
        "ffmpeg",
        "-loglevel", "error",  # Réduire les logs FFmpeg
        "-i", str(video_path),
        "-map", f"0:{subtitle_track}",
        "-f", "webvtt",
        "-"  # Sortie vers stdout
    ]
    
    try:
        # Lancer FFmpeg en mode streaming
        process = popen_hidden(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        def generate():
            """Streamer le contenu WebVTT au fur et à mesure"""
            try:
                chunk_count = 0
                total_size = 0
                while True:
                    chunk = process.stdout.read(8192)
                    if not chunk:
                        break
                    chunk_count += 1
                    total_size += len(chunk)
                    yield chunk
                
                # Vérifier le code de retour après avoir tout lu
                process.wait()
                if process.returncode != 0:
                    stderr_output = process.stderr.read().decode('utf-8', errors='replace')
                    logger.error(f"[ERROR] Erreur FFmpeg extraction sous-titre: {stderr_output}")
                else:
                    logger.info(f"[OK] Sous-titre extrait: {total_size} octets ({chunk_count} chunks)")
                    
            except Exception as e:
                logger.error(f"[ERROR] Erreur streaming sous-titre: {e}")
                process.kill()
            finally:
                process.stdout.close()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        return StreamingResponse(
            generate(),
            media_type="text/vtt",
            headers={
                "Content-Type": "text/vtt; charset=utf-8",
                "Cache-Control": "no-cache",  # Pas de cache pour debug
                "Access-Control-Allow-Origin": "*"
            }
        )
    
    except Exception as e:
        logger.error(f"[ERROR] Erreur extraction sous-titre: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# 🎬 [VIDEO] API : Stream vidéo avec transcodage (pour MKV, AVI, etc.)
# -------------------------------------------------------------------
@app.options("/api/stream/transcode")
async def stream_transcode_preflight():
    """Gère la requête OPTIONS pour CORS preflight"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )

@app.get("/api/stream/transcode")
def stream_video_transcode(path: str, audio_track: int = 0, subtitle_track: int = -1, quality: str = "medium"):
    """
    Transcode les vidéos non supportées (MKV, AVI) en MP4 à la volée avec FFmpeg.
    Garde TOUTES les pistes audio et sous-titres pour permettre la sélection dans le player.
    """
    video_path = Path(path)
    
    logger.info(f"[VIDEO] TRANSCODAGE demandé")
    logger.info(f"   Chemin reçu: {path}")
    logger.info(f"   Chemin normalisé: {video_path}")
    logger.info(f"   Fichier existe: {video_path.exists()}")
    
    if not video_path.exists():
        logger.error(f"   ❌ FICHIER INTROUVABLE!")
        logger.error(f"   Chemin complet: {video_path.absolute()}")
        logger.error(f"   Dossier parent: {video_path.parent}")
        logger.error(f"   Parent existe: {video_path.parent.exists()}")
        raise HTTPException(status_code=404, detail=f"Fichier vidéo introuvable: {path}")
    else:
        try:
            file_size = video_path.stat().st_size / 1024 / 1024
            logger.info(f"   ✅ Fichier trouvé - Taille: {file_size:.1f} MB")
        except Exception as e:
            logger.error(f"   ❌ Erreur stat fichier: {e}")
            pass
    
    # Vérifier que FFmpeg est disponible
    if not shutil.which("ffmpeg"):
        raise HTTPException(status_code=500, detail="FFmpeg non installé sur le serveur")
    
    # ================================================================================
    # 🎬 ANALYSE COMPLÈTE DES CODECS VIDÉO ET AUDIO (avec ffprobe)
    # ================================================================================
    probe_cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", str(video_path)
    ]
    
    video_codec = None
    video_profile = None
    video_width = 0
    video_height = 0
    needs_video_conversion = True
    needs_audio_conversion = False
    audio_streams = []
    audio_indices: list[int] = []
    
    try:
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=15)
        probe_data = json.loads(probe_result.stdout)
        
        # 📹 Analyser le stream vidéo
        video_streams = [s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video']
        if video_streams:
            video_stream = video_streams[0]
            video_codec = video_stream.get('codec_name', '')
            video_profile = video_stream.get('profile', '')
            video_width = int(video_stream.get('width', 0))
            video_height = int(video_stream.get('height', 0))
            
            # 🎬 CODECS VIDÉO COMPATIBLES NAVIGATEURS (copie directe possible)
            # Navigateurs modernes supportent : H.264, H.265/HEVC, VP8, VP9, AV1
            # ⚠️ IMPORTANT : MPEG4/XVID/DIVX/MSMPEG4 nécessitent TOUJOURS un transcodage
            # 
            # 🔧 STRATÉGIE CONSERVATIVE : Seul H.264 baseline/main/high est accepté en COPY
            #    Tous les autres codecs (même H.265) seront transcodés pour garantir compatibilité maximale
            mp4_compatible_video = [
                'h264', 'avc',           # H.264 uniquement (codec le plus universel)
            ]
            
            # TOUS les autres codecs seront transcodés en H.264 pour compatibilité universelle
            # ⚠️ DÉSACTIVATION TEMPORAIRE DU MODE COPY pour les fichiers MKV
            # Raison : Les MKV peuvent avoir des métadonnées/timing incompatibles avec MP4
            is_mkv = str(video_path).lower().endswith('.mkv')
            
            if video_codec.lower() in mp4_compatible_video and not is_mkv:
                # Vérifier le profil H.264 (seuls baseline, main, high sont sûrs)
                safe_profiles = ['baseline', 'main', 'high', 'constrained baseline']
                if video_profile and video_profile.lower() not in [p.lower() for p in safe_profiles]:
                    logger.info(f"   ⚠️ [VIDEO] Profil H.264 '{video_profile}' non standard - TRANSCODAGE par sécurité")
                    needs_video_conversion = True
                else:
                    needs_video_conversion = False
                    logger.info(f"   ✅ [VIDEO] Codec {video_codec.upper()} profil {video_profile} compatible - COPIE DIRECTE")
            elif is_mkv and video_codec.lower() in mp4_compatible_video:
                # Pour les MKV avec H.264, transcoder par précaution
                logger.info(f"   ⚠️ [VIDEO] Fichier MKV détecté - TRANSCODAGE forcé pour compatibilité MP4")
                logger.info(f"      → Conversion H.264 → H.264 (remuxing + correction timing)")
                needs_video_conversion = True
            else:
                logger.info(f"   ⚠️ [VIDEO] Codec {video_codec.upper()} incompatible - TRANSCODAGE requis")
                logger.info(f"      → Conversion vers H.264 (compatibilité universelle)")
        else:
            logger.warning(f"   ❌ [VIDEO] Aucun stream vidéo détecté dans le fichier!")
            logger.warning(f"      → FFmpeg tentera quand même le transcodage...")
        
        # 🎵 Analyser les streams audio
        audio_streams = [s for s in probe_data.get('streams', []) if s.get('codec_type') == 'audio']
        audio_indices = [int(s.get('index')) for s in audio_streams if s.get('index') is not None]
        
        # Politique stricte pour compatibilité HTML5/MP4 dans navigateurs :
        # - On ne considère compatible en copie directe que AAC en ≤ 2 canaux
        # - Tous les autres (MP3, AC3, E-AC3, DTS, OPUS, etc.) seront convertis en AAC stéréo
        # ⚠️ IMPORTANT : MP3 retiré car non universellement supporté dans MP4 par tous les navigateurs
        mp4_copy_allowed = ['aac']

        needs_audio_conversion = False
        for s in audio_streams:
            codec = s.get('codec_name', '')
            channels = int(s.get('channels', 2) or 2)
            if codec not in mp4_copy_allowed or channels > 2:
                needs_audio_conversion = True
                break
        
        if needs_audio_conversion:
            logger.info(f"   ⚠️ [AUDIO] Conversion en AAC stéréo requise pour compatibilité navigateur")
        else:
            logger.info(f"   ✅ [AUDIO] Codec compatible (AAC ≤ 2ch) - copie directe")
        
        # Afficher résolution
        if video_width > 0:
            logger.info(f"   📐 Résolution source: {video_width}x{video_height}")
            
    except Exception as e:
        logger.error(f"   ❌ Erreur analyse FFprobe: {e}")
        logger.warning(f"   ⚠️ Fallback: Transcodage forcé par sécurité")
        needs_video_conversion = True
        needs_audio_conversion = True
    
    # Sélection audio robuste: si l'index demandé n'est pas une piste audio réelle,
    # basculer automatiquement sur la première piste audio disponible.
    selected_audio_index = audio_track
    if not audio_indices:
        logger.warning("   ❌ Aucune piste audio détectée par ffprobe - FFmpeg tentera la sortie sans audio")
        selected_audio_index = None
    elif audio_track not in audio_indices:
        fallback_idx = audio_indices[0]
        logger.warning(
            f"   ⚠️ Piste audio {audio_track} inexistante → fallback vers {fallback_idx}"
        )
        selected_audio_index = fallback_idx
    else:
        logger.info(f"   🎵 Piste audio sélectionnée: {audio_track}")
    if subtitle_track >= 0:
        logger.info(f"   [NOTE] Sous-titre selectionne: {subtitle_track}")
    
    # ================================================================================
    # 🚀 CONFIGURATION FFmpeg OPTIMISÉE AVEC DÉTECTION GPU
    # ================================================================================
    
    # Détecter si une accélération GPU est disponible ET FONCTIONNELLE
    gpu_encoder = None
    try:
        # Test NVIDIA NVENC avec un vrai test d'encodage
        nvenc_test = subprocess.run(
            ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=1", 
             "-c:v", "h264_nvenc", "-f", "null", "-"],
            capture_output=True, text=True, timeout=5
        )
        if nvenc_test.returncode == 0:
            gpu_encoder = "h264_nvenc"
            logger.info(f"   🎮 GPU NVIDIA détecté - Utilisation NVENC")
        else:
            # Test Intel Quick Sync
            qsv_test = subprocess.run(
                ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=1", 
                 "-c:v", "h264_qsv", "-f", "null", "-"],
                capture_output=True, text=True, timeout=5
            )
            if qsv_test.returncode == 0:
                gpu_encoder = "h264_qsv"
                logger.info(f"   🎮 GPU Intel détecté - Utilisation Quick Sync")
    except:
        pass
    
    if not gpu_encoder:
        logger.info(f"   💻 Pas de GPU détecté - Utilisation CPU (libx264)")
    
    # ================================================================================
    # 📊 PROFILS DE QUALITÉ OPTIMISÉS
    # ================================================================================
    if quality == "fast":
        # Profil bas : pour connexions lentes ou démarrage rapide
        crf = "28"
        preset = "veryfast" if not gpu_encoder else "fast"
        target_height = 720
        audio_bitrate = "96k"
    elif quality == "high":
        # Profil haute qualité : préserver qualité source
        crf = "18"
        preset = "slow" if not gpu_encoder else "medium"
        target_height = 1080
        audio_bitrate = "192k"
    else:  # medium (par défaut)
        # Profil équilibré : bon compromis qualité/vitesse
        crf = "21"
        preset = "medium" if not gpu_encoder else "medium"
        target_height = 1080
        audio_bitrate = "128k"
    
    # Adapter la résolution si source < target
    if video_height > 0 and video_height < target_height:
        scale_filter = f"scale=-2:{video_height}"  # Garder résolution source
        logger.info(f"   📐 Résolution conservée: {video_height}p (source < {target_height}p)")
    else:
        scale_filter = f"scale=-2:{target_height}"
        logger.info(f"   📐 Résolution cible: {target_height}p")
    
    # ================================================================================
    # 🔧 CONSTRUCTION COMMANDE FFmpeg INTELLIGENTE
    # ================================================================================
    ffmpeg_cmd = [
        "ffmpeg",
        "-analyzeduration", "20M",  # Augmenté à 20M pour fichiers complexes
        "-probesize", "20M",
        "-fflags", "+genpts+igndts",
        "-i", str(video_path),
        "-map", "0:v:0",
    ]

    # Mapping audio uniquement si une piste valide est connue
    if selected_audio_index is not None:
        ffmpeg_cmd.extend(["-map", f"0:{selected_audio_index}"])
    else:
        logger.warning("   ⚠️ Aucun mapping audio appliqué (pas de piste valide)")

    # Reprise de la construction de la commande
    ffmpeg_cmd += [
    ]
    
    # Configuration VIDÉO : Copie OU Transcodage selon codec détecté
    if needs_video_conversion:
        # TRANSCODAGE NÉCESSAIRE
        encoder = gpu_encoder if gpu_encoder else "libx264"
        ffmpeg_cmd.extend([
            "-c:v", encoder,
            "-preset", preset,
            "-crf", crf if not gpu_encoder else str(int(crf) + 5),  # CRF+5 pour GPU
            "-vf", scale_filter,
            "-pix_fmt", "yuv420p",  # Compatibilité maximale
        ])
        # Améliorer la stabilité du flux (GOP/latence) surtout pour AVI/MKV problématiques
        # 🔧 CORRECTION CRITIQUE : GOP réduite de 48 → 24 frames (1s à 24fps)
        # - Fragments MP4 plus petits et plus fréquents
        # - Meilleure compatibilité avec le buffering navigateur
        # - Réduit le risque de fragments incomplets dans les chunks
        if encoder == "libx264":
            ffmpeg_cmd.extend([
                "-g", "24",           # GOP de 1 seconde (keyframe chaque seconde)
                "-keyint_min", "24",  # Forcer keyframe minimum = GOP
                "-sc_threshold", "0", # Désactiver détection de scène (GOP fixe)
                "-tune", "zerolatency",
                "-x264opts", "no-scenecut"  # Double garantie : pas de scene-cut
            ])
        else:
            # NVENC/QSV acceptent -g mais pas -tune zerolatency
            ffmpeg_cmd.extend([
                "-g", "24",
                "-keyint_min", "24",
                "-sc_threshold", "0"
            ])
        
        # Paramètres spécifiques GPU
        if gpu_encoder == "h264_nvenc":
            ffmpeg_cmd.extend(["-rc:v", "vbr", "-b:v", "0"])  # VBR pour qualité
        elif gpu_encoder == "h264_qsv":
            ffmpeg_cmd.extend(["-look_ahead", "1"])
    else:
        # COPIE DIRECTE - Pas de réencodage vidéo  
        ffmpeg_cmd.extend(["-c:v", "copy"])
        logger.info(f"   ⚡ Mode COPY activé - Pas de réencodage vidéo")
    
    # Configuration AUDIO : Copie OU Conversion en AAC stéréo
    if needs_audio_conversion:
        ffmpeg_cmd.extend([
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-ar", "48000",
            "-ac", "2",  # Stéréo pour compatibilité navigateurs
        ])
    else:
        # Copie audio direct MAIS force stéréo si > 2 canaux
        # Identifier la piste audio sélectionnée pour lire ses métadonnées
        selected_audio_stream = None
        if selected_audio_index is not None:
            for s in audio_streams:
                if int(s.get('index')) == selected_audio_index:
                    selected_audio_stream = s
                    break
        # Fallback sur première piste si non trouvé
        if not selected_audio_stream and audio_streams:
            selected_audio_stream = audio_streams[0]

        if selected_audio_stream and selected_audio_stream.get('channels', 2) > 2:
            logger.info(f"   🎵 Downmix audio {audio_streams[0].get('channels')}ch → 2ch (stéréo)")
            ffmpeg_cmd.extend([
                "-c:a", "aac",
                "-b:a", audio_bitrate,
                "-ac", "2",
            ])
        else:
            ffmpeg_cmd.extend(["-c:a", "copy"])
    
    # Paramètres de sortie MP4 fragmenté
    # 🔧 CORRECTION CRITIQUE : Utilisation de frag_every_frame pour fragments plus petits
    # - frag_every_frame : Crée un fragment pour chaque frame (très petit, très fiable)
    # - empty_moov : Header moov vide (métadonnées dans chaque moof)
    # - default_base_moof : Timing relatif dans chaque fragment
    # - omit_tfhd_offset : Éviter les offsets qui peuvent corrompre le stream
    # 
    # ✅ FALLBACK : Si frag_duration ne fonctionne pas, utiliser frag_keyframe
    # ❌ RETIRÉ : faststart, isml, dash (conçus pour fichiers complets, pas streaming pipe)
    ffmpeg_cmd.extend([
        "-f", "mp4",
        "-movflags", "frag_keyframe+empty_moov+default_base_moof+omit_tfhd_offset",
        # ⚡ TIMING CRITIQUE : Envoyer headers IMMÉDIATEMENT pour éviter timeout navigateur
        "-fflags", "+nobuffer+flush_packets",
        "-flush_packets", "1",
        # Muxing/Interleave pour réduire les risques de blocage en lecture progressive
        "-max_interleave_delta", "0",
        "-muxpreload", "0",
        "-muxdelay", "0",
        "-max_muxing_queue_size", "9999",
        "-avoid_negative_ts", "make_zero",
        "-threads", "0",
        "pipe:1"
    ])
    
    # ================================================================================
    # 🎬 GÉNÉRATEUR DE STREAMING FFmpeg
    # ================================================================================
    def transcode_stream():
        mode_str = "COPY" if not needs_video_conversion else f"TRANSCODAGE ({encoder})"
        logger.info(f"[PROCESS] Lancement FFmpeg - Mode: {mode_str}")
        logger.info(f"   Commande complète:")
        for i, arg in enumerate(ffmpeg_cmd):
            if i % 10 == 0 and i > 0:
                logger.info(f"      {' '.join(ffmpeg_cmd[i:i+10])}")
            elif i == 0:
                logger.info(f"      {' '.join(ffmpeg_cmd[0:10])}")
        logger.info(f"   Buffer initial: 512 KB → 1 MB → 2 MB | Streaming progressif optimisé MP4")
        logger.info(f"   Fichier source: {video_path}")
        
        try:
            process = popen_hidden(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=2*1024*1024  # Buffer 2 MB pour éviter les stalls
            )
        except Exception as e:
            logger.error(f"❌ [FFMPEG] Impossible de démarrer le processus: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur démarrage FFmpeg: {e}")
        
        # Lire les premières lignes de stderr pour voir si FFmpeg démarre bien
        stderr_lines = []
        ffmpeg_started = threading.Event()
        
        def read_stderr():
            try:
                for line in process.stderr:
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    stderr_lines.append(line_str)
                    if 'Stream #0:' in line_str or 'Output #0' in line_str:
                        logger.info(f"   FFmpeg: {line_str}")
                        ffmpeg_started.set()  # Signal que FFmpeg a bien démarré
                    # Détecter les erreurs critiques de FFmpeg
                    if any(err in line_str.lower() for err in ['invalid', 'error', 'failed', 'cannot', 'unsupported']):
                        logger.error(f"   ⚠️ FFmpeg: {line_str}")
            except:
                pass
        
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()
        
        # Attendre que FFmpeg démarre (max 3 secondes)
        if not ffmpeg_started.wait(timeout=3.0):
            logger.warning("⚠️ [FFMPEG] FFmpeg n'a pas envoyé de confirmation de démarrage dans les 3s")
            logger.warning("   → Lecture stderr disponible:")
            for line in stderr_lines[-5:]:
                logger.warning(f"      {line}")
        else:
            logger.info("✅ [FFMPEG] Processus démarré et prêt à encoder")
        
        chunk_count = 0
        total_sent = 0
        first_chunk_sent = False
        
        try:
            while True:
                # ✅ STRATÉGIE DE CHUNKS OPTIMISÉE POUR STREAMING LONG
                # 🔧 NOUVELLE APPROCHE : Chunks constants de 512 KB après l'init
                # - Réduit la latence de buffering
                # - Évite les blocages après plusieurs minutes
                # - Meilleur équilibre performance/réactivité
                if chunk_count == 0:
                    # Premier chunk : 2 MB pour garantir moov+moof+mdat complet
                    chunk_size = 2 * 1024 * 1024
                else:
                    # Tous les autres : 512 KB constant (optimal pour streaming)
                    chunk_size = 512 * 1024
                
                chunk = process.stdout.read(chunk_size)
                    
                if not chunk:
                    # Vérifier si FFmpeg s'est arrêté avec une erreur (ex: -map invalide)
                    try:
                        rc = process.wait(timeout=0.5)
                    except Exception:
                        rc = None
                    if rc not in (None, 0):
                        # Lire quelques lignes d'erreur pour diagnostic
                        logger.error(f"❌ [FFMPEG] Arrêt prématuré (rc={rc}). Détails:")
                        try:
                            err_tail = []
                            for _ in range(20):
                                line = process.stderr.readline()
                                if not line:
                                    break
                                err_tail.append(line.decode('utf-8', errors='ignore').strip())
                            if err_tail:
                                for l in err_tail[-10:]:
                                    logger.error(f"   {l}")
                            else:
                                logger.error("   (Aucune sortie stderr disponible)")
                        except Exception as err_e:
                            logger.error(f"   Erreur lecture stderr: {err_e}")
                        
                        # Si c'est le premier chunk qui échoue, c'est un problème critique
                        if chunk_count == 0:
                            logger.error("❌ [FFMPEG] ÉCHEC DÈS LE PREMIER CHUNK - Fichier probablement corrompu ou codec invalide")
                            logger.error(f"   Fichier: {video_path}")
                            logger.error(f"   Codec détecté: {video_codec}")
                    logger.info(f"📊 [STREAMING] Fin - Total envoyé: {total_sent / 1024 / 1024:.1f} MB")
                    break
                    
                chunk_count += 1
                total_sent += len(chunk)
                
                # Log du premier chunk (CRITIQUE pour démarrage)
                if chunk_count == 1:
                    logger.info(f"✅ [STREAMING] Premier chunk envoyé - Lecture IMMÉDIATE ({len(chunk)/1024:.1f} KB)")
                    # Vérifier si le chunk contient les boxes MP4 essentielles
                    if b'ftyp' in chunk[:100]:
                        logger.info(f"   ✅ ftyp box détectée (File Type)")
                    else:
                        logger.warning(f"   ⚠️ ftyp box manquante dans le premier chunk!")
                    
                    if b'moov' in chunk:
                        logger.info(f"   ✅ moov box détectée (Movie Header)")
                    else:
                        logger.warning(f"   ⚠️ moov box manquante dans le premier chunk!")
                    
                    if b'moof' in chunk:
                        logger.info(f"   ✅ moof box détectée (Movie Fragment)")
                    else:
                        logger.warning(f"   ⚠️ moof box manquante - le navigateur pourrait rejeter le stream!")
                    
                    first_chunk_sent = True
                
                # Log à 1 MB envoyé (buffer navigateur rempli)
                elif not first_chunk_sent and total_sent > 1024 * 1024:
                    logger.info(f"📦 [STREAMING] 1 MB buffered - Lecture devrait démarrer")
                    first_chunk_sent = True
                
                # Log périodique tous les 100 chunks (~200 MB)
                elif chunk_count % 100 == 0:
                    logger.info(f"📊 [STREAMING] {total_sent / 1024 / 1024:.1f} MB envoyés ({chunk_count} chunks)")
                
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ [ERROR] Erreur transcodage FFmpeg: {e}")
            # Afficher les dernières lignes de stderr pour diagnostic
            if stderr_lines:
                logger.error(f"   📋 FFmpeg stderr (10 dernières lignes):")
                for line in stderr_lines[-10:]:
                    logger.error(f"      {line}")
            else:
                logger.error(f"   Aucune sortie stderr FFmpeg disponible")
        finally:
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                process.kill()
                process.wait()
    
    return StreamingResponse(
        transcode_stream(),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "none",
            "Content-Type": "video/mp4",
            "Connection": "keep-alive",  # Maintenir la connexion
            "Cache-Control": "no-cache",  # Éviter le cache pour le transcodage
            # ✅ Headers CORS explicites pour l'élément <video> HTML5
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Type",
            "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges"
        }
    )


# -------------------------------------------------------------------
# 🧪 [VIDEO] API : Prototype HLS transcodé à la volée
# -------------------------------------------------------------------
@app.get("/api/stream/hls/start")
def start_hls_session(path: str, audio_track: int = 0, quality: str = "medium"):
    """
    Démarre une session HLS en générant une playlist et des segments dans un dossier temporaire
    et renvoie l'URL de la playlist.
    """
    video_path = Path(path)
    # Logs détaillés d'entrée
    try:
        logger.info(f"[HLS] Reçu start pour: {path}")
    except Exception:
        pass
    if not video_path.exists():
        logger.warning(f"[HLS] Fichier introuvable pour HLS: {path}")
        raise HTTPException(status_code=404, detail="Fichier vidéo introuvable")
    if not shutil.which("ffmpeg"):
        logger.error("[HLS] FFmpeg non installé - impossible de démarrer HLS")
        raise HTTPException(status_code=500, detail="FFmpeg non installé sur le serveur")

    # Création dossier session
    sid = uuid.uuid4().hex
    out_dir = (HLS_BASE_DIR / sid)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Choix qualité simple
    if quality == "fast":
        crf = "28"; preset = "veryfast"; target_height = 720; audio_bitrate = "96k"
    elif quality == "high":
        crf = "20"; preset = "slow"; target_height = 1080; audio_bitrate = "192k"
    else:
        crf = "23"; preset = "medium"; target_height = 1080; audio_bitrate = "128k"

    # Encodage vidéo: pour fiabilité du prototype HLS, on force libx264
    # (NVENC/QSV ont des jeux d'options différents de libx264 : 'veryfast' non valide NVENC,
    #  'crf' non supporté; on pourra optimiser GPU plus tard)
    encoder = "libx264"

    # Construction commande FFmpeg → HLS
    playlist_name = "playlist.m3u8"
    master_name = "master.m3u8"
    segment_name = "segment_%05d.ts"

    scale_filter = f"scale=-2:{target_height}"

    # Déterminer la meilleure piste audio à mapper (fallback si index invalide)
    selected_audio_index = None
    try:
        probe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", str(video_path)
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=15)
        if probe_result.returncode == 0 and probe_result.stdout:
            pdata = json.loads(probe_result.stdout)
            a_streams = [s for s in pdata.get('streams', []) if s.get('codec_type') == 'audio']
            a_indices = [int(s.get('index')) for s in a_streams if s.get('index') is not None]
            if a_indices:
                if audio_track in a_indices:
                    selected_audio_index = audio_track
                else:
                    selected_audio_index = a_indices[0]
                    logger.info(f"[HLS] Piste audio {audio_track} invalide → fallback {selected_audio_index}")
            else:
                logger.warning("[HLS] Aucune piste audio détectée pour HLS")
        else:
            logger.warning("[HLS] ffprobe n'a pas retourné de données pour la détection audio")
    except Exception as e:
        logger.warning(f"[HLS] Échec détection pistes audio: {e}")

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-analyzeduration", "10M",
        "-probesize", "10M",
        "-i", str(video_path),
        "-map", "0:v:0",
    ]
    if selected_audio_index is not None:
        ffmpeg_cmd += ["-map", f"0:{selected_audio_index}"]
    else:
        # Pas d'audio mappé
        logger.info("[HLS] Démarrage sans piste audio mappée")
    ffmpeg_cmd += [
    "-c:v", encoder,
    "-preset", preset,
    "-crf", crf,
        "-vf", scale_filter,
        "-pix_fmt", "yuv420p",
    ]
    if selected_audio_index is not None:
        ffmpeg_cmd += [
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-ar", "48000",
            "-ac", "2",
        ]
    ffmpeg_cmd += [
        "-f", "hls",
        "-hls_time", "4",
        "-hls_list_size", "10",
        # Prototype test-friendly: ne pas supprimer les segments trop vite
        "-hls_flags", "append_list+independent_segments+program_date_time",
        "-master_pl_name", master_name,
        "-hls_segment_filename", str(out_dir / segment_name),
        str(out_dir / playlist_name)
    ]

    logger.info(f"[HLS] Démarrage session {sid} → {video_path.name}")
    logger.info(f"      Cmd: {' '.join(ffmpeg_cmd[:12])} ...")

    try:
        proc = popen_hidden(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Lire stderr en arrière-plan pour diagnostiquer
        def _stderr_reader(p):
            try:
                for line in p.stderr:
                    try:
                        s = line.decode('utf-8', errors='ignore').strip()
                    except Exception:
                        s = str(line)
                    if s:
                        logger.info(f"[HLS][ffmpeg] {s}")
            except Exception:
                pass
        threading.Thread(target=_stderr_reader, args=(proc,), daemon=True).start()
    except Exception as e:
        logger.error(f"[HLS] Échec démarrage FFmpeg: {e}")
        shutil.rmtree(out_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="Échec démarrage FFmpeg HLS")

    with _hls_lock:
        _hls_sessions[sid] = {
            "dir": out_dir,
            "process": proc,
            "last_access": time.time(),
            "source": video_path,
        }

    # URL playlist publique (via route serve_hls_file)
    playlist_url = f"/api/stream/hls/{sid}/{master_name}"
    return {"ok": True, "sid": sid, "playlist_url": playlist_url}


@app.get("/api/stream/hls/stop")
def stop_hls_session(sid: str):
    with _hls_lock:
        sess = _hls_sessions.pop(sid, None)
    if not sess:
        return {"ok": True, "stopped": False}
    try:
        proc = sess.get("process")
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except Exception:
                proc.kill()
        shutil.rmtree(sess["dir"], ignore_errors=True)
    except Exception as e:
        logger.warning(f"[HLS] Nettoyage session {sid} partiel: {e}")
    return {"ok": True, "stopped": True}


# Nettoyage périodique des sessions HLS inactives (>10 min)
def _hls_gc_worker():
    while not _shutdown_event.is_set():
        time.sleep(60)
        now = time.time()
        stale: list[str] = []
        with _hls_lock:
            for sid, sess in list(_hls_sessions.items()):
                if now - sess.get("last_access", now) > 600:  # 10 min
                    stale.append(sid)
        for sid in stale:
            logger.info(f"[HLS] GC session idle {sid}")
            try:
                stop_hls_session(sid)
            except Exception:
                pass

# 💾 API : Sauvegarder la progression
# -------------------------------------------------------------------
## ancien endpoint save_progress supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# [IMAGE] API : Générer toutes les miniatures
# -------------------------------------------------------------------
## ancien endpoint generate_thumbnails supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# [SYNC] API : Régénérer les miniatures manquantes
# -------------------------------------------------------------------
## ancien endpoint repair_thumbnails supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# [TARGET] API : Enrichir les métadonnées TMDb
# -------------------------------------------------------------------
@app.post("/api/metadata/enrich")
def enrich_metadata(payload: dict | None = Body(None), force: bool = Query(False)):
    """
    Enrichit les métadonnées de toutes les vidéos via TMDb.
    
    Payload optionnel:
        force (bool): Force la mise à jour même si déjà enrichi (défaut: false)
    """
    # Supporte à la fois un body JSON et un query param ?force=true
    force = payload.get("force", force) if payload else force
    
    logger.info(f"Enrichissement des metadonnees TMDb {'(force)' if force else ''}...")
    
    try:
        with get_session() as s:
            stats = enrich_all_videos(s, force=force)
        
        return {
            "ok": True,
            "force": force,
            **stats
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'enrichissement : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enrichissement : {str(e)}")


# -------------------------------------------------------------------
# [PROCESS] API : Gestion de la configuration
# -------------------------------------------------------------------
## ancien endpoint get_settings supprimé (voir api/settings.py)


## ancien endpoint update_settings supprimé (voir api/settings.py)


# -------------------------------------------------------------------
# [STATS] API : Catégories organisées
# -------------------------------------------------------------------
@app.get("/api/videos/all")
def get_all_videos(mode: SessionMode = Query("mixed")):
    """Retourne TOUTES les vidéos de la bibliothèque (pour la grille complète)."""
    with get_session() as s:
        items = s.query(Video).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        # Trier par titre
        sorted_videos = sorted(filtered, key=lambda v: v.title or "")
        
        return {
            "videos": [video_to_dict(v) for v in sorted_videos],
            "total": len(sorted_videos)
        }


@app.get("/api/categories")
def get_categories(
    mode: SessionMode = Query("mixed"),
    profile_id: int | None = Query(None)
):
    """Retourne les vidéos organisées par catégories pour l'écran principal."""
    
    with get_session() as s:
        items = s.query(Video).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        # Exclure les vidéos masquées pour ce profil
        if profile_id is not None:
            DB_PATH = Path(__file__).parent / "homeflix.db"
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
        
        # Carrousel : 10 films aléatoires
        carousel = random.sample(filtered, min(10, len(filtered)))
        
        # Déjà vus
        watched = [v for v in filtered if v.watched]
        
        # À reprendre - Maintenant par profil
        to_resume = []
        if profile_id is not None:
            # Récupérer les progressions de ce profil (10 plus récentes)
            progress_entries = s.query(WatchProgress).filter(
                WatchProgress.profile_id == profile_id
            ).order_by(WatchProgress.updated_at.desc()).limit(10).all()
            
            # Créer un dictionnaire vidéo_id -> (position, ordre)
            video_progress = {
                p.video_id: (p.position, idx) 
                for idx, p in enumerate(progress_entries)
            }
            
            # Récupérer les vidéos et les trier par ordre de visionnage récent
            videos_with_progress = []
            for v in filtered:
                if v.id in video_progress:
                    position, order = video_progress[v.id]
                    # Vérifier que ce n'est pas terminé (< 90%)
                    if not v.duration_seconds or position < (v.duration_seconds * 0.9):
                        # Ajouter la position actuelle à l'objet vidéo pour l'affichage
                        v.last_position = position
                        videos_with_progress.append((order, v))
            
            # Trier par ordre (0 = plus récent, 9 = plus ancien) et extraire les vidéos
            to_resume = [v for _, v in sorted(videos_with_progress, key=lambda x: x[0])]
        else:
            # Fallback: utiliser l'ancien système (last_position global)
            for v in filtered:
                if v.last_position and v.last_position > 0:
                    if not v.duration_seconds:
                        if not v.watched:
                            to_resume.append(v)
                    elif v.last_position < (v.duration_seconds * 0.9):
                        to_resume.append(v)
        
        # Par année (choisir 3 années aléatoires qui ont des films)
        by_year = defaultdict(list)
        for v in filtered:
            if v.year:
                by_year[v.year].append(v)
        
        available_years = [y for y, vids in by_year.items() if len(vids) >= 3]
        selected_years = random.sample(available_years, min(3, len(available_years))) if available_years else []
        
        year_categories = {year: [video_to_dict(v) for v in by_year[year]] for year in selected_years}
        
        # Par genre
        by_genre = defaultdict(list)
        for v in filtered:
            if v.genre:
                by_genre[v.genre].append(v)
        
        genre_categories = {genre: [video_to_dict(v) for v in vids] for genre, vids in by_genre.items() if len(vids) >= 3}
        
        return {
            "carousel": [video_to_dict(v) for v in carousel],
            "watched": [video_to_dict(v) for v in watched],
            "to_resume": [video_to_dict(v) for v in to_resume],
            "by_year": year_categories,
            "by_genre": genre_categories
        }


def _clean_collection_name(name):
    """
    Nettoie le nom de collection en supprimant emojis et mots indésirables.
    """
    
    # Supprimer les emojis
    cleaned = re.sub(r'[[VIDEO][MEDIA]🎞️📽️🎭🎪]', '', name)
    
    # Supprimer "Collection", "Saga", etc. (insensible à la casse)
    patterns = [
        r'\bCollection\b',
        r'\bSaga\b',
        r'\bTrilogie\b',
        r'\bIntégrale\b'
    ]
    
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Nettoyer les espaces multiples et trim
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


@app.get("/api/collections")
def get_collections(mode: SessionMode = Query("mixed"), min_items: int = Query(2)):
    """
    Retourne les vidéos regroupées par collection/saga.
    Utilise PRIORITAIREMENT les collections TMDb (fiables), 
    puis l'extraction de titre en fallback.
    
    Exemples:
        Avec TMDb: "Alien" + "Alien: Romulus" + "Alien 3" -> "Alien Collection" (depuis TMDb)
        Sans TMDb: "Bad Boys" + "Bad Boys II" -> "Bad Boys" (extraction)
    
    Args:
        mode: Mode de filtrage (mixed, films, series)
        min_items: Nombre minimum de vidéos pour qu'une collection soit affichée (défaut: 2)
    """
    
    with get_session() as s:
        items = s.query(Video).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        # Phase 1: Grouper par collection TMDb (prioritaire et fiable)
        by_tmdb_collection = {}
        videos_without_tmdb = []
        seen_paths = set()
        
        for v in filtered:
            # Éviter les doublons par chemin
            if v.path in seen_paths:
                continue
            seen_paths.add(v.path)
            
            # Si le film a une collection TMDb, l'utiliser (prioritaire)
            if v.collection and v.collection.strip():
                # Nettoyer le nom de collection (supprimer " Collection" en fin)
                clean_collection = v.collection.replace(" Collection", "").strip()
                # Normaliser la casse pour éviter les doublons (garder le premier nom rencontré)
                normalized_key = clean_collection.lower()
                if normalized_key not in by_tmdb_collection:
                    by_tmdb_collection[normalized_key] = {
                        "display_name": clean_collection,
                        "videos": []
                    }
                by_tmdb_collection[normalized_key]["videos"].append(v)
            else:
                videos_without_tmdb.append(v)
        
        # Phase 2: Pour les vidéos sans collection TMDb, essayer extraction de titre
        by_extracted_title = defaultdict(list)
        
        for v in videos_without_tmdb:
            base = extract_base_title(v.title or "")
            # IMPORTANT : N'ajouter que si le titre a VRAIMENT changé
            # Cela évite les faux positifs (ex: "7 jours pas plus" reste intact)
            if base and base != (v.title or "").strip() and len(base) >= 3:
                by_extracted_title[base].append(v)
        
        # Phase 3: Fusionner les deux sources et filtrer
        all_collections = {}
        standalone_videos = []
        videos_in_collections = set()  # Pour éviter les doublons
        
        # D'abord les collections TMDb (plus fiables)
        for normalized_key, collection_data in by_tmdb_collection.items():
            display_name = collection_data["display_name"]
            videos = collection_data["videos"]
            unique_videos = _deduplicate_videos(videos)
            
            if len(unique_videos) >= min_items:
                all_collections[display_name] = unique_videos
                # Marquer ces vidéos comme utilisées
                for v in unique_videos:
                    videos_in_collections.add(v.path)
            else:
                standalone_videos.extend(unique_videos)
                for v in unique_videos:
                    videos_in_collections.add(v.path)
        
        # Ensuite les collections extraites du titre (moins fiables)
        for base_title, videos in by_extracted_title.items():
            unique_videos = _deduplicate_videos(videos)
            
            if len(unique_videos) >= min_items:
                # Préfixe pour distinguer des collections TMDb
                all_collections[base_title] = unique_videos
                for v in unique_videos:
                    videos_in_collections.add(v.path)
            else:
                # Ne pas ajouter si déjà dans standalone via TMDb
                for v in unique_videos:
                    if v.path not in videos_in_collections:
                        standalone_videos.append(v)
                        videos_in_collections.add(v.path)
        
        # Ajouter les vidéos sans saga détectée
        for v in videos_without_tmdb:
            if v.path not in videos_in_collections:
                standalone_videos.append(v)
        
        # Construire la réponse
        collections_data = {}
        for collection_name, videos in all_collections.items():
            # Nettoyer le nom (supprimer emojis et mots comme "Saga", "Collection")
            clean_name = _clean_collection_name(collection_name)
            
            # Dédoublonner les vidéos
            unique_videos = _deduplicate_videos(videos)
            
            sorted_videos = sorted(
                unique_videos,
                key=lambda x: (
                    x.episode_number is None,
                    x.episode_number or 0,
                    x.year or 9999,
                    x.title or ""
                )
            )
            
            collections_data[clean_name] = {
                "name": clean_name,
                "videos": [video_to_dict(v) for v in sorted_videos],
                "total": len(sorted_videos)
            }
        
        # Trier les collections par nom
        sorted_collections = dict(sorted(collections_data.items()))
        
        return {
            "collections": sorted_collections,
            "standalone": [video_to_dict(v) for v in sorted(standalone_videos, key=lambda x: x.title or "")],
            "total_collections": len(sorted_collections),
            "total_standalone": len(standalone_videos)
        }


def _deduplicate_videos(videos):
    """Supprime les doublons d'une liste de vidéos."""
    unique_videos = []
    seen_signatures = set()
    
    for v in videos:
        signature = (v.title, v.year, v.path)
        if signature not in seen_signatures:
            unique_videos.append(v)
            seen_signatures.add(signature)
    
    return unique_videos


# -------------------------------------------------------------------
# [SCAN] API : Recherche avancée
# -------------------------------------------------------------------
@app.get("/api/search")
def search_videos(
    q: str = Query(..., min_length=1),
    mode: SessionMode = Query("mixed"),
    year: int = Query(None),
    genre: str = Query(None),
    watched: bool = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """Recherche avancée de vidéos avec filtres multiples.
    
    Args:
        q: Terme de recherche (titre)
        mode: Mode de filtrage (mixed, films, series)
        year: Filtrer par année spécifique
        genre: Filtrer par genre spécifique
        watched: Filtrer par statut vu/non vu
        limit: Nombre maximum de résultats
    """
    with get_session() as s:
        query = s.query(Video)
        
        # Recherche dans le titre (insensible à la casse)
        query = query.filter(Video.title.ilike(f"%{q}%"))
        
        # Filtres optionnels
        if year:
            query = query.filter(Video.year == year)
        if genre:
            query = query.filter(Video.genre.ilike(f"%{genre}%"))
        if watched is not None:
            query = query.filter(Video.watched == watched)
        
        # Récupération et filtrage par mode
        items = query.order_by(Video.title.asc()).limit(limit).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        return {
            "query": q,
            "total": len(filtered),
            "results": [video_to_dict(v) for v in filtered]
        }


# -------------------------------------------------------------------
# �[SYNC] API : Mettre à jour le statut d'une vidéo
# -------------------------------------------------------------------
## ancien endpoint update_video supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# [HTTP] Interface utilisateur Homeflix (client React)
# -------------------------------------------------------------------
@app.get("/favicon.ico")
def serve_favicon():
    """Sert le favicon"""
    favicon_path = CLIENT_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    raise HTTPException(status_code=404, detail="Favicon non trouve")

@app.get("/vite.svg")
def serve_vite_svg():
    """Sert vite.svg si nécessaire"""
    svg_path = CLIENT_DIR / "vite.svg"
    if svg_path.exists():
        return FileResponse(svg_path)
    raise HTTPException(status_code=404, detail="vite.svg non trouve")

@app.get("/", response_class=HTMLResponse)
@app.get("/{full_path:path}", response_class=HTMLResponse)
def serve_frontend(full_path: str = ""):
    """Sert le client React (index.html) pour toutes les routes non-API"""
    # Ne pas intercepter les routes API, assets et avatars
    if full_path.startswith("api/") or full_path.startswith("assets/") or full_path.startswith("avatars/"):
        raise HTTPException(status_code=404, detail="Route non trouvee")
    
    index_path = CLIENT_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate"
        })
    else:
        return HTMLResponse(
            content=f"<h1>Erreur</h1><p>Client non trouve: {CLIENT_DIR}</p>",
            status_code=500
        )


# -------------------------------------------------------------------
# [PROCESS] Lancement local
# -------------------------------------------------------------------
if __name__ == "__main__":
    
    # Vérifier si les certificats SSL existent
    cert_dir = Path(__file__).parent.parent / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Récupérer le port depuis la variable d'environnement (défaut: 8000 pour DEV, 8001 pour STABLE)
    server_port = int(os.environ.get("SERVER_PORT", 8000))
    
    if cert_file.exists() and key_file.exists():
        # Mode HTTPS avec certificat SSL
        logger.info("🔒 Demarrage du serveur en mode HTTPS (port 8443)")
        logger.info(f"   📜 Certificat : {cert_file}")
        logger.info(f"   🔑 Cle privee : {key_file}")
        logger.info("   [WARN]  Certificat auto-signe - avertissement de securite normal sur navigateur")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8443,
            ssl_keyfile=str(key_file),
            ssl_certfile=str(cert_file),
            reload=False
        )
    else:
        # Mode HTTP standard
        logger.info(f"[HTTP] Demarrage du serveur en mode HTTP (port {server_port})")
        if server_port == 8000:
            logger.info("   [INFO] Pour activer HTTPS, executez : .\\setup-https.ps1")
        # 0.0.0.0 permet l'accès depuis le réseau local (téléphone, tablette, etc.)
        uvicorn.run("main:app", host="0.0.0.0", port=server_port, reload=False)