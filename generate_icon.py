#!/usr/bin/env python3
"""
Générateur d'icône HomeOne
---------------------------
Crée une icône .ico avec:
- Pellicule de film vue de côté (orange doré)
- Silhouette de maison découpée au centre
"""

from PIL import Image, ImageDraw
import sys
from pathlib import Path

def create_homeone_icon(output_path, size=256):
    """Génère l'icône HomeOne."""
    
    # Couleurs
    orange_gold = (255, 165, 0)      # Orange doré principal
    dark_gold = (204, 132, 0)        # Ombres dorées
    black = (0, 0, 0)                # Silhouette maison
    film_holes = (50, 50, 50)        # Perforations pellicule
    
    # Crée l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dimensions de la pellicule
    film_width = int(size * 0.75)
    film_height = int(size * 0.85)
    film_x = (size - film_width) // 2
    film_y = (size - film_height) // 2
    
    # Dessine le rectangle principal de la pellicule (orange doré)
    draw.rounded_rectangle(
        [film_x, film_y, film_x + film_width, film_y + film_height],
        radius=int(size * 0.05),
        fill=orange_gold,
        outline=dark_gold,
        width=int(size * 0.02)
    )
    
    # Ajoute l'effet 3D / ombre sur le côté droit
    shadow_offset = int(size * 0.03)
    draw.rounded_rectangle(
        [film_x + shadow_offset, film_y + shadow_offset, 
         film_x + film_width + shadow_offset, film_y + film_height + shadow_offset],
        radius=int(size * 0.05),
        fill=(dark_gold[0]//2, dark_gold[1]//2, dark_gold[2]//2, 100)
    )
    
    # Redessine la pellicule par-dessus
    draw.rounded_rectangle(
        [film_x, film_y, film_x + film_width, film_y + film_height],
        radius=int(size * 0.05),
        fill=orange_gold,
        outline=dark_gold,
        width=int(size * 0.02)
    )
    
    # Dessine les perforations de pellicule (haut et bas)
    hole_size = int(size * 0.04)
    hole_spacing = int(size * 0.08)
    margin = int(size * 0.08)
    
    # Perforations en haut
    for i in range(5):
        x = film_x + margin + i * hole_spacing
        y_top = film_y + int(size * 0.03)
        y_bottom = film_y + film_height - int(size * 0.03) - hole_size
        
        # Trou en haut
        draw.ellipse([x, y_top, x + hole_size, y_top + hole_size], fill=film_holes)
        # Trou en bas
        draw.ellipse([x, y_bottom, x + hole_size, y_bottom + hole_size], fill=film_holes)
    
    # Dessine la silhouette de maison au centre (découpée)
    center_x = size // 2
    center_y = size // 2
    house_size = int(size * 0.35)
    
    # Points du toit (triangle)
    roof_points = [
        (center_x, center_y - house_size // 2),                    # Sommet
        (center_x - house_size // 2, center_y),                    # Gauche
        (center_x + house_size // 2, center_y)                     # Droite
    ]
    
    # Base de la maison (rectangle)
    house_base = [
        center_x - house_size // 2,
        center_y,
        center_x + house_size // 2,
        center_y + house_size // 2
    ]
    
    # Cheminée
    chimney_width = int(house_size * 0.15)
    chimney_height = int(house_size * 0.25)
    chimney = [
        center_x + house_size // 4,
        center_y - house_size // 3,
        center_x + house_size // 4 + chimney_width,
        center_y - house_size // 3 + chimney_height
    ]
    
    # Porte
    door_width = int(house_size * 0.25)
    door_height = int(house_size * 0.35)
    door = [
        center_x - door_width // 2,
        center_y + house_size // 2 - door_height,
        center_x + door_width // 2,
        center_y + house_size // 2
    ]
    
    # Dessine la silhouette (noir opaque pour effet de découpe)
    draw.polygon(roof_points, fill=black)
    draw.rectangle(house_base, fill=black)
    draw.rectangle(chimney, fill=black)
    draw.rectangle(door, fill=black)
    
    return img


def main():
    """Point d'entrée principal."""
    # Détermine le chemin de sortie
    script_dir = Path(__file__).parent
    output_path = script_dir / "homeone.ico"
    
    print("🎨 Génération de l'icône HomeOne...")
    print(f"📁 Emplacement: {output_path}")
    
    # Crée l'icône en plusieurs tailles pour Windows
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        print(f"   ⚙️  Génération {size}x{size}...")
        img = create_homeone_icon(output_path, size)
        images.append(img)
    
    # Sauvegarde au format .ico (multi-résolution)
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    
    print(f"✅ Icône créée avec succès: {output_path.name}")
    print("")
    print("💡 Prochaine étape:")
    print("   Exécutez 'create_shortcut.ps1' pour créer le raccourci avec la nouvelle icône.")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        sys.exit(1)
