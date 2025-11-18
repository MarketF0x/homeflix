## 🎯 v1.3.0 - Amélioration majeure du système TMDB

### ✨ Nouvelles fonctionnalités

- **Algorithme de sélection intelligent** : Scoring amélioré pour choisir automatiquement le meilleur résultat TMDB
  - Titre exact : +10 points (vs 0 avant)
  - Année exacte : +10 points (vs 5 avant)
  - Correspondance partielle titre : +5 points (nouveau)
  - Popularité : jusqu'à +3 points (vs 2 avant)

- **Logs détaillés avec TOP 3** : Affichage des 3 meilleurs résultats avec :
  - Score de chaque résultat
  - URL TMDB directe (ex: https://www.themoviedb.org/movie/603)
  - Film sélectionné clairement identifié

- **URLs TMDB** : Chaque recherche affiche maintenant l'URL du film sélectionné pour vérification

### 🐛 Corrections importantes

- **Bug critique re-scan** : Le bouton 're-scan TMDB' écrasait les métadonnées existantes avec des chaînes vides
  - Avant : Sauvegardait ALL les champs (genre, overview, cast) même vides
  - Maintenant : Ne sauvegarde que titre/année si modifiés
  - Résultat : Les métadonnées existantes sont préservées

- **Préservation des données** : Les métadonnées déjà enrichies ne sont plus effacées lors d'un re-scan

### 📚 Documentation ajoutée

- `AMELIORATION_SELECTION_TMDB.md` - Guide complet avec exemples de scoring
- `CORRECTION_BUG_RESCAN_TMDB.md` - Analyse détaillée du bug et sa correction
- `TEST_RESCAN_TMDB.md` - Guide de test complet avec cas d'usage

### 🔧 Fichiers modifiés

- `server/core/metadata_enricher.py` - Algorithme de scoring + logs détaillés
- `client/src/VideoDetail.jsx` - Logique de sauvegarde améliorée
- `server/api/videos.py` - Support collection_name

### 🎬 Impact utilisateur

Le système TMDB fonctionne maintenant comme attendu :
1. Sélection automatique du meilleur résultat (priorité titre exact + année)
2. Logs clairs montrant les choix effectués avec URLs
3. Plus de perte de métadonnées lors des re-scans
4. Titre manuel respecté et utilisé pour la recherche TMDB
