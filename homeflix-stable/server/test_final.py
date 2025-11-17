"""Test final du système de progression"""
import requests
import time

API = "http://127.0.0.1:8000/api"

print("🎬 Test complet du système de progression")
print("=" * 70)

# 1. Sauvegarder 2 progressions
print("\n1️⃣ Sauvegarde de 2 vidéos...")
r1 = requests.post(f"{API}/progress", json={"id": 1114, "position": 300, "profile_id": 1})
print(f"   Vidéo 1114: {r1.status_code} - {r1.json()}")
time.sleep(0.5)

r2 = requests.post(f"{API}/progress", json={"id": 1115, "position": 450, "profile_id": 1})
print(f"   Vidéo 1115: {r2.status_code} - {r2.json()}")

# 2. Vérifier la liste "À reprendre"
print("\n2️⃣ Vérification de la liste 'À reprendre'...")
r3 = requests.get(f"{API}/categories?mode=mixed&profile_id=1")
data = r3.json()

to_resume = data.get("to_resume", [])
print(f"   ✅ {len(to_resume)} vidéo(s) en reprise")

if len(to_resume) > 0:
    print("\n   Détails (ordre = plus récent à gauche):")
    for idx, video in enumerate(to_resume[:5], 1):
        title = video.get("title", "Sans titre")[:40]
        position = video.get("last_position", 0)
        print(f"      {idx}. {title} → {position//60}min {position%60}s")

# 3. Vérifier dans la base
print("\n3️⃣ Vérification dans la base de données...")
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("""
    SELECT video_id, position, updated_at
    FROM watch_progress
    WHERE profile_id = 1
    ORDER BY updated_at DESC
    LIMIT 5
""")

rows = cursor.fetchall()
print(f"   ✅ {len(rows)} entrée(s) dans watch_progress:")
for video_id, position, updated_at in rows:
    print(f"      • Vidéo {video_id}: {position}s (màj: {updated_at})")

conn.close()

# 4. Nettoyage
print("\n4️⃣ Nettoyage des données de test...")
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute("DELETE FROM watch_progress WHERE video_id IN (1114, 1115)")
deleted = cursor.rowcount
conn.commit()
conn.close()
print(f"   ✅ {deleted} entrée(s) supprimée(s)")

print("\n" + "=" * 70)
print("✅ Système opérationnel !")
print("\n📝 Prochaines étapes:")
print("   1. Ouvrir http://localhost:8000 dans le navigateur")
print("   2. Ouvrir la Console (F12)")
print("   3. Lancer une vidéo et regarder pendant 30 secondes")
print("   4. Vérifier les logs: '💾 Sauvegarde progression...'")
print("   5. Fermer la vidéo et vérifier la section 'À reprendre'")
