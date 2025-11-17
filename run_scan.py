import sys
sys.path.insert(0, 'server')
from core.scanner import scan_all

print('🔍 Scan des vidéos en cours...')
result = scan_all()
print(f'✅ Scan terminé: {len(result.get("videos", []))} vidéos trouvées')
