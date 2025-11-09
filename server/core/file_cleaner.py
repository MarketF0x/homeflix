"""
Module de nettoyage des noms de fichiers vidéo pour améliorer la reconnaissance TMDB.
Supprime les mots-clés techniques, les balises de release, et normalise les noms.
"""

import re
from pathlib import Path
from typing import List, Tuple
from core.db import get_session
from core.models import Video


# ====================
# PATTERNS DE NETTOYAGE
# ====================

# Résolutions et codecs
RESOLUTION_PATTERN = re.compile(
    r"\b(?:480|720|1080|2160|4k|8k)p?\b",
    re.IGNORECASE
)

CODEC_PATTERN = re.compile(
    r"\b(?:x264|x265|h264|h265|hevc|avc|xvid|divx|vc1)\b",
    re.IGNORECASE
)

# Sources de release
SOURCE_PATTERN = re.compile(
    r"\b(?:WEBRip|WEB-DL|BluRay|BRRip|BDRip|HDRip|DVDRip|DVD-Rip|HDTV|PDTV|"
    r"CAM|TS|TC|SCR|R5|DVDSCR|WEBRIP|BRRIP|HDRIP)\b",
    re.IGNORECASE
)

# Audio (avec patterns plus stricts - éviter de matcher "HD" seul)
AUDIO_PATTERN = re.compile(
    r"(?:\b(?:AAC|AC3|DTS|FLAC|MP3|TrueHD|ATMOS|DTS-HD|MA)\b|"
    r"DD\s*\d+\.\d+|DD\d+|"  # DD5.1, DD51, etc.
    r"(?<!\w)\d+\.\d+\s*(?:ch)?(?!\w))",  # 5.1, 7.1, etc. (mais pas dans un mot)
    re.IGNORECASE
)

# Langues
LANGUAGE_PATTERN = re.compile(
    r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|VFI|VF2|MULTI|MULTi|ENGLISH|"
    r"SUBFRENCH|SUBFORCED|VO|VF|VOST)\b",
    re.IGNORECASE
)

# Teams/Groups de release (avec pattern -TEAM à la fin)
TEAM_PATTERN = re.compile(
    r"(?:\b(?:YIFY|YTS|RARBG|SPARKS|EVO|FGT|ION10|NAHOM|PSA|CMRG|GalaxyRG|"
    r"UTR|YG|ETRG|STUTTERSHIT|VPPV|DEFLATE|EXTREME|CiELOS)\b|"
    r"-[A-Z0-9]+$)",  # Pattern -TEAM en fin de nom
    re.IGNORECASE
)

# Balises entre crochets/parenthèses (mais garde les années entre parenthèses)
BRACKETS_PATTERN = re.compile(
    r"\[.*?\]",  # Supprime tout entre crochets
    re.IGNORECASE
)

# Mots-clés divers
MISC_KEYWORDS = re.compile(
    r"\b(?:EXTENDED|UNRATED|DIRECTORS?\.CUT|REMASTERED|REPACK|PROPER|"
    r"REAL|RETAIL|LIMITED|INTERNAL|STV|FESTIVAL|DUBBED|SUBBED|"
    r"COMPLETE|COLLECTOR|EDITION|ANNIVERSARY|IMAX|3D|HFR|HDR|HDR10|"
    r"DOLBY|VISION|10BIT|8BIT|MA|NF|AMZN|DSNP|HMAX|WEB|HD|UHD|FHD|SD)\b",
    re.IGNORECASE
)

# Séparateurs multiples
SEPARATORS_PATTERN = re.compile(r"[._\-]+")

# Espaces multiples
SPACES_PATTERN = re.compile(r"\s{2,}")


# ====================
# FONCTIONS PRINCIPALES
# ====================

def clean_filename(filename: str, keep_year: bool = True) -> str:
    """
    Nettoie un nom de fichier en supprimant tous les mots-clés techniques.
    
    Args:
        filename: Nom du fichier (avec ou sans extension)
        keep_year: Garder l'année si présente (recommandé pour TMDB)
    
    Returns:
        Nom de fichier nettoyé
    
    Exemples:
        >>> clean_filename("The.Matrix.1999.1080p.BluRay.x264.DTS-HD.MA.5.1-SPARKS")
        'The Matrix 1999'
        
        >>> clean_filename("Inception (2010) [1080p] [YTS.AG]")
        'Inception 2010'
        
        >>> clean_filename("Breaking.Bad.S01E01.VOSTFR.720p.WEB-DL.DD5.1.H264")
        'Breaking Bad S01E01'
    """
    # Enlever l'extension
    name = Path(filename).stem
    
    # Extraire et sauvegarder l'année si demandé
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", name)
    year = year_match.group(1) if (keep_year and year_match) else None
    
    # Extraire et sauvegarder les marqueurs de série (S01E01, etc.)
    episode_match = re.search(r"\b(S\d{1,2}E\d{1,2})\b", name, re.IGNORECASE)
    episode = episode_match.group(1).upper() if episode_match else None
    
    # Supprimer d'abord les crochets et parenthèses (sauf années)
    name = BRACKETS_PATTERN.sub(" ", name)
    # Supprimer les parenthèses vides ou avec juste des chiffres/espaces (mais garder l'année)
    name = re.sub(r"\(\s*\)", " ", name)  # Parenthèses vides
    if year:
        # Enlever toutes les parenthèses sauf celles autour de l'année
        name = re.sub(r"\((?!" + year + r").*?\)", " ", name)
        # Supprimer les parenthèses autour de l'année
        name = name.replace(f"({year})", year)
        name = name.replace(f"( {year} )", year)
    
    # Supprimer l'année et l'épisode temporairement
    if year:
        name = name.replace(year, " XXYEARXX ")
    if episode:
        name = re.sub(r"\b" + re.escape(episode) + r"\b", " XXEPISODEXX ", name, flags=re.IGNORECASE)
    
    # Appliquer tous les patterns de nettoyage
    name = RESOLUTION_PATTERN.sub(" ", name)
    name = CODEC_PATTERN.sub(" ", name)
    name = SOURCE_PATTERN.sub(" ", name)
    name = AUDIO_PATTERN.sub(" ", name)
    name = LANGUAGE_PATTERN.sub(" ", name)
    name = TEAM_PATTERN.sub(" ", name)
    name = MISC_KEYWORDS.sub(" ", name)
    
    # Remplacer les séparateurs par des espaces
    name = SEPARATORS_PATTERN.sub(" ", name)
    
    # Réinjecter l'année et l'épisode
    if episode:
        name = name.replace("XXEPISODEXX", episode)
    if year and keep_year:
        name = name.replace("XXYEARXX", year)
    
    # Nettoyer les espaces multiples
    name = SPACES_PATTERN.sub(" ", name)
    name = name.strip()
    
    return name


def suggest_rename(file_path: Path) -> Tuple[Path, str]:
    """
    Suggère un nouveau nom de fichier nettoyé.
    
    Args:
        file_path: Chemin complet du fichier
    
    Returns:
        Tuple (nouveau_chemin, nom_nettoyé)
    """
    cleaned_name = clean_filename(file_path.name)
    new_filename = cleaned_name + file_path.suffix
    new_path = file_path.parent / new_filename
    
    return new_path, cleaned_name


def rename_file_on_disk(old_path: Path, new_path: Path, dry_run: bool = True) -> bool:
    """
    Renomme physiquement un fichier sur le disque.
    
    Args:
        old_path: Ancien chemin
        new_path: Nouveau chemin
        dry_run: Si True, ne fait que simuler (pas de modification réelle)
    
    Returns:
        True si le renommage a réussi (ou serait réussi en mode dry_run)
    """
    if not old_path.exists():
        print(f"❌ Fichier introuvable : {old_path}")
        return False
    
    if old_path == new_path:
        print(f"⏭️ Aucun changement : {old_path.name}")
        return False
    
    if new_path.exists():
        print(f"⚠️ Le fichier cible existe déjà : {new_path}")
        return False
    
    if dry_run:
        print(f"🔍 [DRY RUN] {old_path.name} → {new_path.name}")
        return True
    
    try:
        old_path.rename(new_path)
        print(f"✅ Renommé : {old_path.name} → {new_path.name}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du renommage de {old_path.name}: {e}")
        return False


def clean_database_filenames(dry_run: bool = True, update_titles: bool = True) -> dict:
    """
    Nettoie les noms de fichiers dans la base de données.
    
    Args:
        dry_run: Si True, ne fait que simuler (pas de modification)
        update_titles: Si True, met aussi à jour les titres dans la BDD
    
    Returns:
        Statistiques du nettoyage
    """
    stats = {
        "total": 0,
        "renamed": 0,
        "errors": 0,
        "skipped": 0
    }
    
    with get_session() as session:
        videos = session.query(Video).all()
        stats["total"] = len(videos)
        
        print(f"\n{'='*60}")
        print(f"🧹 NETTOYAGE DES FICHIERS {'(MODE SIMULATION)' if dry_run else '(MODE RÉEL)'}")
        print(f"{'='*60}\n")
        
        for video in videos:
            try:
                old_path = Path(video.path)
                
                if not old_path.exists():
                    print(f"⚠️ Fichier manquant : {old_path}")
                    stats["skipped"] += 1
                    continue
                
                new_path, cleaned_name = suggest_rename(old_path)
                
                # Renommer le fichier physique
                if rename_file_on_disk(old_path, new_path, dry_run=dry_run):
                    stats["renamed"] += 1
                    
                    # Mettre à jour la BDD
                    if not dry_run:
                        video.path = str(new_path)
                        if update_titles:
                            video.title = cleaned_name
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                print(f"❌ Erreur avec {video.path}: {e}")
                stats["errors"] += 1
        
        if not dry_run:
            session.commit()
            print(f"\n💾 Base de données mise à jour.")
    
    print(f"\n{'='*60}")
    print(f"📊 STATISTIQUES")
    print(f"{'='*60}")
    print(f"Total de vidéos     : {stats['total']}")
    print(f"Renommées          : {stats['renamed']}")
    print(f"Ignorées           : {stats['skipped']}")
    print(f"Erreurs            : {stats['errors']}")
    print(f"{'='*60}\n")
    
    return stats


def preview_cleaning(limit: int = 20) -> List[dict]:
    """
    Affiche un aperçu des renommages qui seraient effectués.
    
    Args:
        limit: Nombre maximum de résultats à afficher
    
    Returns:
        Liste des changements prévus
    """
    changes = []
    
    with get_session() as session:
        videos = session.query(Video).limit(limit).all()
        
        print(f"\n{'='*80}")
        print(f"🔍 APERÇU DES RENOMMAGES (premiers {limit} fichiers)")
        print(f"{'='*80}\n")
        
        for video in videos:
            old_path = Path(video.path)
            new_path, cleaned_name = suggest_rename(old_path)
            
            if old_path != new_path:
                change = {
                    "old_name": old_path.name,
                    "new_name": new_path.name,
                    "old_title": video.title,
                    "new_title": cleaned_name,
                    "path": str(old_path.parent)
                }
                changes.append(change)
                
                print(f"📁 {old_path.parent}")
                print(f"   Ancien : {old_path.name}")
                print(f"   Nouveau: {new_path.name}")
                print(f"   Titre  : {video.title} → {cleaned_name}")
                print()
        
        print(f"{'='*80}")
        print(f"Total de changements prévus : {len(changes)}/{len(videos)}")
        print(f"{'='*80}\n")
    
    return changes


# ====================
# FONCTION DE TEST
# ====================

def test_cleaning():
    """Teste le nettoyage sur des exemples types."""
    test_cases = [
        "The.Matrix.1999.1080p.BluRay.x264.DTS-HD.MA.5.1-SPARKS.mkv",
        "Inception (2010) [1080p] [YTS.AG].mp4",
        "Breaking.Bad.S01E01.VOSTFR.720p.WEB-DL.DD5.1.H264.avi",
        "Avatar.2009.EXTENDED.1080p.BluRay.x264.TrueHD.7.1.Atmos-FGT.mkv",
        "Le.Seigneur.des.Anneaux.2001.FRENCH.BRRip.XviD.AC3-EXTREME.avi",
        "Interstellar.2014.IMAX.1080p.BluRay.x265.10bit.HDR.mkv",
        "Game.of.Thrones.S08E06.MULTI.1080p.WEB.H264-CiELOS.mkv",
    ]
    
    print(f"\n{'='*80}")
    print("🧪 TEST DE NETTOYAGE")
    print(f"{'='*80}\n")
    
    for test in test_cases:
        cleaned = clean_filename(test)
        print(f"Original : {test}")
        print(f"Nettoyé  : {cleaned}")
        print()
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Lancer le test de nettoyage
    test_cleaning()
