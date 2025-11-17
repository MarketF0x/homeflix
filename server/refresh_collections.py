#!/usr/bin/env python3
"""
Script pour ré-enrichir les collections TMDb de tous les films.
Force la mise à jour même pour les films déjà enrichis.
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier server au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
os.chdir(current_dir)

from db import get_session
from models import Video
from metadata_enricher import enrich_video_metadata
import yaml
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_settings():
    """Charge les paramètres depuis settings.yaml."""
    settings_path = Path(__file__).parent.parent / "settings.yaml"
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return type('Settings', (), data)()

def refresh_all_collections():
    """Force le rafraîchissement des collections pour tous les films."""
    
    settings = load_settings()
    api_key = settings.tmdb_api_key
    
    if not api_key:
        logger.error("❌ Clé API TMDb manquante dans settings.yaml")
        return
    
    with get_session() as session:
        # Récupérer tous les films (durée > min_film_minutes)
        all_videos = session.query(Video).all()
        
        films = [
            v for v in all_videos 
            if v.duration_minutes and v.duration_minutes >= settings.min_film_minutes
        ]
        
        logger.info(f"🎬 Début du rafraîchissement des collections pour {len(films)} films")
        logger.info(f"📋 Clé TMDb: {api_key[:10]}...")
        
        updated = 0
        failed = 0
        already_has_collection = 0
        
        for i, video in enumerate(films, 1):
            try:
                # Afficher progression tous les 10 films
                if i % 10 == 0:
                    logger.info(f"📊 Progression: {i}/{len(films)} films traités")
                
                # Vérifier si le film a déjà une collection TMDb
                if video.collection:
                    logger.info(f"✓ {video.title} a déjà une collection: {video.collection}")
                    already_has_collection += 1
                    continue
                
                # Forcer l'enrichissement
                logger.info(f"🔄 Enrichissement de: {video.title}")
                success = enrich_video_metadata(video, session, api_key)
                
                if success:
                    if video.collection:
                        logger.info(f"✅ Collection trouvée: {video.collection} pour {video.title}")
                        updated += 1
                    else:
                        logger.info(f"ℹ️ Pas de collection TMDb pour: {video.title}")
                else:
                    logger.warning(f"⚠️ Échec enrichissement pour: {video.title}")
                    failed += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur pour {video.title}: {e}")
                failed += 1
        
        logger.info("=" * 70)
        logger.info(f"✅ Rafraîchissement terminé !")
        logger.info(f"📊 Résumé:")
        logger.info(f"   - Films avec collection (déjà présente): {already_has_collection}")
        logger.info(f"   - Nouvelles collections ajoutées: {updated}")
        logger.info(f"   - Échecs: {failed}")
        logger.info(f"   - Total traité: {len(films)}")
        logger.info("=" * 70)

if __name__ == "__main__":
    refresh_all_collections()
