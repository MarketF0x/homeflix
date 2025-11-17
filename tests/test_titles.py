#!/usr/bin/env python3
"""Test des fonctions de titre"""

import sys
sys.path.insert(0, 'server')

from core.title_utils import extract_base_title, extract_collection_info

tests = [
    '7 jours pas plus',
    'Bad Boys II',
    'Matrix 2',
    'Alien: Covenant',
    'John Wick Chapitre 3',
    'Scream',
    'Scream 2',
    'Avatar',
    'Avatar 2',
    'Le Cinquième Élément',
    '300',
    '2012',
    'Inception',
    'Interstellar',
    'Fast & Furious 7',
    'Mission Impossible 2',
]

print('Test extract_base_title et extract_collection_info:')
print('-' * 100)
print(f'{"Titre original":40} | {"extract_base_title":30} | {"Collection":20} | Episode')
print('-' * 100)

for t in tests:
    base = extract_base_title(t)
    info = extract_collection_info(t)
    coll = info['collection'] or '-'
    ep = info['episode'] if info['episode'] else '-'
    print(f'{t:40} | {base:30} | {coll:20} | {ep}')
