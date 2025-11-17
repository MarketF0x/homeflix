"""
Script de nettoyage des noms de fichiers vidéo.
Utilise le module file_cleaner pour renommer les fichiers et améliorer la reconnaissance TMDB.

Usage:
    python clean_filenames.py                    # Aperçu des changements
    python clean_filenames.py --preview          # Aperçu détaillé (20 premiers)
    python clean_filenames.py --preview 50       # Aperçu de 50 fichiers
    python clean_filenames.py --dry-run          # Simulation complète
    python clean_filenames.py --execute          # Exécution réelle (ATTENTION!)
    python clean_filenames.py --test             # Tests sur des exemples
"""

import sys
import argparse
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from core.file_cleaner import (
    clean_database_filenames,
    preview_cleaning,
    test_cleaning,
    clean_filename
)


def main():
    parser = argparse.ArgumentParser(
        description="🧹 Nettoie les noms de fichiers vidéo pour améliorer la reconnaissance TMDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python clean_filenames.py                     # Aperçu rapide
  python clean_filenames.py --preview 50        # Aperçu de 50 fichiers
  python clean_filenames.py --dry-run           # Simulation complète
  python clean_filenames.py --execute           # ⚠️ Renommage réel
  python clean_filenames.py --test              # Tests unitaires
  
Que fait ce script ?
  - Supprime les résolutions (1080p, 720p, 4K, etc.)
  - Supprime les codecs (x264, x265, HEVC, etc.)
  - Supprime les sources (BluRay, WEB-DL, etc.)
  - Supprime les tags audio (DTS, AC3, AAC, etc.)
  - Supprime les langues (FRENCH, VOSTFR, MULTI, etc.)
  - Supprime les teams de release (YIFY, SPARKS, etc.)
  - Conserve les années et numéros d'épisodes
  
Exemple de transformation:
  "The.Matrix.1999.1080p.BluRay.x264.DTS-SPARKS.mkv"
  → "The Matrix 1999.mkv"
        """
    )
    
    parser.add_argument(
        '--preview',
        type=int,
        nargs='?',
        const=20,
        metavar='N',
        help='Affiche un aperçu de N fichiers (défaut: 20)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulation complète (aucune modification réelle)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='⚠️ EXÉCUTION RÉELLE - Renomme les fichiers sur le disque'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Lance les tests sur des exemples de noms de fichiers'
    )
    
    parser.add_argument(
        '--no-update-titles',
        action='store_true',
        help='Ne pas mettre à jour les titres dans la base de données'
    )
    
    args = parser.parse_args()
    
    # Mode test
    if args.test:
        test_cleaning()
        return
    
    # Mode aperçu
    if args.preview is not None:
        preview_cleaning(limit=args.preview)
        return
    
    # Mode dry-run
    if args.dry_run:
        print("\n⚠️ MODE SIMULATION - Aucune modification ne sera effectuée\n")
        clean_database_filenames(
            dry_run=True,
            update_titles=not args.no_update_titles
        )
        return
    
    # Mode exécution réelle
    if args.execute:
        print("\n" + "="*60)
        print("⚠️  ATTENTION - MODE EXÉCUTION RÉELLE")
        print("="*60)
        print("Cette opération va:")
        print("  1. Renommer les fichiers vidéo sur le disque")
        print("  2. Mettre à jour la base de données")
        print("="*60)
        
        response = input("\nÊtes-vous sûr de vouloir continuer ? (oui/non): ").strip().lower()
        
        if response not in ['oui', 'yes', 'o', 'y']:
            print("\n❌ Opération annulée.\n")
            return
        
        print("\n🚀 Démarrage du nettoyage...\n")
        clean_database_filenames(
            dry_run=False,
            update_titles=not args.no_update_titles
        )
        print("\n✅ Nettoyage terminé avec succès!\n")
        return
    
    # Par défaut : aperçu rapide
    print("\nℹ️  Mode aperçu par défaut. Utilisez --help pour plus d'options.\n")
    preview_cleaning(limit=10)
    print("\n💡 Conseil: Utilisez --dry-run pour voir tous les changements sans les appliquer")
    print("💡 Conseil: Utilisez --execute pour appliquer réellement les changements\n")


if __name__ == "__main__":
    main()
