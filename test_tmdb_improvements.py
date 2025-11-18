"""
Script de test pour vérifier les améliorations TMDB
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / "server"))

from core.metadata_enricher import clean_title_and_year

def test_title_cleaning():
    """Test du nettoyage de titre"""
    
    test_cases = [
        ("The.Matrix.1999.1080p.BluRay.x264.mkv", "the matrix", 1999),
        ("Inception (2010) [1080p]", "inception", 2010),
        ("Avatar.2009.REMASTERED.1080p.BluRay.x264", "avatar", 2009),
        ("The Matrix", "the matrix", None),
        ("Film-Title_2023", "film title", 2023),
    ]
    
    print("🧪 Test de nettoyage de titre\n")
    print("-" * 80)
    
    for filename, expected_title, expected_year in test_cases:
        title, year = clean_title_and_year(filename)
        
        status = "✅" if title == expected_title and year == expected_year else "❌"
        
        print(f"{status} {filename}")
        print(f"   Attendu  : '{expected_title}' ({expected_year})")
        print(f"   Obtenu   : '{title}' ({year})")
        print()

if __name__ == "__main__":
    test_title_cleaning()
    
    print("\n" + "=" * 80)
    print("📋 Rappel des améliorations :")
    print("=" * 80)
    print()
    print("1. ✅ Le titre en BDD a PRIORITÉ sur le nom de fichier")
    print("2. ✅ Toutes les métadonnées sont mises à jour (pas de champs vides)")
    print("3. ✅ Le poster est téléchargé automatiquement")
    print("4. ✅ La collection est récupérée depuis TMDb")
    print("5. ✅ Mise à jour locale sans rechargement de page")
    print()
    print("Pour tester dans l'application :")
    print("- Modifiez le nom d'un film manuellement")
    print("- Cliquez sur 'Re-scanner avec TMDB'")
    print("- Vérifiez que le nouveau nom est utilisé pour la recherche")
    print()
