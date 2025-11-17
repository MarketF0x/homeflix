"""Vérifier l'état actuel de la base de données"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "homeflix.db"
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print("📊 État actuel de watch_progress")
print("=" * 80)

cursor.execute("""
    SELECT wp.id, wp.profile_id, wp.video_id, wp.position, wp.updated_at,
           p.name as profile_name
    FROM watch_progress wp
    LEFT JOIN profiles p ON wp.profile_id = p.id
    ORDER BY wp.updated_at DESC
""")

rows = cursor.fetchall()

if not rows:
    print("⚠️  Aucune progression enregistrée")
    print("\nLe serveur doit être redémarré pour que les sauvegardes fonctionnent.")
else:
    print(f"✅ {len(rows)} progression(s) trouvée(s):\n")
    
    # Grouper par profil
    by_profile = {}
    for row in rows:
        profile_id = row[1]
        profile_name = row[5]
        if profile_id not in by_profile:
            by_profile[profile_id] = []
        by_profile[profile_id].append(row)
    
    for profile_id, entries in by_profile.items():
        profile_name = entries[0][5]
        print(f"👤 Profil: {profile_name} (ID: {profile_id})")
        print(f"   Nombre de vidéos en reprise: {len(entries)}")
        
        if len(entries) > 10:
            print(f"   ⚠️  PROBLÈME: {len(entries)} vidéos (max 10) !")
        
        print(f"\n   {'#':<3} {'Vidéo ID':<10} {'Position':<12} {'Dernière mise à jour':<20}")
        print(f"   {'-'*3} {'-'*10} {'-'*12} {'-'*20}")
        
        for idx, row in enumerate(entries, 1):
            video_id = row[2]
            position = row[3]
            updated_at = row[4]
            
            # Calculer le temps écoulé
            try:
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                elapsed = datetime.now() - dt.replace(tzinfo=None)
                
                if elapsed.days > 0:
                    age = f"{elapsed.days}j"
                elif elapsed.seconds > 3600:
                    age = f"{elapsed.seconds // 3600}h"
                elif elapsed.seconds > 60:
                    age = f"{elapsed.seconds // 60}min"
                else:
                    age = f"{elapsed.seconds}s"
            except:
                age = "?"
            
            marker = "🔴" if idx > 10 else "🟢"
            print(f"   {marker} {idx:<3} {video_id:<10} {position//60}min {position%60}s    il y a {age}")
        
        print()

conn.close()

print("=" * 80)
print("\n💡 Légende:")
print("   🟢 = Dans le top 10 (doit apparaître)")
print("   🔴 = Au-delà de 10 (doit être supprimé)")
print("\nSi vous voyez des 🔴:")
print("   → Ces entrées devraient être supprimées à la prochaine sauvegarde")
print("   → Vérifiez que le serveur a été redémarré")
