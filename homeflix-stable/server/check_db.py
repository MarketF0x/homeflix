import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print("📊 Tables présentes dans homeflix.db:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

if not tables:
    print("   ⚠️  Base vide - aucune table trouvée")
else:
    for table in tables:
        print(f"   • {table[0]}")
        
        # Afficher le schéma de chaque table
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"      - {col[1]} ({col[2]})")
        print()

conn.close()
