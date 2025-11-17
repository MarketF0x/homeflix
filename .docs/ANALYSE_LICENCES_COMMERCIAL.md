# 📄 Analyse des Licences pour Usage Commercial - Homeflix

**Date d'analyse :** 14 novembre 2025  
**Application :** Homeflix (aussi appelée HomeOne dans certains contextes)

## ✅ Conclusion Générale

**OUI, tous les composants du programme Homeflix sont libres de droit pour une utilisation commerciale.**

---

## 📋 Licence du Projet Principal

### Homeflix - Licence MIT

Selon le fichier `installer/README_USER.md`, le projet est distribué sous **licence MIT**.

**Permissions de la licence MIT :**
- ✅ **Utilisation gratuite**
- ✅ **Modification du code**
- ✅ **Distribution**
- ✅ **Usage commercial**

**Obligations :**
- Inclure le texte de la licence MIT dans les distributions
- Mentionner les droits d'auteur originaux

---

## 🔍 Analyse des Dépendances

### Backend (Python)

Toutes les dépendances Python utilisent des licences compatibles avec l'usage commercial :

| Package | Licence | Commercial OK |
|---------|---------|---------------|
| FastAPI | MIT | ✅ |
| Uvicorn | BSD | ✅ |
| SQLAlchemy | MIT | ✅ |
| Pydantic | MIT | ✅ |
| ruamel.yaml | MIT | ✅ |
| Requests | Apache 2.0 | ✅ |
| PyYAML | MIT | ✅ |
| Pillow | HPND (PIL) | ✅ |
| python-multipart | Apache 2.0 | ✅ |
| pytest | MIT | ✅ |
| pytest-asyncio | Apache 2.0 | ✅ |
| pytest-cov | MIT | ✅ |
| httpx | BSD | ✅ |

### Frontend (JavaScript/React)

Toutes les dépendances JavaScript/React utilisent également des licences permissives :

| Package | Licence | Commercial OK |
|---------|---------|---------------|
| React | MIT | ✅ |
| React-DOM | MIT | ✅ |
| Three.js | MIT | ✅ |
| @react-three/fiber | MIT | ✅ |
| Vite | MIT | ✅ |
| ESLint | MIT | ✅ |

---

## 📚 Types de Licences Identifiées

### 1. **MIT License** (Majorité)
- **Permissivité maximale**
- Usage commercial autorisé sans restriction
- Utilisée par : React, FastAPI, SQLAlchemy, Three.js, etc.

### 2. **Apache License 2.0**
- **Très permissive**
- Usage commercial autorisé
- Protection contre les brevets
- Utilisée par : Requests, python-multipart

### 3. **BSD License**
- **Permissive**
- Usage commercial autorisé
- Utilisée par : Uvicorn, httpx

### 4. **HPND (Historical Permission Notice and Disclaimer)**
- **Permissive**
- Usage commercial autorisé
- Utilisée par : Pillow (PIL)

---

## ⚠️ Points d'Attention

### 1. API TMDb
- **Non inclus dans le code source**
- Utilisation soumise aux conditions de TMDb
- ⚠️ **Vérifier les CGU de TMDb pour usage commercial**
- Mention requise dans l'interface : "Ce produit utilise l'API TMDb mais n'est ni approuvé ni certifié par TMDb"

### 2. FFmpeg (Optionnel)
- Licence **LGPL** (ou GPL selon compilation)
- Utilisation en tant qu'exécutable externe : ✅ OK
- Pas de liaison statique dans le code
- Pas de restriction pour usage commercial si utilisé comme outil externe

### 3. Contenu Multimédia
- Les **affiches et métadonnées** récupérées appartiennent à leurs propriétaires
- L'application ne distribue pas ce contenu, elle le récupère dynamiquement
- L'utilisateur est responsable du contenu qu'il héberge

---

## ✅ Recommandations pour Usage Commercial

### 1. Mentions Légales à Inclure

```
HomeFlix - Serveur de Streaming Personnel
Copyright (c) 2025 [Votre Nom/Entreprise]

Basé sur Homeflix sous licence MIT

Ce produit utilise l'API TMDb mais n'est ni approuvé ni certifié par TMDb.
Les affiches et métadonnées appartiennent à leurs propriétaires respectifs.
```

### 2. Fichier LICENSE à Créer

Créer un fichier `LICENSE` à la racine du projet avec le texte complet de la licence MIT :

```
MIT License

Copyright (c) 2025 [Votre Nom]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 3. Attribution des Dépendances

Considérer l'inclusion d'un fichier `THIRD_PARTY_LICENSES.md` listant toutes les dépendances et leurs licences.

### 4. Vérification API TMDb

**Important :** Avant tout usage commercial, vérifier les conditions d'utilisation de l'API TMDb sur :
- https://www.themoviedb.org/documentation/api/terms-of-use

Points clés généralement autorisés :
- ✅ Utilisation gratuite de l'API
- ✅ Usage dans applications commerciales
- ⚠️ Attribution requise
- ⚠️ Respect des limites de requêtes

---

## 📊 Résumé des Risques

| Composant | Risque Commercial | Action Requise |
|-----------|-------------------|----------------|
| Code source Homeflix | ✅ Aucun | Inclure licence MIT |
| Dépendances Python | ✅ Aucun | Respecter attributions |
| Dépendances JavaScript | ✅ Aucun | Respecter attributions |
| API TMDb | ⚠️ Faible | Vérifier CGU + Attribution |
| FFmpeg | ✅ Aucun (usage externe) | Optionnel |
| Contenu utilisateur | ⚠️ Variable | Responsabilité utilisateur |

---

## 🎯 Verdict Final

**Homeflix peut être utilisé commercialement sans restriction juridique majeure.**

### Actions Recommandées :

1. ✅ Créer un fichier `LICENSE` avec la licence MIT
2. ✅ Ajouter les mentions de copyright appropriées
3. ✅ Documenter les dépendances tierces
4. ✅ Vérifier les conditions TMDb pour votre cas d'usage spécifique
5. ✅ Ajouter les attributions requises dans l'interface

### Aucune redevance ou licence supplémentaire requise pour :
- Le code source Homeflix
- Les bibliothèques Python (FastAPI, SQLAlchemy, etc.)
- Les bibliothèques JavaScript (React, Three.js, etc.)
- FFmpeg (si utilisé comme exécutable externe)

---

## 📞 Ressources Utiles

- **Licence MIT** : https://opensource.org/licenses/MIT
- **Apache 2.0** : https://www.apache.org/licenses/LICENSE-2.0
- **BSD Licenses** : https://opensource.org/licenses/BSD-3-Clause
- **TMDb Terms** : https://www.themoviedb.org/documentation/api/terms-of-use
- **Choose a License** : https://choosealicense.com/

---

*Document généré le 14 novembre 2025*
