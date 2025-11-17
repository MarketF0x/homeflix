"""
Script de migration pour remplacer print() par logger dans le code serveur
"""
import re
from pathlib import Path

# Mapping des emojis/patterns vers les niveaux de log
LOG_LEVEL_PATTERNS = {
    'ERROR': [r'❌', r'✗', r'ERROR', r'Erreur', r'Failed', r'échec'],
    'WARNING': [r'⚠️', r'⏳', r'WARNING', r'warn', r'skip'],
    'INFO': [r'✅', r'✓', r'🎬', r'📥', r'📋', r'💾', r'🔍', r'INFO'],
    'DEBUG': [r'DEBUG', r'debug']
}

def get_log_level(print_content):
    """Détermine le niveau de log basé sur le contenu du print"""
    for level, patterns in LOG_LEVEL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, print_content, re.IGNORECASE):
                return level.lower()
    return 'info'  # Par défaut

def migrate_print_to_logger(file_path: Path):
    """Remplace les print() par logger dans un fichier"""
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Vérifier si le logger est déjà importé
    has_logger_import = 'from core.logger import logger' in content
    
    # Pattern pour capturer print(f"...") et print("...")
    print_pattern = r'print\((f?["\'])(.+?)["\']\)'
    
    def replace_print(match):
        is_fstring = match.group(1) == 'f"' or match.group(1) == "f'"
        quote = '"' if '"' in match.group(1) else "'"
        message = match.group(2)
        level = get_log_level(message)
        
        # Nettoyer les emojis principaux qui sont redondants
        message = re.sub(r'(❌|✅|⚠️|🔍|📥|📋|💾|🎬)\s*', '', message)
        
        if is_fstring:
            return f'logger.{level}(f{quote}{message}{quote})'
        else:
            return f'logger.{level}({quote}{message}{quote})'
    
    # Remplacer les print()
    content = re.sub(print_pattern, replace_print, content)
    
    # Ajouter l'import du logger si nécessaire et s'il y a eu des changements
    if not has_logger_import and content != original:
        # Trouver la section des imports
        import_section = re.search(r'(from .+ import .+\n)+', content)
        if import_section:
            last_import_pos = import_section.end()
            content = (content[:last_import_pos] + 
                      'from core.logger import logger, log_exception\n' +
                      content[last_import_pos:])
    
    # Sauvegarder seulement si modifié
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    """Migrer tous les fichiers Python du serveur"""
    server_dir = Path(__file__).parent.parent / 'server'
    
    python_files = list(server_dir.rglob('*.py'))
    # Exclure les tests et migrations
    python_files = [f for f in python_files if 'test' not in str(f) and 'migrate' not in f.name]
    
    print(f"🔍 Analyse de {len(python_files)} fichiers Python...")
    
    modified = []
    for py_file in python_files:
        if migrate_print_to_logger(py_file):
            modified.append(py_file.relative_to(server_dir))
            print(f"  ✅ {py_file.relative_to(server_dir)}")
    
    print(f"\n✅ Migration terminée : {len(modified)} fichiers modifiés")
    for f in modified:
        print(f"  - {f}")

if __name__ == '__main__':
    main()
