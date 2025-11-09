from pathlib import Path
from fastapi.responses import FileResponse
import subprocess
import threading
import shutil
import re
import requests

from .config_manager import load_settings
from .title_utils import clean_title_and_year

# Dossier où seront stockées les miniatures locales
THUMB_DIR = Path.home() / ".homeone_thumbs"
THUMB_DIR.mkdir(exist_ok=True)

# Image par défaut (fallback)
DEFAULT_POSTER = Path(__file__).resolve().parents[1] / "static" / "default_poster.jpg"


def thumb_path_for(video_path: Path) -> Path:
    """Calcule le chemin de miniature pour une vidéo donnée."""
    return THUMB_DIR / f"{video_path.name}.jpg"


def _ffmpeg_path() -> str | None:
    """Retourne le chemin de ffmpeg s'il est disponible dans le PATH."""
    return shutil.which("ffmpeg")


def _generate_thumbnail_sync(video_path: Path, thumb_path: Path) -> bool:
    """Génère une miniature JPEG à partir d'une vidéo en utilisant ffmpeg.

    - Essaye plusieurs positions (1s, 10s, 30s) pour éviter les écrans noirs
    - Écrit un JPEG optimisé (qualité q=2)
    """
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        return False
    
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
                str(thumb_path),
            ]
            result = subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=10  # timeout de sécurité
            )
            if thumb_path.exists() and thumb_path.stat().st_size > 1024:  # au moins 1KB
                return True
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
        print(f"🔍 Recherche TMDb pour: {video_path.name}")
        if _generate_thumbnail_from_tmdb(video_path, thumb_path, tmdb_key):
            print(f"✅ Miniature TMDb récupérée: {video_path.name}")
            return True
        print(f"⚠️ Aucun résultat TMDb pour: {video_path.name}")

    # Stratégie 2: Fallback ffmpeg si TMDb échoue
    if _ffmpeg_path():
        print(f"🎬 Génération ffmpeg pour: {video_path.name}")
        if _generate_thumbnail_sync(video_path, thumb_path):
            print(f"✅ Miniature ffmpeg générée: {video_path.name}")
            return True
        print(f"❌ Échec ffmpeg pour: {video_path.name}")

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

    - Si la miniature existe déjà, on la renvoie
    - Sinon, on tente de la générer en arrière-plan (si ffmpeg est dispo)
      et on renvoie l'image par défaut pour cette requête.
    """
    try:
        video_path = Path(path)
        thumb_path = thumb_path_for(video_path)

        if thumb_path.exists():
            return FileResponse(thumb_path)

        # Tente une génération synchrone (ffmpeg ou TMDb) 
        if ensure_thumbnail_sync(str(video_path), force=False) and thumb_path.exists():
            return FileResponse(thumb_path)
    except Exception:
        pass

    return FileResponse(DEFAULT_POSTER)


# --------------------
# Helpers TMDb
# --------------------

_RES_TAGS = re.compile(r"(?:\b(?:480|720|1080|2160|4k)p?\b|\b(?:x264|x265|hevc|h264|h265|avc)\b|\b(?:WEBrip|WEB-DL|BluRay|BRRip|HDRip|DVDRip|HDTV|PDTV)\b|\b(?:AAC|AC3|DTS|DD5\.1|DD51)\b|\[.*?\]|\(.*?\))", re.I)
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\b")
_LANGUAGE_TAGS = re.compile(r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|MULTI|ENGLISH)\b", re.I)
_EPISODE = re.compile(r"\b(?:S\d{1,2}E\d{1,2}|[Ss]aison\s*\d+|[Ee]pisode\s*\d+)\b", re.I)


def _clean_title_from_filename(stem: str) -> tuple[str, int | None]:
    """Délègue vers l'utilitaire partagé pour cohérence."""
    title, year = clean_title_and_year(stem)
    return title, year


def _generate_thumbnail_from_tmdb(video_path: Path, thumb_path: Path, api_key: str) -> bool:
    """Tente de récupérer un poster depuis TMDb avec plusieurs stratégies."""
    try:
        name = video_path.stem
        title, year = _clean_title_from_filename(name)
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
        # print(f"TMDb error for {video_path.name}: {e}")
        return False
