from PIL import Image, ImageDraw, ImageFont
import os

# Créer une icône simple pour Homeflix
size = 512
img = Image.new('RGB', (size, size), color='#e50914')

# Dessiner un cadre
draw = ImageDraw.Draw(img)
border = 50
draw.rectangle([border, border, size-border, size-border], outline='white', width=12)

# Ajouter le texte "H"
try:
    font_large = ImageFont.truetype("arial.ttf", 200)
    font_small = ImageFont.truetype("arial.ttf", 48)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Centrer le "H"
text = "H"
bbox = draw.textbbox((0, 0), text, font=font_large)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 40

draw.text((x, y), text, fill='white', font=font_large)

# Ajouter "HOMEFLIX"
text2 = "HOMEFLIX"
bbox2 = draw.textbbox((0, 0), text2, font=font_small)
text2_width = bbox2[2] - bbox2[0]
x2 = (size - text2_width) // 2
y2 = y + text_height + 20

draw.text((x2, y2), text2, fill='white', font=font_small)

# Sauvegarder
output_path = os.path.join(os.path.dirname(__file__), 'electron', 'icon.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path)
print(f"✅ Icône créée: {output_path}")
