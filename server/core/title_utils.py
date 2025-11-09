"""
Utilitaires pour nettoyer les noms de fichiers vidéo et extraire titre + année.
Unifiés pour être partagés entre les modules (thumbnails, metadata).
"""

import re
from typing import Optional, Tuple

_RES_TAGS = re.compile(
    r"(?:\b(?:480|720|1080|2160|4k)p?\b|"
    r"\b(?:x264|x265|hevc|h264|h265|avc)\b|"
    r"\b(?:WEBrip|WEB-DL|BluRay|BRRip|HDRip|DVDRip|HDTV|PDTV)\b|"
    r"\b(?:AAC|AC3|DTS|DD5\.1|DD51)\b|"
    r"\b(?:\d+CD)\b|"
    r"\[.*?\]|\(.*?\))",
    re.I,
)
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\b")
_LANGUAGE_TAGS = re.compile(
    r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|MULTI|ENGLISH)\b", re.I
)
_EPISODE = re.compile(r"\b(?:S\d{1,2}E\d{1,2}|[Ss]aison\s*\d+|[Ee]pisode\s*\d+)\b", re.I)


def clean_title_and_year(stem: str) -> Tuple[str, Optional[int]]:
    """
    Nettoie un nom de fichier (sans extension) pour extraire un titre et une année probable.
    Retourne (titre, année_ou_None).
    """
    title = re.sub(r"[._-]+", " ", stem)
    title = _EPISODE.sub(" ", title)
    title = _RES_TAGS.sub(" ", title)
    title = _LANGUAGE_TAGS.sub(" ", title)

    year = None
    all_years = list(_YEAR.finditer(title))
    if len(all_years) >= 1:
        # privilégie la dernière année trouvée comme année de sortie probable
        try:
            year = int(all_years[-1].group(1))
        except Exception:
            year = None
        title = _YEAR.sub(" ", title)

    words = [w for w in title.split() if len(w) > 1 or w.isdigit()]
    title = " ".join(words).strip()
    return title, year
