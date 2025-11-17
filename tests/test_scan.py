"""Test du scan complet avec détection automatique."""
import sys
sys.path.insert(0, 'server')

from core.scanner import scan_all
from core.config_manager import load_settings

print("🔍 Test du scan complet avec détection automatique...\n")

settings = load_settings()
print(f"📁 Répertoires configurés avant: {settings.video_directories}")

print("\n🚀 Lancement du scan...")
stats = scan_all(auto_detect=True)

print(f"\n📊 Résultats:")
print(f"   - Nouvelles vidéos indexées: {stats['indexed']}")
print(f"   - Vidéos supprimées: {stats['removed']}")
print(f"   - Total en base: {stats['total']}")

# Recharger les settings pour voir les changements
settings = load_settings()
print(f"\n📁 Répertoires configurés après: {settings.video_directories}")
