"""
Script de migration pour ajouter les index manquants à la base de données existante.
À exécuter une seule fois après la mise à jour du modèle.
"""
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import engine
from core.models import Base
from sqlalchemy import inspect, text

def add_indexes():
    """Ajoute les index manquants sans recréer les tables."""
    inspector = inspect(engine)
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('videos')}
    
    print("🔍 Vérification des index existants...")
    print(f"Index trouvés : {existing_indexes}")
    
    # Index à créer
    indexes_to_create = [
        ("idx_video_title", "CREATE INDEX IF NOT EXISTS idx_video_title ON videos(title)"),
        ("idx_video_year", "CREATE INDEX IF NOT EXISTS idx_video_year ON videos(year)"),
        ("idx_video_genre", "CREATE INDEX IF NOT EXISTS idx_video_genre ON videos(genre)"),
        ("idx_video_watched", "CREATE INDEX IF NOT EXISTS idx_video_watched ON videos(watched)"),
        ("idx_year_genre", "CREATE INDEX IF NOT EXISTS idx_year_genre ON videos(year, genre)"),
        ("idx_watched_year", "CREATE INDEX IF NOT EXISTS idx_watched_year ON videos(watched, year)"),
    ]
    
    with engine.connect() as conn:
        for idx_name, sql in indexes_to_create:
            if idx_name not in existing_indexes:
                print(f"✅ Création de l'index : {idx_name}")
                conn.execute(text(sql))
                conn.commit()
            else:
                print(f"⏭️  Index déjà existant : {idx_name}")
    
    print("\n✨ Migration terminée avec succès !")
    print("📊 Les performances de recherche sont maintenant optimisées.")

if __name__ == "__main__":
    add_indexes()
