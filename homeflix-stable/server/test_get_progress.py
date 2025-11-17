"""Test direct de l'endpoint GET /progress"""
import requests

API = "http://127.0.0.1:8000/api"

# 1. Sauvegarder une progression
print("1️⃣ Sauvegarde progression...")
response = requests.post(
    f"{API}/progress",
    json={"id": 1114, "position": 150, "profile_id": 1}
)
print(f"   POST /progress -> {response.status_code}: {response.json()}")

# 2. Récupérer via GET
print("\n2️⃣ Récupération via GET...")
response = requests.get(f"{API}/progress/1114?profile_id=1")
print(f"   GET /progress/1114?profile_id=1 -> {response.status_code}")
print(f"   Réponse: {response.json()}")

# 3. Vérifier dans la DB
print("\n3️⃣ Vérification dans la base de données...")
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("""
    SELECT id, profile_id, video_id, position, updated_at
    FROM watch_progress
    WHERE video_id = 1114 AND profile_id = 1
""")
row = cursor.fetchone()

if row:
    print(f"   ✅ Trouvé dans la DB:")
    print(f"      ID: {row[0]}")
    print(f"      Profile: {row[1]}")
    print(f"      Video: {row[2]}")
    print(f"      Position: {row[3]}")
    print(f"      Updated: {row[4]}")
else:
    print("   ❌ Aucune entrée trouvée")

# Nettoyer
cursor.execute("DELETE FROM watch_progress WHERE video_id = 1114")
conn.commit()
conn.close()
print("\n✅ Nettoyé")
