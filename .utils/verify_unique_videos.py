"""
Vérifier si les vidéos uniques de data/homeone.db existent sur le disque
"""
import sqlite3
from pathlib import Path

db1_path = Path("data/homeone.db")
db2_path = Path("server/homeflix.db")

conn1 = sqlite3.connect(db1_path)
cur1 = conn1.cursor()

conn2 = sqlite3.connect(db2_path)
cur2 = conn2.cursor()

# Vidéos dans chaque base
cur1.execute("SELECT id, path FROM videos ORDER BY id")
videos_db1 = {row[0]: row[1] for row in cur1.fetchall()}

cur2.execute("SELECT id, path FROM videos ORDER BY id")
videos_db2 = {row[0]: row[1] for row in cur2.fetchall()}

# Vidéos uniquement dans DB1
only_in_db1 = set(videos_db1.keys()) - set(videos_db2.keys())

print(f"🔍 Vérification des {len(only_in_db1)} vidéos uniques de data/homeone.db")
print("=" * 80)

exist_count = 0
missing_count = 0

for vid_id in sorted(list(only_in_db1)[:10]):  # Vérifier les 10 premières
    path = videos_db1[vid_id]
    exists = Path(path).exists()
    
    if exists:
        exist_count += 1
        print(f"✅ EXISTE : {path}")
    else:
        missing_count += 1
        print(f"❌ MANQUANT : {path}")

print(f"\n📊 Sur 10 vidéos testées:")
print(f"   ✅ Existent: {exist_count}")
print(f"   ❌ Manquantes: {missing_count}")

if missing_count == 10:
    print(f"\n💡 Toutes les vidéos uniques de data/homeone.db n'existent plus sur le disque")
    print(f"   → C'est une vieille base avec des entrées obsolètes")
elif exist_count > 0:
    print(f"\n⚠️ Certaines vidéos existent encore - Il faut investiguer pourquoi le scan ne les a pas trouvées")

conn1.close()
conn2.close()
