"""
Analyser les deux bases de données et choisir la meilleure
"""
import sqlite3
from pathlib import Path

print("🔍 ANALYSE DES BASES DE DONNÉES")
print("=" * 80)

db1_path = Path("data/homeone.db")
db2_path = Path("server/homeflix.db")

def analyze_db(db_path):
    """Analyser une base de données"""
    if not db_path.exists():
        return {"exists": False}
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    info = {"exists": True, "path": str(db_path)}
    
    try:
        # Compter les vidéos
        cur.execute("SELECT COUNT(*) FROM videos")
        info["videos"] = cur.fetchone()[0]
        
        # Compter les profils
        cur.execute("SELECT COUNT(*) FROM profiles")
        info["profiles"] = cur.fetchone()[0]
        
        # Lister les profils
        cur.execute("SELECT name, is_main FROM profiles")
        info["profile_names"] = [f"{row[0]}{' (main)' if row[1] else ''}" for row in cur.fetchall()]
        
        # Compter les progressions
        cur.execute("SELECT COUNT(*) FROM watch_progress")
        info["watch_progress"] = cur.fetchone()[0]
        
        # Taille du fichier
        info["size_mb"] = db_path.stat().st_size / (1024 * 1024)
        
    except Exception as e:
        info["error"] = str(e)
    
    conn.close()
    return info

# Analyser les deux bases
db1_info = analyze_db(db1_path)
db2_info = analyze_db(db2_path)

print("\n📊 BASE 1: data/homeone.db")
print("-" * 80)
if db1_info["exists"]:
    print(f"  ✅ Existe : Oui")
    print(f"  📹 Vidéos : {db1_info.get('videos', 'N/A')}")
    print(f"  👤 Profils : {db1_info.get('profiles', 'N/A')}")
    if db1_info.get('profile_names'):
        print(f"     → {', '.join(db1_info['profile_names'])}")
    print(f"  ⏱️ Progressions : {db1_info.get('watch_progress', 'N/A')}")
    print(f"  💾 Taille : {db1_info.get('size_mb', 0):.2f} MB")
else:
    print(f"  ❌ N'existe pas")

print("\n📊 BASE 2: server/homeflix.db")
print("-" * 80)
if db2_info["exists"]:
    print(f"  ✅ Existe : Oui")
    print(f"  📹 Vidéos : {db2_info.get('videos', 'N/A')}")
    print(f"  👤 Profils : {db2_info.get('profiles', 'N/A')}")
    if db2_info.get('profile_names'):
        print(f"     → {', '.join(db2_info['profile_names'])}")
    print(f"  ⏱️ Progressions : {db2_info.get('watch_progress', 'N/A')}")
    print(f"  💾 Taille : {db2_info.get('size_mb', 0):.2f} MB")
else:
    print(f"  ❌ N'existe pas")

# Déterminer la meilleure base
print("\n" + "=" * 80)
print("🎯 RECOMMANDATION:")
print("-" * 80)

if not db1_info["exists"] and not db2_info["exists"]:
    print("❌ Aucune base de données trouvée !")
elif not db1_info["exists"]:
    print(f"✅ Garder: server/homeflix.db (seule base existante)")
    print(f"   → {db2_info['videos']} vidéos, {db2_info['profiles']} profils")
elif not db2_info["exists"]:
    print(f"✅ Garder: data/homeone.db (seule base existante)")
    print(f"   → {db1_info['videos']} vidéos, {db1_info['profiles']} profils")
else:
    # Les deux existent - comparer
    db1_score = db1_info.get('videos', 0) + db1_info.get('profiles', 0) * 10 + db1_info.get('watch_progress', 0)
    db2_score = db2_info.get('videos', 0) + db2_info.get('profiles', 0) * 10 + db2_info.get('watch_progress', 0)
    
    if db1_score > db2_score:
        print(f"✅ GARDER: data/homeone.db (score: {db1_score})")
        print(f"   → {db1_info['videos']} vidéos, {db1_info['profiles']} profils, {db1_info['watch_progress']} progressions")
        print(f"❌ SUPPRIMER: server/homeflix.db (score: {db2_score})")
        print(f"\n💡 Action à faire:")
        print(f"   1. Utiliser data/homeone.db comme base principale")
        print(f"   2. Supprimer server/homeflix.db")
    else:
        print(f"✅ GARDER: server/homeflix.db (score: {db2_score})")
        print(f"   → {db2_info['videos']} vidéos, {db2_info['profiles']} profils, {db2_info['watch_progress']} progressions")
        print(f"❌ SUPPRIMER: data/homeone.db (score: {db1_score})")
        print(f"\n💡 Action à faire:")
        print(f"   1. Utiliser server/homeflix.db comme base principale")
        print(f"   2. Supprimer data/homeone.db")
