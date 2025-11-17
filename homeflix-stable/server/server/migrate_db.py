"""
Script de migration pour ajouter les nouvelles colonnes au modèle Video.
À exécuter une seule fois pour mettre à jour la base existante.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "homeone.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si les colonnes existent déjà
    cursor.execute("PRAGMA table_info(videos)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Ajouter les nouvelles colonnes si elles n'existent pas
    if 'year' not in columns:
        print("Ajout de la colonne 'year'...")
        cursor.execute("ALTER TABLE videos ADD COLUMN year INTEGER")
    
    if 'genre' not in columns:
        print("Ajout de la colonne 'genre'...")
        cursor.execute("ALTER TABLE videos ADD COLUMN genre TEXT")
    
    if 'watched' not in columns:
        print("Ajout de la colonne 'watched'...")
        cursor.execute("ALTER TABLE videos ADD COLUMN watched BOOLEAN DEFAULT 0")
    
    if 'last_position' not in columns:
        print("Ajout de la colonne 'last_position'...")
        cursor.execute("ALTER TABLE videos ADD COLUMN last_position INTEGER DEFAULT 0")
    
    conn.commit()
    conn.close()
    print("✅ Migration terminée !")

if __name__ == "__main__":
    migrate()
