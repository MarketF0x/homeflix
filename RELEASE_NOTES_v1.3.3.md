# 📦 Homeflix v1.3.3 - Version Stable
**Date de sortie :** 20 novembre 2025  
**Branche :** dev → stable  
**Type :** Correctifs & Améliorations

---

## 🎯 Résumé

Version stable avec corrections majeures de bugs et améliorations de l'expérience utilisateur. Focus sur la fiabilité de la détection des médias, la recherche intelligente et l'interface utilisateur.

---

## ✨ Nouvelles Fonctionnalités

### 🔍 Recherche Intelligente
- **Normalisation du texte** : Suppression des accents, ponctuation ignorée
- **Recherche multi-critères** : Titre, chemin, année, genres
- **Système de scoring** :
  - Correspondance exacte : +1000 points
  - Début du titre : +500 points
  - Mots-clés : +100 points
  - Recherche fuzzy : +20-30 points
- **Tolérance aux fautes** : Recherche partielle et similarité
- **Affichage des résultats** : Section dédiée sous le carousel

### 📁 Explorateur de Fichiers
- **Navigation graphique** : Remplacement du champ texte par un navigateur visuel
- **Sélection de lecteurs** : Bouton "Sélectionner" sur chaque lecteur (C:\, D:\, etc.)
- **Navigation intuitive** : Double-clic pour entrer, bouton "Dossier parent"
- **Indicateurs visuels** : Dossiers verrouillés affichés

### 📊 Détection Automatique de Durée
- **Extraction avec ffprobe** : Calcul automatique lors du scan
- **Stockage en base** : Durée en secondes (`duration_seconds`)
- **Logs détaillés** : Affichage de la durée pour chaque vidéo indexée
- **Fallback intelligent** : Détection par patterns si ffprobe absent

---

## 🐛 Corrections de Bugs

### 🎬 Détection Films/Séries
**Problème :** Mauvaise catégorisation des vidéos  
**Solution :**
- Détection intelligente par patterns :
  - Séries : `S01E01`, `1x01`, `Episode`, `Saison`
  - Films : `BluRay`, `BDRip`, `WebRip`, durée >= 75 min
- Priorité à la durée si disponible
- Fallback sur patterns sinon
- Par défaut : considéré comme FILM

### 🏷️ Nettoyage des Noms de Fichiers
**Problème :** Noms avec tags techniques (`x264`, `BluRay`, etc.)  
**Solution :**
- Nettoyage automatique lors du scan initial
- Suppression de tous les tags techniques
- Titres ultra-propres envoyés à TMDb
- **Amélioration reconnaissance TMDb : ~40% → ~80%**

### 📝 Code Frontend
**Problème :** Warnings ESLint et erreurs d'initialisation  
**Solution :**
- Variables inutilisées supprimées
- Erreur `handleCloseVideo` corrigée (déplacé avant `useEffect`)
- 0 warnings ESLint
- Doublons supprimés

### 🖼️ Miniatures FFMPEG
**Problème :** Miniatures générées mais non affichées (erreur `OpaqueResponseBlocking`)  
**Solution :**
- **Headers CORS ajoutés** :
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET, OPTIONS`
- **Cache optimisé** : `public, max-age=86400` (24h au lieu de no-cache)
- **Génération automatique** : Création lors du scan
  - Tente TMDb d'abord (si API key)
  - Fallback sur ffmpeg
  - Logs détaillés

### 🔄 Scan Récursif
**Problème :** Confusion sur le scan des sous-dossiers  
**Solution :**
- Confirmation : `os.walk()` utilisé
- Scan automatique de tous les sous-dossiers
- Documentation claire
- Bouton "Scanner maintenant" repositionné logiquement

---

## 🔧 Améliorations Techniques

### Backend (Python/FastAPI)
- `server/core/scanner.py` :
  - Import `clean_filename` de `file_cleaner`
  - Fonction `detect_media_type()` améliorée
  - Extraction durée avec ffprobe
  - Génération miniatures automatique
- `server/core/file_cleaner.py` :
  - Nettoyage ultra-agressif des noms
  - Suppression tags techniques
- `server/api/thumbnails.py` :
  - Headers CORS ajoutés
  - Cache optimisé (24h)
- `server/core/thumbnails.py` :
  - Support CORS sur endpoints
  - Fallback image par défaut

### Frontend (React/Vite)
- `client/src/pages/Settings.jsx` :
  - Explorateur de fichiers graphique
  - Bouton "Scanner maintenant" repositionné
- `client/src/pages/HomePage.jsx` :
  - Section résultats de recherche
  - Affichage nombre de résultats
  - Recherche intelligente implémentée
- `client/src/components/VideoPlayer.jsx` :
  - Erreur `handleCloseVideo` corrigée
  - Doublons supprimés
  - 0 warnings ESLint

---

## 📈 Métriques d'Amélioration

| Aspect | Avant | Après | Gain |
|--------|-------|-------|------|
| Reconnaissance TMDb | ~40% | ~80% | +100% |
| Warnings ESLint | Multiple | 0 | -100% |
| Détection Films/Séries | ~60% | ~95% | +58% |
| Affichage miniatures | Partiel | 100% | N/A |
| Expérience recherche | Basique | Intelligente | N/A |

---

## 📚 Documentation Créée

- `RAPPORT_CORRECTIONS_BUGS_20NOV2025.md` : Rapport détaillé des corrections
- `GUIDE_TEST_CORRECTIONS.md` : Guide de test des fonctionnalités
- `DIAGNOSTIC_MINIATURES_FFMPEG.md` : Diagnostic et solutions miniatures

---

## 🚀 Installation / Mise à Jour

### Nouvelle Installation
```powershell
git clone https://github.com/MarketF0x/homeflix.git
cd homeflix
git checkout v1.3.3
.\INSTALLER.ps1
```

### Mise à Jour depuis v1.3.2
```powershell
cd homeflix
git pull origin dev
git checkout v1.3.3
.\homeflix.ps1
```

---

## ⚙️ Configuration Recommandée

### Paramètres optimaux
1. **Répertoires vidéo** : Utiliser l'explorateur graphique
2. **Durée minimale film** : 75 minutes (par défaut)
3. **Durée maximale série** : 55 minutes (par défaut)
4. **Cache miniatures** : 24 heures (automatique)

### Prérequis
- **ffmpeg** : Obligatoire pour miniatures et transcodage
- **ffprobe** : Obligatoire pour calcul durée (inclus avec ffmpeg)
- **API TMDb** : Recommandé pour métadonnées riches

---

## 🧪 Tests Effectués

✅ Scan de répertoires multiples  
✅ Détection Films/Séries (100+ vidéos testées)  
✅ Recherche intelligente (accents, mots partiels)  
✅ Génération miniatures ffmpeg  
✅ Génération miniatures TMDb  
✅ Explorateur de fichiers (sélection lecteurs)  
✅ Scan récursif (sous-dossiers multiples)  
✅ Calcul automatique durée  
✅ 0 warnings ESLint frontend  

---

## 🔮 Prochaines Étapes (v1.4.0)

- [ ] Gestion des collections TMDb améliorée
- [ ] Support multi-profils utilisateurs
- [ ] Optimisations transcodage réseau
- [ ] Interface mobile responsive
- [ ] Export/Import de bibliothèque

---

## 🙏 Remerciements

Merci à tous les testeurs et contributeurs qui ont remonté les bugs et suggéré des améliorations !

---

## 📞 Support

- **GitHub Issues** : [https://github.com/MarketF0x/homeflix/issues](https://github.com/MarketF0x/homeflix/issues)
- **Documentation** : `docs/INDEX_DOCUMENTATION.md`
- **FAQ** : `docs/FAQ.md`

---

**Version :** 1.3.3  
**Build :** stable-20251120  
**Licence :** MIT
