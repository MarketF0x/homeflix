"""
Utilitaires pour nettoyer les noms de fichiers vidéo et extraire titre + année.
Unifiés pour être partagés entre les modules (thumbnails, metadata).
"""

import re
from typing import Optional, Tuple, Dict

_RES_TAGS = re.compile(
    r"(?:\b(?:480|720|1080|2160|4k|8k)p?\b|"
    r"\b(?:x264|x265|hevc|h264|h265|avc|xvid|divx)\b|"
    r"\b(?:WEBrip|WEB-DL|BluRay|BRRip|HDRip|DVDRip|HDTV|PDTV|BDRip|HDLIGHT|STREAMING)\b|"
    r"\b(?:AAC|AC3|DTS|DD5\.1|DD51|FLAC|MP3|TrueHD|ATMOS)\b|"
    r"\b(?:\d+CD)\b|"
    r"\[.*?\]|\(.*?\))",
    re.I,
)
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\b")
_LANGUAGE_TAGS = re.compile(
    r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|MULTI|ENGLISH)\b", re.I
)
_EPISODE = re.compile(r"\b(?:S\d{1,2}E\d{1,2}|[Ss]aison\s*\d+|[Ee]pisode\s*\d+)\b", re.I)

# Patterns pour détecter les collections/sagas
_COLLECTION_PATTERNS = [
    # Numéros romains (I, II, III, IV, V...)
    re.compile(r"^(.+?)\s+([IVX]+)$", re.I),
    # Tiret + numéro (ex: "Matrix - 1", "Avengers - 2")
    re.compile(r"^(.+?)\s*[-:]\s*(\d+)$"),
    # Numéro en fin (ex: "Matrix 1", "Harry Potter 2")
    re.compile(r"^(.+?)\s+(\d+)$"),
    # Chapitre / Partie (ex: "John Wick Chapitre 3")
    re.compile(r"^(.+?)\s+(?:Chapitre|Partie|Chapter|Part)\s*(\d+)$", re.I),
    # Épisode pour séries (ex: "Breaking Bad S01E01")
    re.compile(r"^(.+?)\s+S(\d{1,2})E\d{1,2}", re.I),
]

# Conversion numéros romains
_ROMAN_TO_INT = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15
}


def extract_base_title(title: str) -> str:
    """
    Extrait le titre de base d'un film pour regrouper les sagas.
    Version CONSERVATRICE qui évite les faux positifs.
    
    Ne regroupe QUE si le titre contient des indicateurs CLAIRS de suite :
    - Numéros en fin : "Matrix 2", "Bad Boys II"
    - Sous-titres après : ou virgule avec mots-clés de suite
    - Crossovers : "X vs Y" reste séparé
    
    Exemples:
        "Alien" -> "Alien" (inchangé)
        "Alien, le huitième passager" -> "Alien" (virgule détectée)
        "Alien: Romulus" -> "Alien" (deux-points + nom propre)
        "Alien vs Predator" -> "Alien vs Predator" (crossover = saga séparée)
        "Bad Boys II" -> "Bad Boys" (numéro romain)
        "Matrix 2" -> "Matrix" (numéro arabe)
        "7 jours pas plus" -> "7 jours pas plus" (INCHANGÉ - pas de pattern de suite)
    
    Args:
        title: Titre complet du film
    
    Returns:
        Titre de base (saga) OU titre original si aucun pattern détecté
    """
    if not title:
        return title
    
    original = title.strip()
    
    # CAS 1 : Crossovers (vs/versus/contre) = Saga séparée
    # "Alien vs Predator" reste "Alien vs Predator"
    if re.search(r'\b(vs\.?|versus|contre)\b', original, re.I):
        # Supprimer uniquement le sous-titre après :
        if ':' in original:
            base = original.split(':')[0].strip()
        else:
            base = original
        # Supprimer les numéros en fin UNIQUEMENT
        base = re.sub(r'\s+[IVX]+$', '', base, flags=re.I).strip()
        base = re.sub(r'\s+\d+$', '', base).strip()
        return base
    
    # CAS 2 : Mots-clés de suite EXPLICITES (Chapitre, Partie, etc.) - PRIORITAIRE
    # "John Wick Chapitre 3" -> "John Wick"
    chapter_match = re.search(r'^(.+?)\s+(?:chapitre|chapter|part|partie)\s+\d+', original, re.I)
    if chapter_match:
        return chapter_match.group(1).strip()
    
    episode_match = re.search(r'^(.+?)\s+(?:episode|épisode)\s+\d+', original, re.I)
    if episode_match:
        return episode_match.group(1).strip()
    
    # CAS 3 : Numéros romains/arabes EN FIN (suite claire)
    # "Bad Boys II" -> "Bad Boys"
    # "Matrix 2" -> "Matrix"
    if re.search(r'\s+([IVX]+|\d+)$', original, re.I):
        base = re.sub(r'\s+[IVX]+$', '', original, flags=re.I).strip()
        base = re.sub(r'\s+\d+$', '', base).strip()
        return base
    
    # CAS 4 : Sous-titres après : ou , SEULEMENT si contiennent des mots-clés de suite
    # "Alien, le huitième passager" -> "Alien" (virgule + article)
    # "Alien: Covenant" -> "Alien" (deux-points + nom propre)
    # "7 jours pas plus" -> "7 jours pas plus" (INCHANGÉ)
    
    if ':' in original:
        parts = original.split(':', 1)
        main_part = parts[0].strip()
        subtitle = parts[1].strip()
        
        # Vérifier si le sous-titre ressemble à une suite
        # Indicateurs : commence par article, numéro, ou mot-clé
        suite_indicators = [
            r'^(?:le|la|les|l\'|the|a|an)\s',  # Articles
            r'^(?:reloaded|revolutions|resurrection|origins|returns|begins|rises)',  # Mots-clés
            r'^\w+$',  # Un seul mot (probable nom propre de suite)
        ]
        
        is_sequel = any(re.search(indicator, subtitle, re.I) for indicator in suite_indicators)
        
        if is_sequel:
            return main_part
    
    if ',' in original:
        parts = original.split(',', 1)
        main_part = parts[0].strip()
        subtitle = parts[1].strip()
        
        # Virgule suivie d'article = probablement un sous-titre
        if re.search(r'^(?:le|la|les|l\'|the|a|an)\s', subtitle, re.I):
            return main_part
    
    # CAS 5 : Tiret suivi de numéro = suite
    # "Matrix - 2" -> "Matrix"
    if re.search(r'\s*[-:]\s*\d+$', original):
        base = re.sub(r'\s*[-:]\s*\d+$', '', original).strip()
        return base
    
    # AUCUN PATTERN DÉTECTÉ : Retourner le titre original
    # Évite les faux positifs comme "7 jours pas plus"
    return original


def extract_collection_info(title: str) -> Dict[str, Optional[any]]:
    """
    Extrait les informations de collection/saga d'un titre.
    Version CONSERVATRICE alignée avec extract_base_title.
    
    Ne détecte une collection QUE si des patterns CLAIRS de suite sont présents.
    
    Args:
        title: Titre nettoyé du film/série
    
    Returns:
        Dict avec 'collection' (nom de la saga) et 'episode' (numéro)
        {'collection': 'Matrix', 'episode': 2} ou {'collection': None, 'episode': None}
    
    Exemples:
        "Bad Boys II" -> {'collection': 'Bad Boys', 'episode': 2}
        "Matrix 2" -> {'collection': 'Matrix', 'episode': 2}
        "Alien: Covenant" -> {'collection': 'Alien', 'episode': None}
        "7 jours pas plus" -> {'collection': None, 'episode': None}
    """
    result = {'collection': None, 'episode': None}
    
    if not title:
        return result
    
    original = title.strip()
    
    # Pattern 1: Numéros romains en fin (ex: "Bad Boys II")
    roman_match = re.search(r'^(.+?)\s+([IVX]+)$', original, re.I)
    if roman_match:
        collection_name = roman_match.group(1).strip()
        roman_num = roman_match.group(2).upper()
        if roman_num in _ROMAN_TO_INT:
            result['collection'] = collection_name
            result['episode'] = _ROMAN_TO_INT[roman_num]
            return result
    
    # Pattern 2: Numéros arabes en fin (ex: "Matrix 2")
    arabic_match = re.search(r'^(.+?)\s+(\d+)$', original)
    if arabic_match:
        collection_name = arabic_match.group(1).strip()
        num = int(arabic_match.group(2))
        # Éviter les faux positifs : numéro doit être <= 20 (sinon probablement une année)
        if num <= 20:
            result['collection'] = collection_name
            result['episode'] = num
            return result
    
    # Pattern 3: Chapitre/Partie/Chapter/Part (ex: "John Wick Chapitre 3")
    chapter_match = re.search(r'^(.+?)\s+(?:chapitre|chapter|part|partie)\s+(\d+)', original, re.I)
    if chapter_match:
        result['collection'] = chapter_match.group(1).strip()
        result['episode'] = int(chapter_match.group(2))
        return result
    
    # Pattern 4: Épisode de série (ex: "Breaking Bad S01E01")
    episode_match = re.search(r'^(.+?)\s+S(\d{1,2})E\d{1,2}', original, re.I)
    if episode_match:
        result['collection'] = episode_match.group(1).strip()
        result['episode'] = int(episode_match.group(2))
        return result
    
    # Pattern 5: Tiret suivi de numéro (ex: "Matrix - 2")
    dash_match = re.search(r'^(.+?)\s*[-:]\s*(\d+)$', original)
    if dash_match:
        collection_name = dash_match.group(1).strip()
        num = int(dash_match.group(2))
        if num <= 20:
            result['collection'] = collection_name
            result['episode'] = num
            return result
    
    # Pattern 6: Sous-titre après : avec indicateurs de suite
    if ':' in original:
        parts = original.split(':', 1)
        main_part = parts[0].strip()
        subtitle = parts[1].strip()
        
        # Vérifier si c'est une suite évidente
        suite_indicators = [
            r'^(?:le|la|les|l\'|the|a|an)\s',
            r'^(?:reloaded|revolutions|resurrection|origins|returns|begins|rises|covenant|romulus)',
            r'^\w+$',  # Un seul mot
        ]
        
        is_sequel = any(re.search(indicator, subtitle, re.I) for indicator in suite_indicators)
        
        if is_sequel:
            result['collection'] = main_part
            # Pas de numéro d'épisode détectable
            return result
    
    # AUCUN pattern détecté - pas une suite
    return result


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
