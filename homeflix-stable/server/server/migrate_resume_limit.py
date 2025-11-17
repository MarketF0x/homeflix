"""
Migration pour ajouter le champ last_position_updated et limiter les reprises à 10 films.
"""
import sqlite3
from pathlib import Path

# Chemin vers la base de données (dans le dossier data/)
APP_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = APP_ROOT / "data" / "homeone.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(videos)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'last_position_updated' not in columns:
        print("Ajout de la colonne 'last_position_updated'...")
        cursor.execute("ALTER TABLE videos ADD COLUMN last_position_updated DATETIME")
        
        # Initialiser last_position_updated pour les vidéos ayant déjà une position
        print("Initialisation des dates pour les vidéos en cours...")
        cursor.execute("""
            UPDATE videos 
            SET last_position_updated = datetime('now') 
            WHERE last_position > 0 AND watched = 0
        """)
        
        # Limiter à 10 films les plus récents (basé sur updated_at comme approximation)
        print("Limitation à 10 films en attente de reprise...")
        cursor.execute("""
            UPDATE videos 
            SET last_position = 0, last_position_updated = NULL
            WHERE id IN (
                SELECT id FROM videos 
                WHERE last_position > 0 AND watched = 0
                ORDER BY updated_at ASC
                LIMIT -1 OFFSET 10
            )
        """)
        
        conn.commit()
        print("✓ Migration terminée avec succès!")
    else:
        print("La colonne 'last_position_updated' existe déjà. Aucune migration nécessaire.")
    
    conn.close()

if __name__ == "__main__":
    migrate()
