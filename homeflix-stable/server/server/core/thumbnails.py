from pathlib import Path
from fastapi.responses import FileResponse
from core.logger import logger, log_exception
from PIL import Image
import subprocess
import threading
import shutil
import re
import requests

from .config_manager import load_settings
from .title_utils import clean_title_and_year

# Dossier où seront stockées les miniatures locales
import subprocess
import hashlib
from pathlib import Path
import requests
from typing import Optional
from .subprocess_helper import run_hidden

# Constantes
THUMB_DIR = Path(__file__).resolve().parents[2] / "data" / "thumbs"
THUMB_DIR.mkdir(exist_ok=True)

# Image par défaut (fallback)
DEFAULT_POSTER = Path(__file__).resolve().parents[1] / "static" / "default_poster.jpg"


def thumb_path_for(video_path: Path) -> Path:
    """
    Calcule le chemin de miniature pour une vidéo donnée.
    Cherche en priorité .webp (plus léger), puis .jpg
    Retourne toujours .webp pour les nouvelles générations
    """
    base_name = f"{video_path.name}"
    
    # Chercher WebP en priorité
    webp_path = THUMB_DIR / f"{base_name}.webp"
    if webp_path.exists():
        return webp_path
    
    # Chercher JPG si WebP n'existe pas
    jpg_path = THUMB_DIR / f"{base_name}.jpg"
    if jpg_path.exists():
        return jpg_path
    
    # Pour les nouvelles miniatures, utiliser WebP par défaut
    return webp_path


def _ffmpeg_path() -> str | None:
    """Retourne le chemin de ffmpeg s'il est disponible dans le PATH."""
    return shutil.which("ffmpeg")


def _generate_thumbnail_sync(video_path: Path, thumb_path: Path) -> bool:
    """
    Génère une miniature WebP à partir d'une vidéo en utilisant ffmpeg.
    
    - Essaye plusieurs positions (1s, 10s, 30s) pour éviter les écrans noirs
    - Génère d'abord un JPG temporaire, puis le convertit en WebP
    - Supprime le JPG temporaire après conversion
    """
    from PIL import Image
    
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        return False
    
    # Générer un JPG temporaire d'abord
    temp_jpg = thumb_path.with_suffix('.jpg.tmp')
    
    # Essaye plusieurs positions temporelles pour éviter les écrans noirs/intros
    seek_times = ["10", "30", "1", "60"]
    
    for seek_time in seek_times:
        try:
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                ffmpeg,
                "-y",              # overwrite sortie
                "-ss", seek_time,  # seek à différentes positions
                "-i", str(video_path),
                "-frames:v", "1",
                "-vf", "scale=500:-1",  # redimensionne pour optimiser
                "-q:v", "2",
                str(temp_jpg),
            ]
            result = run_hidden(
                cmd, 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=10  # timeout de sécurité
            )
            
            # Si le JPG temporaire a été créé avec succès, le convertir en WebP
            if temp_jpg.exists() and temp_jpg.stat().st_size > 1024:  # au moins 1KB
                try:
                    # Convertir JPG → WebP avec PIL
                    img = Image.open(temp_jpg)
                    img.save(thumb_path, 'WEBP', quality=85, method=6)
                    
                    # Supprimer le JPG temporaire
                    temp_jpg.unlink()
                    
                    # Vérifier que le WebP a été créé
                    if thumb_path.exists() and thumb_path.stat().st_size > 1024:
                        return True
                except Exception as e:
                    logger.warning(f"Erreur conversion WebP pour {video_path.name}: {e}")
                    # En cas d'erreur, garder le JPG
                    if temp_jpg.exists():
                        temp_jpg.rename(thumb_path.with_suffix('.jpg'))
                    return False
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
        except Exception:
            continue
    
    return False


def ensure_thumbnail_sync(path: str, force: bool = False) -> bool:
    """Assure la présence d'une miniature pour `path`.

    Retourne True si la miniature existe (ou a été créée), False sinon.
    """
    video_path = Path(path)
    thumb_path = thumb_path_for(video_path)
    if thumb_path.exists() and not force:
        return True

    settings = load_settings()
    tmdb_key = getattr(settings, "tmdb_api_key", None)

    # Stratégie 1: Tenter TMDb d'abord (plus fiable pour les métadonnées)
    if tmdb_key:
        logger.info(f"Recherche TMDb pour: {video_path.name}")
        if _generate_thumbnail_from_tmdb(video_path, thumb_path, tmdb_key):
            logger.info(f"Miniature TMDb récupérée: {video_path.name}")
            return True
        logger.warning(f"Aucun résultat TMDb pour: {video_path.name}")

    # Stratégie 2: Fallback ffmpeg si TMDb échoue
    if _ffmpeg_path():
        logger.info(f"Génération ffmpeg pour: {video_path.name}")
        if _generate_thumbnail_sync(video_path, thumb_path):
            logger.info(f"Miniature ffmpeg générée: {video_path.name}")
            return True
        logger.error(f"Échec ffmpeg pour: {video_path.name}")

    return False


def _ensure_thumbnail_async(video_path: Path, thumb_path: Path) -> None:
    """Lance la génération de miniature en arrière-plan si manquante."""
    if thumb_path.exists():
        return

    def _worker():
        try:
            _generate_thumbnail_sync(video_path, thumb_path)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def get_thumbnail(path: str):
    """Retourne la miniature pour une vidéo.

    - Si la miniature existe déjà (WebP ou JPG), on la renvoie
    - Sinon, on tente de la générer en arrière-plan (si ffmpeg est dispo)
      et on renvoie l'image par défaut pour cette requête.
    """
    try:
        video_path = Path(path)
        thumb_path = thumb_path_for(video_path)

        if thumb_path.exists():
            # Déterminer le type MIME
            media_type = "image/webp" if thumb_path.suffix.lower() == ".webp" else "image/jpeg"
            return FileResponse(
                thumb_path,
                media_type=media_type,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )

        # Tente une génération synchrone (ffmpeg ou TMDb) 
        if ensure_thumbnail_sync(str(video_path), force=False) and thumb_path.exists():
            media_type = "image/webp" if thumb_path.suffix.lower() == ".webp" else "image/jpeg"
            return FileResponse(
                thumb_path,
                media_type=media_type,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
    except Exception:
        pass

    return FileResponse(DEFAULT_POSTER)


# --------------------
# Helpers TMDb
# --------------------


def _generate_thumbnail_from_tmdb(video_path: Path, thumb_path: Path, api_key: str) -> bool:
    """Tente de récupérer un poster depuis TMDb avec plusieurs stratégies."""
    try:
        name = video_path.stem
        title, year = clean_title_and_year(name)
        if not title or len(title) < 2:
            return False

        # Stratégie 1: recherche avec titre nettoyé
        params = {"api_key": api_key, "query": title}
        if year:
            params["year"] = year
            
        url = "https://api.themoviedb.org/3/search/multi"
        r = requests.get(url, params=params, timeout=8)
        
        if r.status_code != 200:
            return False
            
        data = r.json()
        results = data.get("results") or []
        
        # Stratégie 2: si aucun résultat et qu'on a une année, réessaye sans l'année
        if not results and year:
            params.pop("year", None)
            r = requests.get(url, params=params, timeout=8)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results") or []
        
        if not results:
            return False

        # Choisir le meilleur résultat (priorité movie/tv, filtre année si disponible)
        def score(item):
            s = 0
            media_type = item.get("media_type", "")
            
            # Priorité aux films et séries
            if media_type == "movie":
                s += 3
            elif media_type == "tv":
                s += 2
                
            # Popularité
            popularity = item.get("popularity", 0)
            s += min(popularity / 10, 2)  # max +2 points
            
            # boost si année correspond
            item_year = None
            date = item.get("release_date") or item.get("first_air_date")
            if date and len(date) >= 4:
                try:
                    item_year = int(date[:4])
                except Exception:
                    item_year = None
            if year and item_year == year:
                s += 5  # boost important si l'année correspond
            elif year and item_year and abs(item_year - year) <= 1:
                s += 2  # boost moyen si année proche (±1 an)
                
            return s

        best = max(results, key=score)
        poster_path = best.get("poster_path")
        
        # Si pas de poster, essaye le backdrop
        if not poster_path:
            poster_path = best.get("backdrop_path")
            
        if not poster_path:
            return False

        # Télécharge l'image
        img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        ir = requests.get(img_url, timeout=10)
        if ir.status_code != 200:
            return False

        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(thumb_path, "wb") as f:
            f.write(ir.content)
        
        # Vérifie que l'image est valide (taille minimale)
        return thumb_path.exists() and thumb_path.stat().st_size > 1024
        
    except Exception as e:
        # Log silencieux en production, mais utile pour debug
        # logger.error(f"TMDb error for {video_path.name}: {e}")
        return False
