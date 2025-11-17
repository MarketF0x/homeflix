"""
Supprimer toutes les vidéos de server/homeflix.db et refaire un scan complet
"""
import sqlite3
from pathlib import Path

db_path = Path("server/homeflix.db")

print("🗑️ Nettoyage de la base de données...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Compter avant
cur.execute("SELECT COUNT(*) FROM videos")
count_before = cur.fetchone()[0]
print(f"   Vidéos avant: {count_before}")

# Supprimer toutes les vidéos (mais garder les profils et progressions)
cur.execute("DELETE FROM videos")
conn.commit()

# Compter après
cur.execute("SELECT COUNT(*) FROM videos")
count_after = cur.fetchone()[0]
print(f"   Vidéos après: {count_after}")

# Vérifier les profils (ne doivent pas être touchés)
cur.execute("SELECT COUNT(*) FROM profiles")
profiles = cur.fetchone()[0]
print(f"   Profils: {profiles} (conservés)")

# Vérifier les progressions (attention, elles pointent vers des video_id qui n'existent plus)
cur.execute("SELECT COUNT(*) FROM watch_progress")
progress = cur.fetchone()[0]
print(f"   Progressions: {progress} (seront invalides jusqu'au rescan)")

conn.close()

print("\n✅ Base nettoyée - Prêt pour le rescan complet")
print("   Les progressions seront réassociées si les vidéos ont le même ID après rescan")
