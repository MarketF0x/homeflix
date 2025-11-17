"""
Migration: Ajout des champs collection et episode_number
"""

from core.db import engine, get_session
from core.models import Video
from sqlalchemy import text

def migrate():
    """Ajoute les colonnes collection et episode_number à la table videos."""
    print("🔄 Migration: Ajout des champs collection et episode_number...")
    
    with engine.connect() as conn:
        # Vérifier si les colonnes existent déjà
        result = conn.execute(text("PRAGMA table_info(videos)"))
        columns = [row[1] for row in result]
        
        # Ajouter collection si elle n'existe pas
        if 'collection' not in columns:
            print("  → Ajout de la colonne 'collection'...")
            conn.execute(text("ALTER TABLE videos ADD COLUMN collection VARCHAR"))
            conn.commit()
            print("  ✅ Colonne 'collection' ajoutée")
        else:
            print("  ⏭️  Colonne 'collection' déjà présente")
        
        # Ajouter episode_number si elle n'existe pas
        if 'episode_number' not in columns:
            print("  → Ajout de la colonne 'episode_number'...")
            conn.execute(text("ALTER TABLE videos ADD COLUMN episode_number INTEGER"))
            conn.commit()
            print("  ✅ Colonne 'episode_number' ajoutée")
        else:
            print("  ⏭️  Colonne 'episode_number' déjà présente")
    
    # Créer l'index composite
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_collection_episode ON videos (collection, episode_number)"))
            conn.commit()
            print("  ✅ Index 'idx_collection_episode' créé")
    except Exception as e:
        print(f"  ⚠️  Index déjà existant ou erreur: {e}")
    
    print("✅ Migration terminée avec succès!")

if __name__ == "__main__":
    migrate()
