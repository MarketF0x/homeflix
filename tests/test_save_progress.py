"""
Test de sauvegarde de progression manuellement
"""
import requests

# Test avec une vraie vidéo de la base
print("🧪 Test de sauvegarde de progression")
print("=" * 60)

# 1. Récupérer une vidéo du carousel
print("\n1️⃣ Récupération d'une vidéo du carousel...")
response = requests.get("http://127.0.0.1:8000/api/categories?mode=mixed&profile_id=1")
data = response.json()

if not data.get("carousel"):
    print("❌ Aucune vidéo dans le carousel")
    exit(1)

video = data["carousel"][0]
print(f"✅ Vidéo sélectionnée: {video['title']} (ID: {video['id']})")

# 2. Sauvegarder une progression
print("\n2️⃣ Sauvegarde de la progression (position 120s)...")
response = requests.post(
    "http://127.0.0.1:8000/api/progress",
    json={
        "id": video["id"],
        "position": 120,
        "profile_id": 1
    }
)

if response.status_code == 200:
    print(f"✅ Réponse: {response.json()}")
else:
    print(f"❌ Erreur: {response.status_code} - {response.text}")
    exit(1)

# 3. Vérifier que c'est bien sauvegardé
print("\n3️⃣ Vérification dans la base de données...")
import sqlite3
conn = sqlite3.connect('server/homeflix.db')
cur = conn.cursor()
cur.execute("SELECT * FROM watch_progress WHERE video_id = ? AND profile_id = ?", (video["id"], 1))
row = cur.fetchone()
conn.close()

if row:
    print(f"✅ Entrée trouvée en base: position={row[3]}s, updated_at={row[4]}")
else:
    print("❌ Aucune entrée en base !")
    exit(1)

# 4. Vérifier que l'API /categories renvoie bien la vidéo dans to_resume
print("\n4️⃣ Vérification de l'API /categories...")
response = requests.get("http://127.0.0.1:8000/api/categories?mode=mixed&profile_id=1")
data = response.json()

if data.get("to_resume"):
    print(f"✅ {len(data['to_resume'])} vidéo(s) dans to_resume:")
    for v in data["to_resume"]:
        print(f"   • {v['title']} (ID: {v['id']})")
else:
    print("❌ Aucune vidéo dans to_resume")
    print(f"Réponse complète: {data.keys()}")

print("\n" + "=" * 60)
print("✅ Test terminé !")
