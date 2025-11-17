"""Test de copie d'affiche"""
import requests
import json

# Configuration
API_URL = "http://localhost:8000"
VIDEO_ID = 743  # ID de "Kaamelott S02E094 Le Tourment II"
SOURCE_POSTER = r"C:\Users\fparo\Desktop\homeflix\data\thumbs\Kaamelott S01E078 Le Discobole.mkv.jpg"

print(f"🧪 Test de copie d'affiche")
print(f"📹 Vidéo ID: {VIDEO_ID}")
print(f"🖼️ Source: {SOURCE_POSTER}")
print()

# Faire la requête
payload = {
    "id": VIDEO_ID,
    "copy_poster": SOURCE_POSTER
}

print(f"📤 Envoi de la requête...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        f"{API_URL}/api/video/update",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📥 Réponse serveur:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    if response.ok:
        data = response.json()
        print(f"✅ Succès!")
        print(f"Données: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erreur!")
        print(f"Contenu: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
