"""Debug direct avec SQLite"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"

print("🔍 Test direct avec SQLite (bypass API)")
print("=" * 70)

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Insérer manuellement une progression
print("\n1️⃣ Insertion manuelle dans watch_progress...")
cursor.execute("""
    INSERT INTO watch_progress (profile_id, video_id, position, updated_at)
    VALUES (?, ?, ?, ?)
""", (1, 99999, 120, datetime.utcnow().isoformat()))

conn.commit()
print("   ✅ Insertion réussie")

# Vérifier
cursor.execute("""
    SELECT id, profile_id, video_id, position, updated_at
    FROM watch_progress
    WHERE video_id = 99999
""")
row = cursor.fetchone()

if row:
    print(f"\n2️⃣ Vérification:")
    print(f"   ID: {row[0]}")
    print(f"   Profile: {row[1]}")
    print(f"   Video: {row[2]}")
    print(f"   Position: {row[3]}s")
    print(f"   Updated: {row[4]}")
    print("\n   ✅ SQLite fonctionne correctement")
else:
    print("\n   ❌ Échec de lecture")

# Nettoyer
cursor.execute("DELETE FROM watch_progress WHERE video_id = 99999")
conn.commit()
conn.close()

print("\n" + "=" * 70)
print("✅ La base de données fonctionne")
print("\n⚠️  Le problème vient de SQLAlchemy ou de la gestion de session")
print("   → Vérifier que s.commit() est bien appelé")
print("   → Vérifier que la session n'est pas en mode autocommit=False")
