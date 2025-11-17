"""Test simple de la logique de copie"""
from pathlib import Path

# Simuler le payload
payload = {
    "id": 743,
    "copy_poster": r"C:\Users\fparo\Desktop\homeflix\data\thumbs\Kaamelott S01E078 Le Discobole.mkv.jpg"
}

print(f"🧪 Test de la condition")
print(f"'copy_poster' in payload: {'copy_poster' in payload}")
print(f"payload['copy_poster']: {payload['copy_poster']}")
print(f"bool(payload['copy_poster']): {bool(payload['copy_poster'])}")
print()

if "copy_poster" in payload and payload["copy_poster"]:
    print("✅ Condition TRUE - on devrait entrer dans le bloc")
    source_path = Path(payload["copy_poster"])
    print(f"📂 Source path: {source_path}")
    print(f"📂 Existe: {source_path.exists()}")
else:
    print("❌ Condition FALSE - on n'entre PAS dans le bloc")
