"""
Afficher exactement ce que le frontend reçoit
"""
import requests
import json

print("🔍 SIMULATION FRONTEND - Appel API /categories")
print("=" * 80)

response = requests.get("http://127.0.0.1:8000/api/categories?mode=mixed&profile_id=1")
data = response.json()

print(f"\n📦 Réponse API (status {response.status_code}):")
print(json.dumps({
    "ok": data.get("ok"),
    "carousel_count": len(data.get("carousel", [])),
    "to_resume_count": len(data.get("to_resume", [])),
    "watched_count": len(data.get("watched", [])),
    "by_year_count": len(data.get("by_year", {})),
    "by_genre_count": len(data.get("by_genre", {}))
}, indent=2))

if data.get("to_resume"):
    print(f"\n✅ TO_RESUME ({len(data['to_resume'])} vidéos):")
    for video in data["to_resume"]:
        print(f"   • {video['title']} (ID: {video['id']})")
else:
    print("\n❌ TO_RESUME est vide ou manquant")
    print(f"   Clés présentes: {list(data.keys())}")

print("\n" + "=" * 80)
print("💡 Si to_resume est vide alors que la DB contient des données:")
print("   1. Vérifiez que profile_id=1 dans l'URL")
print("   2. Rafraîchissez le navigateur (F5)")
print("   3. Vérifiez la console du navigateur pour les erreurs")
