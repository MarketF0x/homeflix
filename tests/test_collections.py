#!/usr/bin/env python3
"""Test de l'extraction du titre de base pour les collections."""

import sys
sys.path.insert(0, 'server')

from core.title_utils import extract_base_title

# Tests avec différents titres
test_cases = [
    # Sagas réelles
    ("Alien", "Alien"),
    ("Alien: Romulus", "Alien"),
    ("Alien 3", "Alien"),
    ("Bad Boys", "Bad Boys"),
    ("Bad Boys II", "Bad Boys"),
    ("Bad Boys for Life", "Bad Boys"),
    ("Matrix", "Matrix"),
    ("Matrix Reloaded", "Matrix"),
    ("Matrix Revolutions", "Matrix"),
    ("Iron Man", "Iron Man"),
    ("Iron Man 2", "Iron Man"),
    ("Iron Man 3", "Iron Man"),
    
    # Films uniques (ne doivent PAS être modifiés)
    ("Avatar", "Avatar"),
    ("Avatar: The Way of Water", "Avatar"),
    ("Inception", "Inception"),
    ("Interstellar", "Interstellar"),
    
    # Harry Potter
    ("Harry Potter et la Chambre des Secrets", "Harry Potter"),
    ("Harry Potter et le Prisonnier d'Azkaban", "Harry Potter"),
]

print("=" * 70)
print("TEST D'EXTRACTION DU TITRE DE BASE POUR COLLECTIONS")
print("=" * 70)

for original, expected in test_cases:
    result = extract_base_title(original)
    status = "✅" if result == expected else "❌"
    print(f"{status} {original:45} -> {result:20} (attendu: {expected})")

print("=" * 70)
