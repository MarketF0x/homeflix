"""Test rapide de l'endpoint /api/progress après redémarrage du serveur"""
import requests
import time

API = "http://127.0.0.1:8000/api"

print("🧪 Test de l'endpoint /api/progress")
print("=" * 70)

# Vérifier que le serveur répond
print("\n1️⃣ Vérification que le serveur est accessible...")
try:
    response = requests.get(f"{API}/profiles", timeout=2)
    print(f"   ✅ Serveur OK (status {response.status_code})")
except requests.exceptions.ConnectionError:
    print("   ❌ SERVEUR NON ACCESSIBLE")
    print("   → Démarrez le serveur : .\\start.ps1")
    exit(1)
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT")
    exit(1)

# Test POST /api/progress avec un video_id fictif
print("\n2️⃣ Test POST /api/progress (sauvegarde)...")
response = requests.post(
    f"{API}/progress",
    json={"id": 99999, "position": 60, "profile_id": 1},
    timeout=5
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ SUCCESS: {response.json()}")
elif response.status_code == 404:
    print(f"   ❌ ERROR 404: {response.text}")
    print("   → Le serveur utilise encore l'ancien code")
    print("   → REDÉMARREZ LE SERVEUR !")
else:
    print(f"   ⚠️  Status inattendu: {response.text}")

# Test GET /api/progress
print("\n3️⃣ Test GET /api/progress/{video_id}...")
response = requests.get(f"{API}/progress/99999?profile_id=1", timeout=5)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ SUCCESS: {data}")
    if data.get("position") == 60:
        print("   ✅ Position correcte (60s)")
    else:
        print(f"   ⚠️  Position: {data.get('position')} (attendu: 60)")
elif response.status_code == 404:
    print(f"   ❌ ERROR 404")
    print("   → Endpoint GET non trouvé")
else:
    print(f"   Status: {response.text}")

# Nettoyage
print("\n4️⃣ Nettoyage...")
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "homeflix.db"
if DB_PATH.exists():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watch_progress WHERE video_id = 99999")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"   ✅ {deleted} entrée(s) de test supprimée(s)")

print("\n" + "=" * 70)
print("✅ Test terminé")
print("\nSi vous voyez des erreurs 404:")
print("  → REDÉMARREZ LE SERVEUR pour charger le nouveau code")
print("  → Arrêt : Ctrl+C dans le terminal du serveur")
print("  → Démarrage : .\\start.ps1")
