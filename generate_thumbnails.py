#!/usr/bin/env python3
"""
Script standalone pour générer les miniatures manquantes
Fonctionne sans avoir besoin du serveur FastAPI
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from server.core.db import get_session
from server.core.models import Video
from server.core.thumbnails import ensure_thumbnail_sync, thumb_path_for

def main():
    print("\n" + "="*70)
    print("  🎬 Génération des miniatures manquantes - Mode Standalone")
    print("="*70)
    print("\n⚠️  Ce processus peut prendre 10-30 minutes selon le nombre de vidéos\n")
    
    stats = {
        "total": 0,
        "missing": 0,
        "generated": 0,
        "failed": 0,
        "skipped": 0
    }
    
    try:
        with get_session() as s:
            videos = s.query(Video).all()
            stats["total"] = len(videos)
            
            print(f"📊 Total de vidéos: {stats['total']}\n")
            
            for i, v in enumerate(videos, 1):
                try:
                    vpath = Path(v.path)
                    
                    # Vérifier si le fichier existe
                    if not vpath.exists():
                        stats["skipped"] += 1
                        continue
                    
                    # Vérifier si la miniature existe
                    tpath = thumb_path_for(vpath)
                    if tpath.exists():
                        stats["skipped"] += 1
                        continue
                    
                    stats["missing"] += 1
                    
                    # Afficher progression
                    print(f"[{i}/{stats['total']}] {v.title[:60]}...")
                    
                    # Générer la miniature
                    ok = ensure_thumbnail_sync(str(vpath), force=True)
                    
                    if ok:
                        stats["generated"] += 1
                        print(f"         ✅ Générée\n")
                    else:
                        stats["failed"] += 1
                        print(f"         ❌ Échec\n")
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interruption par l'utilisateur")
                    break
                except Exception as e:
                    stats["failed"] += 1
                    print(f"         ❌ Erreur: {e}\n")
        
        # Résumé final
        print("\n" + "="*70)
        print("  ✅ GÉNÉRATION TERMINÉE")
        print("="*70)
        print(f"📊 Total de vidéos:        {stats['total']}")
        print(f"⏭️  Déjà existantes:        {stats['skipped']}")
        print(f"🔍 Miniatures manquantes:  {stats['missing']}")
        print(f"✅ Générées avec succès:   {stats['generated']}")
        print(f"❌ Échecs:                 {stats['failed']}")
        
        if stats['generated'] > 0:
            success_rate = (stats['generated'] / stats['missing']) * 100
            print(f"📈 Taux de réussite:       {success_rate:.1f}%")
        
        print("="*70 + "\n")
        
        if stats['generated'] > 0:
            print("🎉 Miniatures générées ! Relancez HomeOne pour les voir.\n")
        
        return 0 if stats['failed'] == 0 else 1
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
