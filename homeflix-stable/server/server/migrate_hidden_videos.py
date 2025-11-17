"""
Migration pour créer la table hidden_videos
Permet aux profils secondaires de masquer des vidéos sans les supprimer
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"

def migrate():
    """Crée la table hidden_videos si elle n'existe pas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hidden_videos'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Créer la table hidden_videos
            cursor.execute("""
                CREATE TABLE hidden_videos (
                    profile_id INTEGER NOT NULL,
                    video_id INTEGER NOT NULL,
                    hidden_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (profile_id, video_id),
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            """)
            print("✓ Table hidden_videos créée")
            
            # Créer un index pour des requêtes rapides
            cursor.execute("""
                CREATE INDEX idx_hidden_profile ON hidden_videos(profile_id)
            """)
            print("✓ Index idx_hidden_profile créé")
        else:
            print("✓ Table hidden_videos déjà existante")
        
        conn.commit()
        print("✓ Migration hidden_videos terminée")
        
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
