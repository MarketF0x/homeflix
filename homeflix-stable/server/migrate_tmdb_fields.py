"""
Script de migration pour ajouter les champs TMDb à la base de données
Ajoute : overview, vote_average, cast, poster_path
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Ajoute les nouveaux champs TMDb à la table videos"""
    
    # Chemin vers la base de données (même logique que db.py)
    app_root = Path(__file__).resolve().parents[1]
    data_dir = app_root / "data"
    db_path = data_dir / "homeone.db"
    
    if not db_path.exists():
        print("❌ Base de données non trouvée :", db_path)
        return False
    
    print(f"📊 Migration de la base de données : {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des colonnes à ajouter
    new_columns = [
        ("overview", "TEXT"),
        ("vote_average", "REAL"),
        ("cast", "TEXT"),
        ("poster_path", "TEXT"),
    ]
    
    # Vérifier quelles colonnes existent déjà
    cursor.execute("PRAGMA table_info(videos)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print(f"✅ Colonnes existantes : {len(existing_columns)}")
    
    # Ajouter les colonnes manquantes
    added = 0
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE videos ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Ajout colonne : {col_name} ({col_type})")
                added += 1
            except sqlite3.Error as e:
                print(f"  ⚠️  Erreur pour {col_name} : {e}")
        else:
            print(f"  ⏭️  Colonne déjà présente : {col_name}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration terminée : {added} colonnes ajoutées")
    return True


if __name__ == "__main__":
    migrate_database()
