"""
Script de test pour vérifier la sauvegarde de progression par profil
"""
import requests
import json

API = "http://127.0.0.1:8000/api"

print("🧪 Test de la sauvegarde de progression par profil")
print("=" * 80)

# 1. Récupérer les profils
print("\n1️⃣ Récupération des profils...")
response = requests.get(f"{API}/profiles")
data = response.json()

if not data.get("ok"):
    print("❌ Erreur récupération profils")
    exit(1)

profiles = data["profiles"]
print(f"✅ {len(profiles)} profil(s) trouvé(s):")
for p in profiles:
    print(f"   • {p['name']} (ID: {p['id']}) {'[PRINCIPAL]' if p.get('is_main') else ''}")

main_profile = next((p for p in profiles if p.get("is_main")), profiles[0])
print(f"\n📌 Utilisation du profil: {main_profile['name']} (ID: {main_profile['id']})")

# 2. Récupérer une vidéo pour tester
print("\n2️⃣ Récupération des catégories...")
response = requests.get(f"{API}/categories?mode=mixed&profile_id={main_profile['id']}")
categories = response.json()

if not categories.get("carousel") or len(categories["carousel"]) == 0:
    print("❌ Aucune vidéo disponible pour tester")
    exit(1)

test_video = categories["carousel"][0]
print(f"✅ Vidéo de test: {test_video['title']} (ID: {test_video['id']})")

# 3. Sauvegarder une progression
print("\n3️⃣ Sauvegarde d'une progression de 120 secondes...")
response = requests.post(
    f"{API}/progress",
    headers={"Content-Type": "application/json"},
    json={
        "id": test_video["id"],
        "position": 120,
        "profile_id": main_profile["id"]
    }
)

if response.status_code == 200:
    print("✅ Progression sauvegardée avec succès")
else:
    print(f"❌ Erreur {response.status_code}: {response.text}")
    exit(1)

# 4. Vérifier que la progression est bien récupérée
print("\n4️⃣ Récupération de la progression...")
response = requests.get(f"{API}/progress/{test_video['id']}?profile_id={main_profile['id']}")
data = response.json()

if data.get("position") == 120:
    print(f"✅ Progression récupérée: {data['position']} secondes")
else:
    print(f"❌ Progression incorrecte: {data.get('position')} au lieu de 120")

# 5. Vérifier que la vidéo apparaît dans "À reprendre"
print("\n5️⃣ Vérification de la liste 'À reprendre'...")
response = requests.get(f"{API}/categories?mode=mixed&profile_id={main_profile['id']}")
categories = response.json()

to_resume = categories.get("to_resume", [])
if any(v["id"] == test_video["id"] for v in to_resume):
    print(f"✅ Vidéo '{test_video['title']}' présente dans 'À reprendre'")
    print(f"   Liste: {len(to_resume)} vidéo(s) en attente")
else:
    print(f"❌ Vidéo NON présente dans 'À reprendre'")
    print(f"   Liste actuelle: {[v['title'] for v in to_resume]}")

# 6. Nettoyer (supprimer la progression de test)
print("\n6️⃣ Nettoyage de la progression de test...")
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute(
    "DELETE FROM watch_progress WHERE profile_id = ? AND video_id = ?",
    (main_profile["id"], test_video["id"])
)
conn.commit()
conn.close()
print("✅ Progression supprimée")

print("\n" + "=" * 80)
print("✅ Test terminé avec succès!")
