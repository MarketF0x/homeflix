# Amélioration de la sélection automatique TMDB

## 🎯 Objectif

Le bouton "Re-scanner avec TMDB" fait maintenant **exactement** ce que vous faisiez manuellement :
1. Rechercher le film sur TMDB avec le nom
2. **Sélectionner automatiquement le MEILLEUR résultat** (titre exact + année)
3. Afficher l'URL TMDB dans les logs
4. Enrichir avec toutes les métadonnées

## ✨ Améliorations apportées

### 1. Algorithme de scoring amélioré

**Avant** :
- Popularité : max +2 points
- Année exacte : +5 points
- Type média : +3 points (film)
- **Total max : ~10 points**

**Maintenant** :
- **Titre exact** : +10 points ⭐ (NOUVEAU!)
- **Année exacte** : +10 points ⭐ (doublé!)
- Titre partiel : +5 points
- Année proche (±1 an) : +5 points
- Type média : +3 points (film)
- Popularité : max +3 points
- **Total max : ~31 points**

### 2. Logs détaillés

Maintenant vous verrez dans les logs serveur :

```
📊 5 résultats trouvés sur TMDB pour 'The Matrix'
🏆 Top 3 résultats TMDB :
   1. [movie] The Matrix (1999) - Score: 28.4
      📎 https://www.themoviedb.org/movie/603
   2. [tv] The Matrix Trilogy (2021) - Score: 15.2
      📎 https://www.themoviedb.org/tv/12345
   3. [movie] The Matrix Reloaded (2003) - Score: 12.8
      📎 https://www.themoviedb.org/movie/604
✅ Film sélectionné (score 28.4): The Matrix
   🔗 URL TMDB: https://www.themoviedb.org/movie/603
```

### 3. Détection intelligente

L'algorithme privilégie maintenant :
1. **Correspondance EXACTE du titre** (priorité absolue)
2. **Année EXACTE** (priorité absolue)
3. Titre partiel (si exact pas trouvé)
4. Année proche ±1 an
5. Type de média (film > série)
6. Popularité

## 🧪 Comment tester

### Test 1 : Film avec nom exact et année

1. Trouvez un film avec un titre propre (ex: "The Matrix" 1999)
2. Ouvrez VideoDetail → Modifier → Re-scanner avec TMDB
3. **Regardez les logs serveur**
4. Vous devriez voir :
   - Le TOP 3 des résultats avec leurs URLs
   - Le film avec titre exact ET année exacte aura le score le plus élevé
   - L'URL TMDB du film sélectionné

### Test 2 : Film avec titre imparfait

1. Film avec titre type "The Dark Knight 2008 1080p"
2. Modifiez le titre en "The Dark Knight"
3. Re-scanner avec TMDB
4. **Logs attendus** :
   ```
   🔍 Recherche TMDb: 'The Dark Knight' (2008) [titre BDD - manuel ou nettoyé]
   📊 8 résultats trouvés sur TMDB
   🏆 Top 3 résultats TMDB :
      1. [movie] The Dark Knight (2008) - Score: 28.x
         📎 https://www.themoviedb.org/movie/155
   ✅ Film sélectionné: The Dark Knight
   ```

### Test 3 : Vérifier la sélection

Si vous voyez dans les logs que le **mauvais film** est sélectionné :

1. Regardez le TOP 3 affiché
2. Vérifiez les scores de chaque résultat
3. Le bon film devrait avoir :
   - Titre exact : +10
   - Année exacte : +10
   - Type film : +3
   - **Total : ~23+ points minimum**

## 📊 Exemples de scoring

### Exemple 1 : Correspondance parfaite
```
Recherche : "Inception" (2010)
Résultat 1 : "Inception" (2010) [movie]
  - Titre exact: +10
  - Année exacte: +10
  - Type film: +3
  - Popularité: +2.5
  = Score: 25.5 ⭐
```

### Exemple 2 : Année différente
```
Recherche : "Inception" (2010)
Résultat 2 : "Inception" (2014) [tv]
  - Titre exact: +10
  - Année différente: 0
  - Type série: +2
  - Popularité: +1.2
  = Score: 13.2
```

### Exemple 3 : Titre partiel
```
Recherche : "Matrix" (1999)
Résultat 3 : "The Matrix Reloaded" (2003) [movie]
  - Titre partiel: +5
  - Année proche: +5
  - Type film: +3
  - Popularité: +2.8
  = Score: 15.8
```

## 🔍 Comprendre les logs

### Symboles utilisés
- 📊 = Nombre de résultats trouvés
- 🏆 = Top 3 des meilleurs résultats
- 📎 = URL TMDB du résultat
- ✅ = Film finalement sélectionné
- 🔗 = URL TMDB finale
- ⚠️ = Avertissement (ex: aucun résultat)
- ❌ = Erreur

### Informations affichées
```
[movie] = Type de média (movie/tv)
(1999) = Année du film
Score: 28.4 = Points calculés par l'algorithme
```

## 💡 Conseils

### Si le mauvais film est sélectionné

1. **Vérifiez le titre** :
   - Est-ce que le titre en BDD correspond EXACTEMENT au titre TMDB?
   - Exemple : "The Matrix" ✅ vs "Matrix" ❌

2. **Vérifiez l'année** :
   - L'année est-elle correcte dans votre base de données?
   - TMDB privilégie la correspondance exacte de l'année

3. **Utilisez l'URL manuelle** :
   - Copiez l'URL du bon film depuis les logs TOP 3
   - Collez-la dans le champ "URL TMDB" et enrichissez

4. **Simplifiez le titre** :
   - Retirez les articles ("The", "Le", "La")
   - Essayez juste le nom principal
   - Exemple : "Dark Knight" au lieu de "The Dark Knight"

## 🎬 Workflow complet

```
1. Nom de fichier détecté : "The.Matrix.1999.1080p.mkv"
   ↓
2. Nettoyage automatique : "the matrix" (1999)
   ↓
3. Recherche TMDB avec "the matrix" + année 1999
   ↓
4. TMDB retourne 5 résultats
   ↓
5. Algorithme calcule les scores :
   - The Matrix (1999) = 28.4 points ⭐
   - The Matrix Reloaded (2003) = 15.8 points
   - Matrix (2018) = 13.2 points
   ↓
6. Sélection automatique du meilleur (28.4)
   ↓
7. Enrichissement avec URL : themoviedb.org/movie/603
   ↓
8. ✅ Métadonnées complètes récupérées
```

## 📝 Fichier modifié

- **`server/core/metadata_enricher.py`** (lignes 71-147)
  - Algorithme de scoring amélioré
  - Logs détaillés avec TOP 3
  - Affichage des URLs TMDB

## ✅ Avantages

- ✅ Sélection automatique du BON film (titre + année)
- ✅ Logs détaillés pour comprendre la sélection
- ✅ URLs TMDB affichées pour vérification
- ✅ Possibilité de copier l'URL du TOP 3 si besoin
- ✅ Correspondance exacte privilégiée sur la popularité

## 🚀 Prochaine étape

Si vous voyez dans les logs que le **bon film est dans le TOP 3** mais pas sélectionné en #1, dites-moi et j'ajusterai encore l'algorithme de scoring !
