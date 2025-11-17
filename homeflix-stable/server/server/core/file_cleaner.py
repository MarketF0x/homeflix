"""
Module de nettoyage des noms de fichiers vidéo pour améliorer la reconnaissance TMDB.
Supprime les mots-clés techniques, les balises de release, et normalise les noms.
"""

import re
from pathlib import Path
from typing import List, Tuple
from core.db import get_session
from core.models import Video
from core.logger import logger, log_exception


# ====================
# PATTERNS DE NETTOYAGE
# ====================

# Résolutions et codecs
RESOLUTION_PATTERN = re.compile(
    r"\b(?:\d{3,4}p)\b",  # 360p, 480p, 720p, 1080p, 2160p, etc.
    re.IGNORECASE
)

CODEC_PATTERN = re.compile(
    r"\b(?:x264|x265|h264|h265|h\s*264|h\s*265|hevc|avc|xvid|divx|vc1)\b",
    re.IGNORECASE
)

# Sources de release
SOURCE_PATTERN = re.compile(
    r"\b(?:WEBRip|WEB-DL|BluRay|BRRip|BDRip|HDRip|DVDRip|DVD-Rip|DvD\s*Rip|HDTV|HDTS|PDTV|"
    r"CAM|TS|TC|SCR|R5|DVDSCR|WEBRIP|BRRIP|HDRIP|HDLIGHT|STREAMING|mHD|MD)\b",
    re.IGNORECASE
)

# Audio (avec patterns plus stricts - éviter de matcher "HD" seul)
AUDIO_PATTERN = re.compile(
    r"(?:\b(?:AAC|AC3|DTS|FLAC|MP3|TrueHD|ATMOS|DTS-HD|MA|DDP|DD|EAC3|E-AC-3)\b|"
    r"DD\s*\d+[\s.]\d+|DD\d+|DDP\s*\d+[\s.]\d+|DDP\d+|"  # DD5.1, DD51, DDP5.1, DDP5 1, etc.
    r"(?<!\w)\d+[\s.]\d+\s*(?:ch)?(?!\w))",  # 5.1, 5 1, 7.1, etc. (mais pas dans un mot)
    re.IGNORECASE
)

# Langues (patterns stricts pour éviter de couper les mots)
LANGUAGE_PATTERN = re.compile(
    r"\b(?:VOSTFR|FRENCH|TRUEFRENCH|VFF|VFQ|VFI|VF2|MULTI|MULTi|ENGLISH|"
    r"SUBFRENCH|SUBFORCED|VO|VOST|VOF|SUB)\b|"
    r"\sFR\b|\sEN\b|\sENG\b|\sVF\b|\sFr\b",  # FR, EN, Fr précédés d'un espace
    re.IGNORECASE
)

# Teams/Groups de release (avec pattern -TEAM à la fin)
TEAM_PATTERN = re.compile(
    r"(?:\b(?:YIFY|YTS|RARBG|SPARKS|EVO|FGT|ION10|NAHOM|PSA|CMRG|GalaxyRG|"
    r"UTR|YG|ETRG|STUTTERSHIT|VPPV|DEFLATE|EXTREME|CiELOS|GHT|"
    r"KILLERS|FUM|DRONES|COCKLES|LOST|BLOW|DEPTH|FLEET|GZR|"
    r"ROVERS|CRYS|NOMA|PHOENiX|GECKOS|MZABI|TITROV|BPH|DREAD)\b|"
    r"-[A-Z0-9]+$)",  # Pattern -TEAM en fin de nom
    re.IGNORECASE
)

# Tags techniques supplémentaires
TECH_TAGS_PATTERN = re.compile(
    r"\b(?:VMPP|mHDgz|mHD|JiHEFF|AV1|QTZ|4KLight|6CH|8CH|Blu[-\s]?Ray|BR)\b",
    re.IGNORECASE
)

# Mots-clés de streaming/plateformes (éviter de matcher "en" au milieu des mots)
STREAMING_KEYWORDS = re.compile(
    r"\b(?:GRATUIT|Complet|Streaming|Film|sur|StreamComp|StreeamComp|"
    r"Comp\b|Franç(?:ais)?|Comple\b)|"
    r"(?:^|\s)en(?:\s|$)",  # "en" seulement si isolé
    re.IGNORECASE
)

# Balises entre crochets/parenthèses (mais garde les années entre parenthèses)
BRACKETS_PATTERN = re.compile(
    r"\[.*?\]",  # Supprime tout entre crochets
    re.IGNORECASE
)

# Mots-clés divers
MISC_KEYWORDS = re.compile(
    r"(?:\b(?:EXTENDED|UNRATED|DIRECTORS?\.CUT|REMASTERED|REPACK|PROPER|"
    r"REAL|RETAIL|LIMITED|INTERNAL|STV|FESTIVAL|DUBBED|SUBBED|"
    r"COMPLETE|COLLECTOR|EDITION|ANNIVERSARY|IMAX|3D|HFR|DV|"
    r"DOLBY|VISION|10BITS?|8BITS?|MA|NF|AMZN|DSNP|HMAX|WEB|HD|UHD|FHD|SD|V2)\b|"
    r"HDR10Plus|HDR10P|HDR)",  # HDR10Plus et variants
    re.IGNORECASE
)

# Séparateurs multiples
SEPARATORS_PATTERN = re.compile(r"[._\-]+")

# Espaces multiples
SPACES_PATTERN = re.compile(r"\s{2,}")


# ====================
# FONCTIONS PRINCIPALES
# ====================

def clean_filename(filename: str, keep_year: bool = False) -> str:
    """
    Nettoie un nom de fichier en supprimant tous les mots-clés techniques.
    
    Args:
        filename: Nom du fichier (avec ou sans extension)
        keep_year: Garder l'année si présente (par défaut: False, TMDb s'en charge)
    
    Returns:
        Nom de fichier nettoyé
    
    Exemples:
        >>> clean_filename("The.Matrix.1999.1080p.BluRay.x264.DTS-HD.MA.5.1-SPARKS")
        'The Matrix'
        
        >>> clean_filename("Inception (2010) [1080p] [YTS.AG]")
        'Inception'
        
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
    else:
        # Supprimer toutes les parenthèses
        name = re.sub(r"\(.*?\)", " ", name)
    
    # Supprimer l'année et l'épisode temporairement
    if year:
        name = name.replace(year, " XXYEARXX ")
    if episode:
        name = re.sub(r"\b" + re.escape(episode) + r"\b", " XXEPISODEXX ", name, flags=re.IGNORECASE)
    
    # Supprimer TOUTES les années (1900-2099)
    name = re.sub(r"\b(19\d{2}|20\d{2})\b", " ", name)
    
    # Appliquer tous les patterns de nettoyage
    name = RESOLUTION_PATTERN.sub(" ", name)
    name = CODEC_PATTERN.sub(" ", name)
    name = SOURCE_PATTERN.sub(" ", name)
    name = AUDIO_PATTERN.sub(" ", name)
    name = LANGUAGE_PATTERN.sub(" ", name)
    name = TEAM_PATTERN.sub(" ", name)
    name = TECH_TAGS_PATTERN.sub(" ", name)
    name = STREAMING_KEYWORDS.sub(" ", name)
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


def rename_file_on_disk(old_path: Path, new_path: Path, dry_run: bool = True) -> dict:
    """
    Renomme physiquement un fichier sur le disque.
    
    Args:
        old_path: Ancien chemin
        new_path: Nouveau chemin
        dry_run: Si True, ne fait que simuler (pas de modification réelle)
    
    Returns:
        Dict avec statut: 'success', 'skipped', 'error', 'exists', 'permission_denied'
    """
    result = {
        'status': 'unknown',
        'old_name': old_path.name,
        'new_name': new_path.name,
        'message': ''
    }
    
    if not old_path.exists():
        logger.error(f"Fichier introuvable : {old_path}")
        result['status'] = 'error'
        result['message'] = 'Fichier introuvable'
        return result
    
    if old_path == new_path:
        logger.info(f"⏭️ Aucun changement : {old_path.name}")
        result['status'] = 'skipped'
        result['message'] = 'Aucun changement nécessaire'
        return result
    
    if new_path.exists():
        # Vérifier s'il s'agit du même fichier (hardlink ou doublon réel)
        try:
            if old_path.resolve() == new_path.resolve():
                logger.warning(f"Même fichier (hardlink) : {old_path.name}")
                result['status'] = 'skipped'
                result['message'] = 'Hardlink vers le même fichier'
                return result
            else:
                logger.warning(f"Le fichier cible existe déjà : {new_path}")
                result['status'] = 'exists'
                result['message'] = f'Doublon détecté : {new_path}'
                return result
        except Exception:
            logger.warning(f"Le fichier cible existe déjà : {new_path}")
            result['status'] = 'exists'
            result['message'] = f'Doublon détecté : {new_path}'
            return result
    
    if dry_run:
        logger.info(f"[DRY RUN] {old_path.name} → {new_path.name}")
        result['status'] = 'success'
        result['message'] = 'Simulation réussie'
        return result
    
    try:
        old_path.rename(new_path)
        logger.info(f"Renommé : {old_path.name} → {new_path.name}")
        result['status'] = 'success'
        result['message'] = 'Renommage réussi'
        return result
    except PermissionError as e:
        logger.error(f"Erreur de permissions pour {old_path.name}: fichier verrouillé ou en lecture seule")
        result['status'] = 'permission_denied'
        result['message'] = f'Permissions refusées: {str(e)}'
        return result
    except Exception as e:
        logger.error(f"Erreur lors du renommage de {old_path.name}: {e}")
        result['status'] = 'error'
        result['message'] = str(e)
        return result


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
        "skipped": 0,
        "duplicates": 0,
        "permission_denied": 0
    }
    
    duplicates_log = []
    permission_errors_log = []
    
    with get_session() as session:
        videos = session.query(Video).all()
        stats["total"] = len(videos)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🧹 NETTOYAGE DES FICHIERS {'(MODE SIMULATION)' if dry_run else '(MODE RÉEL)'}")
        logger.info(f"{'='*60}\n")
        
        for video in videos:
            try:
                old_path = Path(video.path)
                
                if not old_path.exists():
                    logger.warning(f"Fichier manquant : {old_path}")
                    stats["skipped"] += 1
                    continue
                
                new_path, cleaned_name = suggest_rename(old_path)
                
                # Renommer le fichier physique
                result = rename_file_on_disk(old_path, new_path, dry_run=dry_run)
                
                if result['status'] == 'success':
                    stats["renamed"] += 1
                    
                    # Mettre à jour la BDD
                    if not dry_run:
                        video.path = str(new_path)
                        if update_titles:
                            video.title = cleaned_name
                
                elif result['status'] == 'skipped':
                    stats["skipped"] += 1
                
                elif result['status'] == 'exists':
                    stats["duplicates"] += 1
                    duplicates_log.append({
                        'original': str(old_path),
                        'target': str(new_path)
                    })
                
                elif result['status'] == 'permission_denied':
                    stats["permission_denied"] += 1
                    permission_errors_log.append({
                        'file': str(old_path),
                        'message': result['message']
                    })
                
                else:
                    stats["errors"] += 1
                    
            except Exception as e:
                logger.error(f"Erreur avec {video.path}: {e}")
                stats["errors"] += 1
        
        if not dry_run:
            session.commit()
            logger.info(f"\nBase de données mise à jour.")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 STATISTIQUES")
    logger.info(f"{'='*60}")
    logger.info(f"Total de vidéos       : {stats['total']}")
    logger.info(f"Renommées            : {stats['renamed']}")
    logger.warning(f"Ignorées             : {stats['skipped']}")
    logger.info(f"Doublons détectés    : {stats['duplicates']}")
    logger.error(f"Erreurs permissions  : {stats['permission_denied']}")
    logger.error(f"Autres erreurs       : {stats['errors']}")
    logger.info(f"{'='*60}\n")
    
    # Afficher les doublons détectés
    if duplicates_log:
        logger.warning(f"\nDOUBLONS DÉTECTÉS ({len(duplicates_log)}):")
        logger.info(f"{'='*60}")
        for dup in duplicates_log[:10]:  # Limiter à 10 pour lisibilité
            logger.info(f"Original : {dup['original']}")
            logger.info(f"Cible    : {dup['target']}")
            print()
        if len(duplicates_log) > 10:
            logger.info(f"... et {len(duplicates_log) - 10} autres doublons")
    
    # Afficher les erreurs de permissions
    if permission_errors_log:
        logger.error(f"\n🔒 ERREURS DE PERMISSIONS ({len(permission_errors_log)}):")
        logger.info(f"{'='*60}")
        for err in permission_errors_log[:5]:
            logger.info(f"Fichier : {err['file']}")
            logger.error(f"Erreur  : {err['message']}")
            print()
        if len(permission_errors_log) > 5:
            logger.error(f"... et {len(permission_errors_log) - 5} autres erreurs de permissions")
    
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
        
        logger.info(f"\n{'='*80}")
        logger.info(f"APERÇU DES RENOMMAGES (premiers {limit} fichiers)")
        logger.info(f"{'='*80}\n")
        
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
                
                logger.info(f"📁 {old_path.parent}")
                logger.info(f"   Ancien : {old_path.name}")
                logger.info(f"   Nouveau: {new_path.name}")
                logger.info(f"   Titre  : {video.title} → {cleaned_name}")
                print()
        
        logger.info(f"{'='*80}")
        logger.info(f"Total de changements prévus : {len(changes)}/{len(videos)}")
        logger.info(f"{'='*80}\n")
    
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
    
    logger.info(f"\n{'='*80}")
    logger.info("🧪 TEST DE NETTOYAGE")
    logger.info(f"{'='*80}\n")
    
    for test in test_cases:
        cleaned = clean_filename(test)
        logger.info(f"Original : {test}")
        logger.info(f"Nettoyé  : {cleaned}")
        print()
    
    logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    # Lancer le test de nettoyage
    test_cleaning()
