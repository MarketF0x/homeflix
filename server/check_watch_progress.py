import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print("📊 Contenu de la table watch_progress:")
print("=" * 80)

cursor.execute("""
    SELECT wp.id, wp.profile_id, wp.video_id, wp.position, wp.updated_at,
           p.name as profile_name
    FROM watch_progress wp
    LEFT JOIN profiles p ON wp.profile_id = p.id
    ORDER BY wp.updated_at DESC
""")

rows = cursor.fetchall()

if not rows:
    print("⚠️  Aucune progression enregistrée")
else:
    print(f"✅ {len(rows)} progression(s) trouvée(s):\n")
    for row in rows:
        print(f"  ID: {row[0]}")
        print(f"  Profil: {row[5]} (ID: {row[1]})")
        print(f"  Vidéo ID: {row[2]}")
        print(f"  Position: {row[3]} secondes ({row[3]//60}min {row[3]%60}s)")
        print(f"  Mis à jour: {row[4]}")
        print("-" * 80)

print("\n📊 Profils disponibles:")
cursor.execute("SELECT id, name, is_main FROM profiles")
profiles = cursor.fetchall()
for p in profiles:
    print(f"  • {p[1]} (ID: {p[0]}) {'[PRINCIPAL]' if p[2] else ''}")

conn.close()
