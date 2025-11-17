"""
Script pour remplacer tous les emojis Unicode par des caractères ASCII dans main.py
Compatible Windows PowerShell
"""
import re

# Mapping des emojis vers ASCII
EMOJI_MAP = {
    "🌐": "[HTTP]",
    "💡": "[INFO]",
    "ℹ️": "[INFO]",
    "⚠️": "[WARN]",
    "🎬": "[VIDEO]",
    "✨": "[AUTO]",
    "🔍": "[SCAN]",
    "📁": "[FILE]",
    "🚀": "[START]",
    "✅": "[OK]",
    "❌": "[ERROR]",
    "🔄": "[SYNC]",
    "📊": "[STATS]",
    "🎯": "[TARGET]",
    "🔧": "[CONFIG]",
    "⏰": "[TIME]",
    "📝": "[NOTE]",
    "🎥": "[MEDIA]",
    "🖼️": "[IMAGE]",
    "⚙️": "[PROCESS]",
}

# Mapping des accents pour Windows
ACCENT_MAP = {
    "é": "e",
    "è": "e",
    "ê": "e",
    "à": "a",
    "ù": "u",
    "ô": "o",
    "î": "i",
    "ç": "c",
    "É": "E",
    "È": "E",
    "Ê": "E",
    "À": "A",
    "Ù": "U",
    "Ô": "O",
    "Î": "I",
    "Ç": "C",
    "—": "-",
}

def fix_file(filepath):
    """Remplace les emojis et accents dans un fichier"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remplacer les emojis
    for emoji, replacement in EMOJI_MAP.items():
        content = content.replace(emoji, replacement)
    
    # Remplacer les accents dans les logger.info/warning/error uniquement
    def replace_accents_in_logger(match):
        line = match.group(0)
        for accent, replacement in ACCENT_MAP.items():
            line = line.replace(accent, replacement)
        return line
    
    content = re.sub(
        r'logger\.(info|warning|error|debug)\([^)]+\)',
        replace_accents_in_logger,
        content
    )
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fichier corrigé: {filepath}")
        return True
    else:
        print(f"- Aucun changement nécessaire: {filepath}")
        return False

if __name__ == "__main__":
    fixed = fix_file("server/main.py")
    if fixed:
        print("\n[OK] Tous les emojis et accents ont été remplacés!")
        print("[INFO] Le serveur devrait maintenant s'afficher correctement dans PowerShell")
    else:
        print("\n[INFO] Aucune modification nécessaire")
