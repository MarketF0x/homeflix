# Améliorations du système TMDB - Novembre 2025

## 🎯 Problèmes résolus

### 1. Métadonnées vides malgré la bonne jaquette
**Avant** : Parfois la jaquette s'affichait correctement mais les métadonnées (résumé, acteurs, note) restaient vides.

**Maintenant** :
- ✅ Téléchargement automatique du poster lors de l'enrichissement
- ✅ Toutes les métadonnées sont TOUJOURS mises à jour (même si certaines existent déjà)
- ✅ Logs détaillés pour identifier les champs manquants
- ✅ Le poster est téléchargé et enregistré localement dans `data/thumbs/`
- ✅ Marqueur `.manual` créé pour indiquer que c'est un poster TMDb

### 2. Nom modifié manuellement non pris en compte pour le re-scan
**Avant** : Même après avoir modifié le nom du film manuellement, le re-scan TMDb utilisait le nom du fichier original.

**Maintenant** :
- ✅ Le titre en base de données a PRIORITÉ sur le nom du fichier
- ✅ Quand vous modifiez le nom manuellement, il est sauvegardé AVANT le re-scan
- ✅ Le re-scan TMDb utilise le nouveau nom nettoyé pour la recherche
- ✅ Mise à jour locale immédiate sans rechargement de page

## 📋 Modifications apportées

### Backend (`server/core/metadata_enricher.py`)
```python
# PRIORITÉ AU TITRE DE LA BDD (modifié manuellement ou déjà nettoyé)
if video.title and video.title.strip():
    search_title = video.title.strip()  # Utilise le titre manuel
    logger.info(f"🔍 Recherche TMDb: '{search_title}' [titre BDD - manuel ou nettoyé]")
else:
    search_title, extracted_year = clean_title_and_year(video_path.stem)
    logger.info(f"🔍 Recherche TMDb: '{search_title}' [nettoyé depuis fichier]")
```

**Téléchargement du poster** :
```python
if metadata.get("poster_path"):
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    thumb_file = thumb_path_for(Path(video.path))
    # Téléchargement et création du marqueur .manual
```

### Backend (`server/api/videos.py`)
- ✅ Ajout de `collection_name` dans les réponses API
- ✅ Gestion de la collection pour l'endpoint `/enrich-from-url`

### Frontend (`client/src/VideoDetail.jsx`)
**Fonction `handleEnrichFromTMDb()` améliorée** :
1. Sauvegarde d'abord TOUTES les modifications (titre, année, etc.)
2. Puis enrichissement TMDb avec le nouveau titre en BDD
3. Mise à jour locale immédiate (pas de rechargement complet)
4. Rechargement de l'affiche si elle a changé

**Fonction `handleSaveMetadata()` améliorée** :
- Mise à jour locale de toutes les dépendances
- Rechargement forcé de l'affiche si modifiée
- Pas de rechargement du carousel complet

## 🔄 Flux de travail amélioré

### Scénario 1 : Film avec nom de fichier mal formaté
1. **Fichier** : `The.Matrix.1999.1080p.BluRay.x264.mkv`
2. **Premier scan** : Trouve la jaquette mais nom pas parfait
3. **Modification manuelle** : Changez en "The Matrix"
4. **Clic sur "Re-scanner avec TMDB"** :
   - ✅ Sauvegarde "The Matrix" en BDD
   - ✅ Recherche TMDb avec "The Matrix"
   - ✅ Récupère TOUTES les métadonnées (résumé, acteurs, note, collection)
   - ✅ Télécharge le poster officiel
   - ✅ Mise à jour locale immédiate

### Scénario 2 : Métadonnées incomplètes
Si une vidéo a le bon poster mais manque des métadonnées :
1. Cliquez sur "Re-scanner avec TMDB"
2. ✅ Le système détecte les champs manquants dans les logs
3. ✅ Force la mise à jour de TOUS les champs
4. ✅ Télécharge le poster même s'il existe déjà

## 📊 Logs améliorés

Exemple de log détaillé :
```
🔍 Recherche TMDb: 'The Matrix' (1999) [titre BDD - manuel ou nettoyé]
📥 Téléchargement poster: https://image.tmdb.org/t/p/w500/abc123.jpg
✅ Poster téléchargé: C:\...\data\thumbs\video_123.jpg
✅ Enrichi: The Matrix (1999) - science fiction
   | Note: 8.7/10
   | Résumé: 136 caractères
   | Acteurs: Keanu Reeves, Laurence Fishburne, Carrie-...
   | Collection: The Matrix Collection #1
```

## 🐛 Bugs corrigés

1. ✅ **Métadonnées vides** : Le poster était retourné mais pas téléchargé
2. ✅ **Re-scan avec nom modifié** : Le titre manuel était écrasé par le nettoyage du fichier
3. ✅ **Rechargement complet** : Plus besoin de recharger la page pour voir les changements
4. ✅ **Collection manquante** : Maintenant récupérée et affichée correctement

## 🎨 Expérience utilisateur

- **Pas de rechargement de page** : Tout se met à jour instantanément
- **Feedback visuel** : Messages clairs à chaque étape
- **Logs détaillés** : Aide au diagnostic si problème
- **Préservation du contexte** : Le carousel ne se recharge pas

## 🔧 Fichiers modifiés

1. `server/core/metadata_enricher.py` - Logique d'enrichissement
2. `server/api/videos.py` - Endpoints API
3. `client/src/VideoDetail.jsx` - Interface utilisateur

## 📝 Notes techniques

- Le poster TMDb est téléchargé en résolution w500 (optimale)
- Un marqueur `.jpg.manual` est créé pour tracer l'origine
- La priorité est donnée au titre en BDD pour permettre les modifications manuelles
- Tous les champs sont mis à jour même s'ils existent déjà pour garantir la cohérence
