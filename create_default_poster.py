#!/usr/bin/env python3
"""
Crée une image par défaut pour les miniatures manquantes
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_default_poster():
    """Crée une affiche par défaut style minimaliste."""
    # Dimensions standard d'affiche
    width, height = 500, 750
    
    # Couleurs
    bg_color = (20, 20, 25)      # Fond sombre
    accent = (255, 107, 53)       # Orange HomeOne
    text_color = (200, 200, 200)  # Gris clair
    
    # Créer l'image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cadre
    margin = 40
    draw.rectangle(
        [margin, margin, width-margin, height-margin],
        outline=accent,
        width=4
    )
    
    # Icône de pellicule au centre
    icon_size = 120
    icon_x = (width - icon_size) // 2
    icon_y = (height - icon_size) // 2 - 40
    
    # Dessiner la pellicule
    film_color = (80, 80, 90)
    draw.rectangle(
        [icon_x, icon_y, icon_x + icon_size, icon_y + icon_size],
        fill=film_color,
        outline=accent,
        width=3
    )
    
    # Trous de pellicule
    hole_size = 12
    for i in range(3):
        x = icon_x - 20
        y = icon_y + 20 + i * 40
        draw.ellipse([x, y, x + hole_size, y + hole_size], fill=bg_color)
        
        x = icon_x + icon_size + 8
        draw.ellipse([x, y, x + hole_size, y + hole_size], fill=bg_color)
    
    # Texte "Pas d'aperçu"
    try:
        # Essayer d'utiliser une police système
        font = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fallback sur la police par défaut
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Titre
    text = "🎬"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = icon_y + icon_size + 40
    draw.text((text_x, text_y), text, fill=accent, font=font)
    
    # Sous-titre
    subtitle = "Miniature indisponible"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    sub_width = bbox[2] - bbox[0]
    sub_x = (width - sub_width) // 2
    sub_y = text_y + 60
    draw.text((sub_x, sub_y), subtitle, fill=text_color, font=font_small)
    
    # Sauvegarder
    output_path = Path(__file__).parent / "server" / "static" / "default_poster.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=85)
    print(f"✅ Image par défaut créée : {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_default_poster()
