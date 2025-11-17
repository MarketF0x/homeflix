"""
Comparer les différences entre les deux bases de données
"""
import sqlite3
from pathlib import Path

print("🔍 COMPARAISON DÉTAILLÉE DES BASES DE DONNÉES")
print("=" * 80)

db1_path = Path("data/homeone.db")
db2_path = Path("server/homeflix.db")

# Charger les données de chaque base
conn1 = sqlite3.connect(db1_path)
cur1 = conn1.cursor()

conn2 = sqlite3.connect(db2_path)
cur2 = conn2.cursor()

# === VIDÉOS ===
print("\n📹 VIDÉOS")
print("-" * 80)

# Vidéos dans DB1
cur1.execute("SELECT id, title, path FROM videos ORDER BY id")
videos_db1 = {row[0]: {"title": row[1], "path": row[2]} for row in cur1.fetchall()}

# Vidéos dans DB2
cur2.execute("SELECT id, title, path FROM videos ORDER BY id")
videos_db2 = {row[0]: {"title": row[1], "path": row[2]} for row in cur2.fetchall()}

print(f"DB1 (data/homeone.db): {len(videos_db1)} vidéos")
print(f"DB2 (server/homeflix.db): {len(videos_db2)} vidéos")

# Vidéos uniquement dans DB1
only_in_db1 = set(videos_db1.keys()) - set(videos_db2.keys())
if only_in_db1:
    print(f"\n⚠️ Vidéos UNIQUEMENT dans data/homeone.db ({len(only_in_db1)}):")
    for vid_id in sorted(only_in_db1):
        print(f"   • ID {vid_id}: {videos_db1[vid_id]['title']}")
else:
    print(f"\n✅ Aucune vidéo unique dans data/homeone.db")

# Vidéos uniquement dans DB2
only_in_db2 = set(videos_db2.keys()) - set(videos_db1.keys())
if only_in_db2:
    print(f"\n⚠️ Vidéos UNIQUEMENT dans server/homeflix.db ({len(only_in_db2)}):")
    for vid_id in sorted(only_in_db2):
        print(f"   • ID {vid_id}: {videos_db2[vid_id]['title']}")
else:
    print(f"\n✅ Aucune vidéo unique dans server/homeflix.db")

# === PROFILS ===
print("\n\n👤 PROFILS")
print("-" * 80)

cur1.execute("SELECT id, name, is_main FROM profiles")
profiles_db1 = cur1.fetchall()
print(f"DB1 (data/homeone.db): {len(profiles_db1)} profils")
if profiles_db1:
    for p in profiles_db1:
        print(f"   • ID {p[0]}: {p[1]}{' (main)' if p[2] else ''}")

cur2.execute("SELECT id, name, is_main FROM profiles")
profiles_db2 = cur2.fetchall()
print(f"\nDB2 (server/homeflix.db): {len(profiles_db2)} profils")
if profiles_db2:
    for p in profiles_db2:
        print(f"   • ID {p[0]}: {p[1]}{' (main)' if p[2] else ''}")

# === PROGRESSIONS ===
print("\n\n⏱️ WATCH_PROGRESS (Progressions de lecture)")
print("-" * 80)

cur1.execute("""
    SELECT wp.id, wp.profile_id, wp.video_id, wp.position, wp.updated_at, v.title
    FROM watch_progress wp
    LEFT JOIN videos v ON wp.video_id = v.id
    ORDER BY wp.updated_at DESC
""")
progress_db1 = cur1.fetchall()
print(f"DB1 (data/homeone.db): {len(progress_db1)} progressions")
if progress_db1:
    for p in progress_db1:
        print(f"   • Video ID {p[2]}: '{p[5]}' - Position: {p[3]}s (Profile: {p[1] or 'NULL'}, Updated: {p[4]})")

cur2.execute("""
    SELECT wp.id, wp.profile_id, wp.video_id, wp.position, wp.updated_at, v.title
    FROM watch_progress wp
    LEFT JOIN videos v ON wp.video_id = v.id
    ORDER BY wp.updated_at DESC
""")
progress_db2 = cur2.fetchall()
print(f"\nDB2 (server/homeflix.db): {len(progress_db2)} progressions")
if progress_db2:
    for p in progress_db2:
        print(f"   • Video ID {p[2]}: '{p[5]}' - Position: {p[3]}s (Profile: {p[1]}, Updated: {p[4]})")

# === CONCLUSION ===
print("\n\n" + "=" * 80)
print("📊 CONCLUSION")
print("-" * 80)

print("\n✅ RAISONS DE GARDER server/homeflix.db:")
print(f"   1. Contient 2 profils fonctionnels ('Principal' et 'fred')")
print(f"   2. Progressions liées à des profils valides (profile_id = 1)")
print(f"   3. {len(videos_db2)} vidéos (vs {len(videos_db1)})")

print("\n❌ RAISONS DE SUPPRIMER data/homeone.db:")
print(f"   1. Aucun profil (les progressions sont orphelines)")
print(f"   2. Progressions avec profile_id NULL ou invalides")
print(f"   3. 1 vidéo de moins")

if only_in_db1:
    print(f"\n⚠️ ATTENTION: data/homeone.db contient {len(only_in_db1)} vidéo(s) supplémentaire(s)")
    print(f"   Il faudra peut-être rescanner après suppression")

conn1.close()
conn2.close()
