"""
Tester la sauvegarde de progression avec différents profils
"""
import requests
import sqlite3

print("🧪 TEST DE PROGRESSION PAR PROFIL")
print("=" * 80)

# 1. Récupérer les profils
print("\n1️⃣ Récupération des profils...")
response = requests.get("http://127.0.0.1:8000/api/profiles")
profiles = response.json()["profiles"]
print(f"   Profils disponibles: {[p['name'] for p in profiles]}")

# 2. Tester sauvegarde pour chaque profil
for profile in profiles:
    print(f"\n2️⃣ Test pour profil '{profile['name']}' (ID: {profile['id']})...")
    
    # Sauvegarder une progression
    response = requests.post(
        "http://127.0.0.1:8000/api/progress",
        json={
            "id": 1062,  # Futurama S11E13
            "position": 100 + profile['id'] * 10,  # Position différente par profil
            "profile_id": profile['id']
        }
    )
    
    if response.status_code == 200:
        print(f"   ✅ Sauvegarde OK: {response.json()}")
    else:
        print(f"   ❌ Erreur: {response.status_code} - {response.text}")

# 3. Vérifier dans la base de données
print(f"\n3️⃣ Vérification dans la base de données...")
conn = sqlite3.connect('server/homeflix.db')
cur = conn.cursor()

cur.execute("""
    SELECT wp.profile_id, p.name, wp.video_id, v.title, wp.position, wp.updated_at
    FROM watch_progress wp
    LEFT JOIN profiles p ON wp.profile_id = p.id
    LEFT JOIN videos v ON wp.video_id = v.id
    ORDER BY wp.updated_at DESC
    LIMIT 10
""")

rows = cur.fetchall()
print(f"   Progressions enregistrées:")
for row in rows:
    print(f"   • Profil {row[0]} ({row[1]}): Video {row[2]} '{row[3]}' - {row[4]}s - {row[5]}")

conn.close()

# 4. Tester l'API categories pour chaque profil
print(f"\n4️⃣ Test API /categories par profil...")
for profile in profiles:
    response = requests.get(
        f"http://127.0.0.1:8000/api/categories?mode=mixed&profile_id={profile['id']}"
    )
    data = response.json()
    to_resume = data.get("to_resume", [])
    print(f"   Profil '{profile['name']}': {len(to_resume)} vidéo(s) dans to_resume")
    if to_resume:
        for v in to_resume[:3]:
            print(f"      • {v['title']}")

print("\n" + "=" * 80)
print("✅ Test terminé")
