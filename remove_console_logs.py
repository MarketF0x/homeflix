#!/usr/bin/env python3
"""
Script pour supprimer TOUS les console.log/warn/error/info du VideoPlayer.jsx
"""
import re

file_path = r"client\src\VideoPlayer.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns à supprimer
patterns = [
    # console.log/warn/error sur une seule ligne
    r'^\s*console\.(log|warn|error|info)\([^;]*\);?\s*\n',
    
    # console.log multi-lignes avec console.error('...', e)
    r'^\s*console\.(log|warn|error|info)\([^)]*\)\s*;\s*\n',
    
    # console dans un catch: .catch(e => console.error(...))
    r'\.catch\([^=]*=>\s*console\.(log|warn|error|info)\([^)]*\)\)',
    
    # console dans un .then: .then(() => console.log(...))
    r'\.then\([^=]*=>\s*console\.(log|warn|error|info)\([^)]*\)\)',
]

# Compter avant
console_count_before = len(re.findall(r'console\.(log|warn|error|info)', content))

# Supprimer les patterns simples (lignes complètes)
content = re.sub(
    r'^\s*console\.(log|warn|error|info)\([^;]*\);?\s*$',
    '',
    content,
    flags=re.MULTILINE
)

# Remplacer les .catch(err => console.error(...)) par .catch(() => {})
content = re.sub(
    r'\.catch\([^)]*\s*=>\s*console\.(log|warn|error|info)\([^)]*\)\)',
    '.catch(() => {})',
    content
)

# Remplacer les .then(() => console.log(...)) par .then(() => {})
content = re.sub(
    r'\.then\([^)]*\s*=>\s*console\.(log|warn|error|info)\([^)]*\)\)',
    '.then(() => {})',
    content
)

# Supprimer les lignes vides multiples
content = re.sub(r'\n\n\n+', '\n\n', content)

# Compter après
console_count_after = len(re.findall(r'console\.(log|warn|error|info)', content))

# Sauvegarder
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Nettoyage terminé!")
print(f"   Console logs avant: {console_count_before}")
print(f"   Console logs après: {console_count_after}")
print(f"   Supprimés: {console_count_before - console_count_after}")
