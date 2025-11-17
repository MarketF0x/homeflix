"""Test de la détection automatique des répertoires vidéo."""
import sys
sys.path.insert(0, 'server')

from core.scanner import auto_detect_video_directories

print("🔍 Démarrage de la détection automatique...")
try:
    dirs = auto_detect_video_directories(max_depth=2, min_videos=3)
    print(f"\n✅ Détection terminée!")
    print(f"📁 {len(dirs)} répertoire(s) trouvé(s):")
    for d in dirs:
        print(f"   - {d}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
