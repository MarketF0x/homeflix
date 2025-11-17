"""
Test pour vérifier que la liste À reprendre se met à jour correctement
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Configuration
APP_ROOT = Path(__file__).parent.parent
DB_PATH = APP_ROOT / "server" / "homeflix.db"

def show_watch_progress():
    """Affiche la table watch_progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📊 WATCH_PROGRESS TABLE")
    print("=" * 80)
    
    cursor.execute("""
        SELECT wp.id, wp.profile_id, wp.video_id, wp.position, wp.updated_at,
               v.title, p.name as profile_name
        FROM watch_progress wp
        LEFT JOIN videos v ON wp.video_id = v.id
        LEFT JOIN profiles p ON wp.profile_id = p.id
        ORDER BY wp.updated_at DESC
        LIMIT 15
    """)
    
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            id_, profile_id, video_id, position, updated_at, title, profile_name = row
            print(f"  • [{profile_name or 'N/A'}] {title or f'Video {video_id}'}")
            print(f"    Position: {position}s | Updated: {updated_at}")
    else:
        print("  ❌ Aucune entrée")
    
    conn.close()

def simulate_api_call():
    """Simule un appel à l'API /categories pour voir ce que le frontend reçoit"""
    print("\n🌐 SIMULATION API /categories")
    print("=" * 80)
    
    import requests
    try:
        # Test avec profil Principal (id=1)
        response = requests.get("http://127.0.0.1:8000/api/categories?mode=mixed&profile_id=1")
        data = response.json()
        
        if data.get("to_resume"):
            print(f"✅ {len(data['to_resume'])} vidéo(s) dans to_resume:")
            for video in data["to_resume"]:
                print(f"  • {video['title']} (ID: {video['id']})")
        else:
            print("❌ Aucune vidéo dans to_resume")
            
        print(f"\n📦 Autres catégories:")
        print(f"  • Carousel: {len(data.get('carousel', []))} vidéos")
        print(f"  • Watched: {len(data.get('watched', []))} vidéos")
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")

if __name__ == "__main__":
    print("🔍 TEST DE RAFRAÎCHISSEMENT UI")
    print("=" * 80)
    
    show_watch_progress()
    simulate_api_call()
    
    print("\n" + "=" * 80)
    print("📝 Instructions:")
    print("  1. Ouvrez le navigateur (F12 pour la console)")
    print("  2. Lancez une vidéo et attendez 10 secondes")
    print("  3. Fermez le lecteur")
    print("  4. Vérifiez la console pour voir les logs de sauvegarde")
    print("  5. Relancez ce script pour voir si la DB est mise à jour")
