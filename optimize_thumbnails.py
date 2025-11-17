"""
Optimisation JPG sans conversion (compatibilité maximale)
Utilise PIL/Pillow pour une compression optimale des JPG existants
"""
import os
from pathlib import Path
from PIL import Image
import shutil

def optimize_jpg_inplace(image_path, quality=85, max_width=300):
    """
    Optimise un JPG sans changer le format
    - Compression avec qualité optimale
    - Redimensionnement intelligent
    - Suppression métadonnées EXIF
    
    Returns: (success, old_size, new_size, saved_mb)
    """
    try:
        original_size = os.path.getsize(image_path)
        
        # Ouvrir l'image
        img = Image.open(image_path)
        
        # Redimensionner si nécessaire (thumbnails n'ont pas besoin d'être énormes)
        resized = False
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            resized = True
        
        # Convertir en RGB si nécessaire
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Créer un fichier temporaire
        temp_path = image_path.with_suffix('.tmp.jpg')
        
        # Sauvegarder avec optimisation maximale
        img.save(
            temp_path,
            'JPEG',
            quality=quality,
            optimize=True,  # Optimisation Huffman
            progressive=True,  # JPEG progressif (charge plus vite)
            subsampling=0  # Meilleure qualité chrominance
        )
        
        new_size = os.path.getsize(temp_path)
        
        # Remplacer l'original seulement si c'est plus petit
        if new_size < original_size:
            shutil.move(str(temp_path), str(image_path))
            saved = original_size - new_size
            return True, original_size, new_size, saved, resized
        else:
            # Pas d'amélioration, garder l'original
            temp_path.unlink()
            return False, original_size, original_size, 0, False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False, 0, 0, 0, False


def optimize_directory(directory, quality=85, max_width=300, dry_run=False):
    """
    Optimise tous les JPG d'un dossier
    
    Args:
        directory: Dossier à traiter
        quality: Qualité JPEG (75-95, 85 recommandé)
        max_width: Largeur max pour thumbnails (300px suffit)
        dry_run: Mode simulation (ne modifie pas les fichiers)
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"❌ Dossier introuvable: {directory}")
        return
    
    jpg_files = list(directory.glob('*.jpg')) + list(directory.glob('*.jpeg'))
    
    if not jpg_files:
        print(f"ℹ️  Aucune image JPG trouvée dans {directory}")
        return
    
    print(f"\n🔍 {len(jpg_files)} images JPG trouvées")
    print(f"📁 {directory}")
    print(f"⚙️  Qualité: {quality}, Largeur max: {max_width}px")
    
    if dry_run:
        print("🧪 MODE SIMULATION (aucune modification)")
    
    print()
    
    total_original = 0
    total_optimized = 0
    optimized_count = 0
    resized_count = 0
    
    for i, jpg_file in enumerate(jpg_files, 1):
        if i % 50 == 0 or i == 1:
            print(f"\n[{i}/{len(jpg_files)}]", end=" ")
        
        if not dry_run:
            success, old_size, new_size, saved, resized = optimize_jpg_inplace(
                jpg_file,
                quality=quality,
                max_width=max_width
            )
        else:
            # Mode simulation
            img = Image.open(jpg_file)
            old_size = os.path.getsize(jpg_file)
            success = True
            new_size = old_size * 0.5  # Estimation
            saved = old_size - new_size
            resized = img.width > max_width
        
        total_original += old_size
        
        if success and saved > 0:
            total_optimized += new_size
            optimized_count += 1
            if resized:
                resized_count += 1
            
            # Afficher seulement les économies significatives (>10%)
            if saved / old_size > 0.1:
                print(f"✓", end="")
        else:
            total_optimized += old_size
            print(f"·", end="")
        
        # Afficher stats tous les 50
        if i % 50 == 0:
            current_saved = total_original - total_optimized
            ratio = (current_saved / total_original * 100) if total_original > 0 else 0
            print(f" ({ratio:.1f}% économisé)")
    
    print("\n")
    
    # Résumé
    total_saved = total_original - total_optimized
    ratio = (total_saved / total_original * 100) if total_original > 0 else 0
    
    print("=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"📁 Images analysées: {len(jpg_files)}")
    print(f"✅ Images optimisées: {optimized_count} ({optimized_count/len(jpg_files)*100:.1f}%)")
    print(f"📐 Images redimensionnées: {resized_count}")
    print(f"📦 Taille originale: {total_original/1024/1024:.2f} MB")
    print(f"📦 Taille finale: {total_optimized/1024/1024:.2f} MB")
    print(f"💾 Espace économisé: {total_saved/1024/1024:.2f} MB ({ratio:.1f}%)")
    
    if dry_run:
        print("\n⚠️  Mode simulation - Aucune modification effectuée")
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Détecter le dossier de thumbnails
    paths_to_check = [
        Path(__file__).parent / "electron" / "dist" / "win-unpacked" / "resources" / "data" / "thumbs",
        Path(__file__).parent / "data" / "thumbs",
        Path("data/thumbs"),
    ]
    
    target = None
    for path in paths_to_check:
        if path.exists():
            target = path
            break
    
    if not target:
        print("❌ Dossier de miniatures introuvable!")
        print("Chemins vérifiés:")
        for p in paths_to_check:
            print(f"  - {p}")
        sys.exit(1)
    
    print("🎨 OPTIMISATION JPEG HOMEFLIX")
    print("=" * 70)
    print(f"\n📍 Dossier: {target}")
    
    # Compter les fichiers
    jpg_count = len(list(target.glob('*.jpg'))) + len(list(target.glob('*.jpeg')))
    
    if jpg_count == 0:
        print("ℹ️  Aucune image à optimiser")
        sys.exit(0)
    
    print(f"🖼️  Images trouvées: {jpg_count}")
    print(f"\n⚙️  Paramètres:")
    print(f"   • Qualité: 85 (excellent)")
    print(f"   • Largeur max: 300px (suffisant pour thumbnails)")
    print(f"   • Optimisation: Huffman + Progressive")
    print(f"\n💡 Gain estimé: 50-70% de réduction de taille")
    print(f"   (~{jpg_count * 56 * 0.6 / 1024:.1f} MB économisés)")
    
    # Mode interactif
    if "--yes" not in sys.argv:
        print("\n❓ Options:")
        print("   1. Simulation (voir l'impact sans modifier)")
        print("   2. Optimiser maintenant")
        print("   3. Annuler")
        
        choice = input("\nVotre choix (1/2/3): ").strip()
        
        if choice == "1":
            print("\n🧪 Lancement de la simulation...\n")
            optimize_directory(target, quality=85, max_width=300, dry_run=True)
        elif choice == "2":
            print("\n🚀 Lancement de l'optimisation...\n")
            # Backup prompt
            print("⚠️  Voulez-vous créer une sauvegarde avant? (recommandé)")
            backup = input("Sauvegarder? (o/n): ").strip().lower()
            
            if backup in ['o', 'oui', 'y', 'yes']:
                backup_dir = target.parent / "thumbs_backup"
                if not backup_dir.exists():
                    print(f"💾 Création de sauvegarde dans {backup_dir}...")
                    shutil.copytree(target, backup_dir)
                    print("✅ Sauvegarde créée")
                else:
                    print("ℹ️  Sauvegarde existante trouvée")
            
            optimize_directory(target, quality=85, max_width=300, dry_run=False)
            
            print("\n✅ Optimisation terminée!")
            print("\n🔄 Prochaines étapes:")
            print("   1. Reconstruire le client: cd client && npm run build")
            print("   2. Copier vers Electron")
            print("   3. Tester l'application")
        else:
            print("\n❌ Annulé")
    else:
        # Mode automatique (--yes)
        optimize_directory(target, quality=85, max_width=300, dry_run=False)
