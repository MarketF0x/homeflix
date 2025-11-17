"""
Optimisation intelligente des images pour Homeflix
- Conversion JPG → WebP (meilleure compression)
- Compression agressive sans perte de qualité visuelle
- Redimensionnement intelligent des thumbnails
"""
import os
import sys
from pathlib import Path
from PIL import Image
import shutil

def optimize_image(input_path, output_path=None, quality=85, max_width=400):
    """
    Optimise une image en la convertissant en WebP et en la redimensionnant si nécessaire
    
    Args:
        input_path: Chemin de l'image source
        output_path: Chemin de sortie (None = même nom avec .webp)
        quality: Qualité WebP (0-100, 85 recommandé)
        max_width: Largeur max pour thumbnails
    
    Returns:
        Tuple (success, old_size, new_size, compression_ratio)
    """
    try:
        img = Image.open(input_path)
        original_size = os.path.getsize(input_path)
        
        # Convertir en RGB si nécessaire (WebP ne supporte pas RGBA pour certaines config)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (0, 0, 0))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionner si trop large (thumbnails)
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"  📐 Redimensionné: {img.width}x{img.height}")
        
        # Déterminer le chemin de sortie
        if output_path is None:
            output_path = Path(input_path).with_suffix('.webp')
        else:
            output_path = Path(output_path)
        
        # Sauvegarder en WebP avec optimisation
        img.save(
            output_path,
            'WebP',
            quality=quality,
            method=6,  # Meilleure compression (plus lent mais optimal)
            lossless=False
        )
        
        new_size = os.path.getsize(output_path)
        compression_ratio = (1 - new_size / original_size) * 100
        
        return True, original_size, new_size, compression_ratio
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False, 0, 0, 0


def optimize_directory(directory, quality=85, max_width=400, delete_original=False):
    """
    Optimise toutes les images JPG d'un dossier
    
    Args:
        directory: Dossier à traiter
        quality: Qualité WebP
        max_width: Largeur max
        delete_original: Supprimer les JPG originaux après conversion
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"❌ Dossier introuvable: {directory}")
        return
    
    jpg_files = list(directory.glob('**/*.jpg')) + list(directory.glob('**/*.jpeg'))
    
    if not jpg_files:
        print(f"ℹ️ Aucune image JPG trouvée dans {directory}")
        return
    
    print(f"\n🔍 Trouvé {len(jpg_files)} images à optimiser")
    print(f"📁 Dossier: {directory}")
    print(f"⚙️  Qualité: {quality}, Largeur max: {max_width}px\n")
    
    total_original = 0
    total_optimized = 0
    success_count = 0
    
    for i, jpg_file in enumerate(jpg_files, 1):
        print(f"[{i}/{len(jpg_files)}] {jpg_file.name}...")
        
        success, old_size, new_size, ratio = optimize_image(
            jpg_file,
            quality=quality,
            max_width=max_width
        )
        
        if success:
            total_original += old_size
            total_optimized += new_size
            success_count += 1
            
            print(f"  ✅ {old_size/1024:.1f} KB → {new_size/1024:.1f} KB ({ratio:.1f}% compression)")
            
            # Supprimer l'original si demandé
            if delete_original:
                jpg_file.unlink()
                print(f"  🗑️  Original supprimé")
        
        # Afficher progression tous les 100 fichiers
        if i % 100 == 0:
            current_ratio = (1 - total_optimized / total_original) * 100 if total_original > 0 else 0
            print(f"\n📊 Progression: {i}/{len(jpg_files)} ({current_ratio:.1f}% compression globale)\n")
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE L'OPTIMISATION")
    print("="*60)
    print(f"✅ Images traitées: {success_count}/{len(jpg_files)}")
    print(f"📦 Taille originale: {total_original/1024/1024:.2f} MB")
    print(f"📦 Taille optimisée: {total_optimized/1024/1024:.2f} MB")
    
    if total_original > 0:
        saved = total_original - total_optimized
        ratio = (saved / total_original) * 100
        print(f"💾 Espace économisé: {saved/1024/1024:.2f} MB ({ratio:.1f}%)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Chemins par défaut
    ELECTRON_THUMBS = Path(__file__).parent / "electron" / "dist" / "win-unpacked" / "resources" / "data" / "thumbs"
    DATA_THUMBS = Path(__file__).parent / "data" / "thumbs"
    DATA_POSTERS = Path(__file__).parent / "data" / "posters"
    
    print("🎨 OPTIMISATION DES IMAGES HOMEFLIX")
    print("=" * 60)
    
    # Détecter quel dossier existe
    if ELECTRON_THUMBS.exists():
        print("📍 Mode: Application Electron empaquetée")
        target = ELECTRON_THUMBS
    elif DATA_THUMBS.exists():
        print("📍 Mode: Développement")
        target = DATA_THUMBS
    else:
        print("❌ Aucun dossier de miniatures trouvé!")
        sys.exit(1)
    
    print(f"\n⚠️  ATTENTION: Cette opération va:")
    print(f"   1. Convertir toutes les images JPG en WebP")
    print(f"   2. Redimensionner si > 400px de large")
    print(f"   3. Économiser ~60-80% d'espace disque")
    print(f"\n📁 Dossier cible: {target}")
    
    response = input("\n❓ Continuer? (oui/non): ").strip().lower()
    
    if response in ['oui', 'o', 'yes', 'y']:
        # Optimiser avec qualité 85 (excellent rapport qualité/taille)
        optimize_directory(
            target,
            quality=85,
            max_width=400,
            delete_original=False  # Garder les originaux pour le moment
        )
        
        print("\n✅ Optimisation terminée!")
        print("\nℹ️  Les fichiers WebP sont créés à côté des JPG.")
        print("ℹ️  Pour activer WebP, mettez à jour le code serveur:")
        print("   - Modifier core/thumbnails.py pour servir .webp")
        print("   - Tester l'affichage dans le navigateur")
        print("   - Une fois validé, supprimer les JPG manuellement")
    else:
        print("\n❌ Optimisation annulée")
