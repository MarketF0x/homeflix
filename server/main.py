from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from typing import Literal, List
import threading
import time
import random

from core.db import init_db, get_session
from core.models import Video
from core.scanner import scan_all
from core.config_manager import load_settings
from core.player import open_with_default
from core.thumbnails import get_thumbnail, ensure_thumbnail_sync, thumb_path_for
from core.file_cleaner import clean_database_filenames
from core.metadata_enricher import enrich_all_videos
from api.videos import router as videos_router
from api.thumbnails import router as thumbnails_router
from api.settings import router as settings_router


# -------------------------------------------------------------------
# 🚀 Initialisation de l'application
# -------------------------------------------------------------------
app = FastAPI(title="HomeOne Lite", version="2.4")

# Création / vérification de la base SQLite
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs modularisés
app.include_router(videos_router)
app.include_router(thumbnails_router)
app.include_router(settings_router)


# -------------------------------------------------------------------
# ⏰ Scan automatique toutes les 10 minutes
# -------------------------------------------------------------------
def auto_scan_worker():
    """Thread en arrière-plan qui scanne et nettoie automatiquement toutes les 10 minutes."""
    while True:
        try:
            time.sleep(600)  # 10 minutes = 600 secondes
            print("🔄 Scan automatique en cours...")
            settings = load_settings()
            
            # 1. Nettoyer les noms de fichiers pour améliorer la reconnaissance TMDB (si activé)
            auto_clean_enabled = getattr(settings, 'auto_clean_filenames', True)
            if auto_clean_enabled:
                print("🧹 Nettoyage des noms de fichiers...")
                try:
                    clean_stats = clean_database_filenames(dry_run=False, update_titles=True)
                    if clean_stats['renamed'] > 0:
                        print(f"✅ Nettoyage : {clean_stats['renamed']} fichiers renommés")
                    else:
                        print("ℹ️ Aucun fichier à nettoyer")
                except Exception as e:
                    print(f"⚠️ Erreur lors du nettoyage : {e}")
            
            # 2. Scanner les dossiers vidéos
            stats = scan_all(settings)
            print(f"✅ Scan auto terminé : {stats['indexed']} ajoutés, {stats['removed']} supprimés, {stats['total']} total")
        except Exception as e:
            print(f"❌ Erreur lors du scan automatique : {e}")


# Lancement du thread de scan automatique au démarrage
@app.on_event("startup")
def start_auto_scan():
    """Démarre le scan automatique en arrière-plan.

    Nouvel ordre des opérations au démarrage (demande utilisateur):
      1. Nettoyage des noms de fichiers (si activé)
      2. Validation de la clé API TMDb
      3. Détection de FFmpeg
      4. Lancement du thread de scan périodique
    """
    import shutil, requests

    settings = load_settings()

    # 1. Nettoyage initial (prioritaire)
    auto_clean_enabled = getattr(settings, 'auto_clean_filenames', True)
    if auto_clean_enabled:
        print("🧹 Nettoyage initial des noms de fichiers...")
        try:
            clean_stats = clean_database_filenames(dry_run=False, update_titles=True)
            print(f"✅ Nettoyage initial: {clean_stats['renamed']} fichiers renommés / {clean_stats['total']} total")
        except Exception as e:
            print(f"⚠️ Erreur nettoyage initial: {e}")
    else:
        print("ℹ️ Nettoyage automatique désactivé — étape 1 ignorée")

    # 2. Validation TMDb
    if settings.tmdb_api_key:
        print("🔑 Validation de la clé TMDb...")
        try:
            test_url = f"https://api.themoviedb.org/3/configuration?api_key={settings.tmdb_api_key}"
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print("✅ Clé API TMDb validée")
            else:
                print(f"⚠️ Clé API TMDb invalide (code {response.status_code})")
        except Exception as e:
            print(f"⚠️ Impossible de valider la clé TMDb: {e}")
    else:
        print("⚠️ Aucune clé API TMDb configurée — étape 2 limitée")

    # 3. Détection FFmpeg
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    if ffmpeg_installed:
        print("🎬 FFmpeg détecté — génération locale de miniatures activée")
    else:
        print("⚠️ FFmpeg non détecté — fallback TMDb uniquement (installer: python check_and_install_ffmpeg.py)")

    # 4. Thread périodique
    threading.Thread(target=auto_scan_worker, daemon=True).start()
    print("✨ Scan automatique activé (toutes les 10 minutes)")


SessionMode = Literal["mixed", "films", "series"]


# -------------------------------------------------------------------
# 🔍 Filtrage selon le mode
# -------------------------------------------------------------------
def _filter_by_mode(videos: List[Video], mode: SessionMode, min_film=75, max_series=55):
    if mode == "films":
        return [v for v in videos if (v.duration_seconds or 0) >= (min_film * 60)]
    if mode == "series":
        return [v for v in videos if 20 * 60 <= (v.duration_seconds or 0) <= (max_series * 60)]
    return videos


# -------------------------------------------------------------------
# 📁 API : Liste des vidéos
# -------------------------------------------------------------------
## ancien endpoint list_videos supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# 🔄 API : Scan complet
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
                print("🔍 Enrichissement des métadonnées TMDb...")
                enrich_all_videos(s, force=False)
                
                # 2. Générer les miniatures
                videos = s.query(Video).all()
                for v in videos:
                    try:
                        ensure_thumbnail_sync(v.path, force=False)
                    except Exception:
                        pass
        except Exception as e:
            print(f"❌ Erreur background worker: {e}")

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
    
    print(f"🧹 Nettoyage des noms de fichiers {'(simulation)' if dry_run else '(réel)'}...")
    
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
        print(f"❌ Erreur lors du nettoyage : {e}")
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
# 🖼️ API : Miniature
# -------------------------------------------------------------------
## ancien endpoint thumbnail supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# 🎬 API : Stream vidéo
# -------------------------------------------------------------------
@app.get("/api/stream")
def stream_video(path: str, range: str = Query(None, alias="Range")):
    """
    Streaming vidéo avec support du Range (permet le seek).
    """
    video_path = Path(path)
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Fichier vidéo introuvable")
    
    file_size = video_path.stat().st_size
    
    # Support du Range header pour le seek
    if range:
        # Parse le range header (format: "bytes=start-end")
        range_match = range.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
    else:
        start = 0
        end = file_size - 1
    
    chunk_size = end - start + 1
    
    # Générateur de chunks
    def iter_file():
        with open(video_path, 'rb') as video_file:
            video_file.seek(start)
            remaining = chunk_size
            while remaining > 0:
                read_size = min(8192, remaining)
                data = video_file.read(read_size)
                if not data:
                    break
                remaining -= len(data)
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
    
    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(chunk_size),
        'Content-Type': media_type,
    }
    
    return StreamingResponse(
        iter_file(),
        status_code=206 if range else 200,
        headers=headers,
        media_type=media_type
    )


# -------------------------------------------------------------------
# 💾 API : Sauvegarder la progression
# -------------------------------------------------------------------
## ancien endpoint save_progress supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# 🖼️ API : Générer toutes les miniatures
# -------------------------------------------------------------------
## ancien endpoint generate_thumbnails supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# 🔄 API : Régénérer les miniatures manquantes
# -------------------------------------------------------------------
## ancien endpoint repair_thumbnails supprimé (voir api/thumbnails.py)


# -------------------------------------------------------------------
# 🎯 API : Enrichir les métadonnées TMDb
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
    
    print(f"🔍 Enrichissement des métadonnées TMDb {'(forcé)' if force else ''}...")
    
    try:
        with get_session() as s:
            stats = enrich_all_videos(s, force=force)
        
        return {
            "ok": True,
            "force": force,
            **stats
        }
    except Exception as e:
        print(f"❌ Erreur lors de l'enrichissement : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enrichissement : {str(e)}")


# -------------------------------------------------------------------
# ⚙️ API : Gestion de la configuration
# -------------------------------------------------------------------
## ancien endpoint get_settings supprimé (voir api/settings.py)


## ancien endpoint update_settings supprimé (voir api/settings.py)


# -------------------------------------------------------------------
# 📊 API : Catégories organisées
# -------------------------------------------------------------------
@app.get("/api/videos/all")
def get_all_videos(mode: SessionMode = Query("mixed")):
    """Retourne TOUTES les vidéos de la bibliothèque (pour la grille complète)."""
    with get_session() as s:
        items = s.query(Video).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        def video_dict(v):
            return {
                "id": v.id,
                "title": v.title,
                "path": v.path,
                "duration_seconds": v.duration_seconds,
                "size": v.size,
                "year": v.year,
                "genre": v.genre,
                "watched": v.watched,
                "last_position": v.last_position
            }
        
        # Trier par titre
        sorted_videos = sorted(filtered, key=lambda v: v.title or "")
        
        return {
            "videos": [video_dict(v) for v in sorted_videos],
            "total": len(sorted_videos)
        }


@app.get("/api/categories")
def get_categories(mode: SessionMode = Query("mixed")):
    """Retourne les vidéos organisées par catégories pour l'écran principal."""
    import random
    from collections import defaultdict
    
    with get_session() as s:
        items = s.query(Video).all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        
        def video_dict(v):
            return {
                "id": v.id,
                "title": v.title,
                "path": v.path,
                "duration_seconds": v.duration_seconds,
                "size": v.size,
                "year": v.year,
                "genre": v.genre,
                "watched": v.watched,
                "last_position": v.last_position
            }
        
        # Carrousel : 10 films aléatoires
        carousel = random.sample(filtered, min(10, len(filtered)))
        
        # Déjà vus
        watched = [v for v in filtered if v.watched]
        
        # À reprendre (ceux avec last_position > 0 ET pas encore marqués comme vus)
        # On considère qu'une vidéo est "à reprendre" si :
        # - Elle a une position de lecture > 0
        # - Elle n'est pas encore marquée comme "vue" (watched = False)
        # - Ou si la position est < 90% de la durée totale
        to_resume = []
        for v in filtered:
            if v.last_position and v.last_position > 0:
                # Si pas de durée connue, on l'ajoute si pas marquée comme vue
                if not v.duration_seconds:
                    if not v.watched:
                        to_resume.append(v)
                # Si on a la durée, vérifier qu'on est pas à plus de 90%
                elif v.last_position < (v.duration_seconds * 0.9):
                    to_resume.append(v)
        
        # Trier par date de dernière lecture (les plus récentes en premier)
        # Pour l'instant on n'a pas ce champ, donc on garde l'ordre actuel
        
        # Par année (choisir 3 années aléatoires qui ont des films)
        by_year = defaultdict(list)
        for v in filtered:
            if v.year:
                by_year[v.year].append(v)
        
        available_years = [y for y, vids in by_year.items() if len(vids) >= 3]
        selected_years = random.sample(available_years, min(3, len(available_years))) if available_years else []
        
        year_categories = {year: [video_dict(v) for v in by_year[year]] for year in selected_years}
        
        # Par genre
        by_genre = defaultdict(list)
        for v in filtered:
            if v.genre:
                by_genre[v.genre].append(v)
        
        genre_categories = {genre: [video_dict(v) for v in vids] for genre, vids in by_genre.items() if len(vids) >= 3}
        
        return {
            "carousel": [video_dict(v) for v in carousel],
            "watched": [video_dict(v) for v in watched],
            "to_resume": [video_dict(v) for v in to_resume],
            "by_year": year_categories,
            "by_genre": genre_categories
        }


# -------------------------------------------------------------------
# � API : Recherche avancée
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
            "results": [{
                "id": v.id,
                "title": v.title,
                "path": v.path,
                "duration_seconds": v.duration_seconds,
                "size": v.size,
                "year": v.year,
                "genre": v.genre,
                "watched": v.watched,
                "last_position": v.last_position
            } for v in filtered]
        }


# -------------------------------------------------------------------
# �🔄 API : Mettre à jour le statut d'une vidéo
# -------------------------------------------------------------------
## ancien endpoint update_video supprimé (voir api/videos.py)


# -------------------------------------------------------------------
# 🌐 Interface utilisateur HomeOne Lite
# -------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>HomeOne Lite</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background-color: #181a1b;
                color: #f1f1f1;
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #00bcd4;
                margin-bottom: 10px;
            }
            .toolbar {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
                gap: 10px;
            }
            select, button.scan {
                background-color: #2c2f33;
                color: #fff;
                border: none;
                padding: 10px 14px;
                border-radius: 6px;
                font-size: 15px;
                cursor: pointer;
            }
            button.scan:hover {
                background-color: #0097a7;
            }
            .video-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 14px;
            }
            .video-card {
                background-color: #2c2f33;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: transform 0.2s;
            }
            .video-card:hover {
                transform: scale(1.03);
            }
            .video-title {
                font-weight: bold;
                flex: 1;
                margin-right: 10px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            button.open {
                background-color: #00bcd4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button.open:hover {
                background-color: #0097a7;
            }
            .status {
                text-align: center;
                margin-top: 10px;
                font-size: 14px;
                color: #aaa;
            }
        </style>
    </head>
    <body>
        <h1>🎬 HomeOne Lite</h1>

        <div class="toolbar">
            <select id="mode" onchange="loadVideos()">
                <option value="mixed">Mixte</option>
                <option value="films">Films</option>
                <option value="series">Séries</option>
            </select>
            <button class="scan" onclick="scan()">🔄 Rescanner</button>
        </div>

        <div id="videos" class="video-list"></div>
        <div class="status" id="status"></div>

        <script>
            async function loadVideos() {
                const res = await fetch('/api/videos');
                const data = await res.json();
                const items = Array.isArray(data) ? data : (data.videos || []);
                const list = document.getElementById('videos');
                const status = document.getElementById('status');

                list.innerHTML = "";
                if (!items || items.length === 0) {
                    list.innerHTML = "<p>Aucune vidéo trouvée.</p>";
                    status.textContent = "";
                    return;
                }

                items.forEach(v => {
                    // Nettoie le chemin pour éviter les erreurs d'échappement
                    const safePath = v.path.replace(/\\/g, "/").replace(/'/g, "\\'");
                    const card = document.createElement('div');
                    card.className = 'video-card';
                    card.innerHTML = `
                        <div class="video-title">${v.title}</div>
                        <button class="open" onclick="openVideo('${safePath}')">Ouvrir</button>
                    `;
                    list.appendChild(card);
                });

                status.textContent = `${items.length} vidéos trouvées`;
            }

            async function openVideo(path) {
                try {
                    const res = await fetch('/api/open', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ path: path })
                    });
                    if (!res.ok) {
                        const err = await res.json();
                        alert("Erreur : " + err.detail);
                    } else {
                        console.log("Ouverture réussie :", path);
                    }
                } catch (e) {
                    alert("Impossible d'ouvrir la vidéo. Détails : " + e);
                }
            }

            async function scan() {
                document.getElementById('status').textContent = "Scan en cours...";
                const res = await fetch('/api/scan', {method: 'POST'});
                const data = await res.json();
                if (data.ok) {
                    document.getElementById('status').textContent = `${data.indexed} fichiers indexés ✅`;
                    loadVideos();
                } else {
                    document.getElementById('status').textContent = "Erreur pendant le scan ❌";
                }
            }

            loadVideos();
        </script>
    </body>
    </html>
    """


# -------------------------------------------------------------------
# ⚙️ Lancement local
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
