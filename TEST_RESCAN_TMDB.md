# Test rapide - Correction Re-scan TMDB

## 🎯 Objectif
Vérifier que le re-scan TMDB fonctionne maintenant correctement.

## 📝 Avant de commencer
1. Assurez-vous que le serveur est démarré
2. Assurez-vous que le client est lancé
3. Ouvrez les logs serveur pour voir les détails

## 🧪 Test 1 : Film avec affiche mais métadonnées vides

### Étapes :
1. Trouvez un film qui a :
   - ✅ Une affiche (poster)
   - ❌ Résumé vide
   - ❌ Acteurs vides
   - ❌ Note vide

2. Cliquez sur le film pour ouvrir `VideoDetail`

3. Cliquez sur le titre pour ouvrir le mode édition

4. **NE MODIFIEZ RIEN** dans le formulaire

5. Cliquez sur "Re-scanner avec TMDB"

### Résultat attendu :
- ✅ Message : "🔍 Recherche sur TMDb..."
- ✅ Puis : "✓ Métadonnées TMDb récupérées !"
- ✅ Le résumé est rempli
- ✅ Les acteurs sont affichés
- ✅ La note est présente
- ✅ La collection apparaît (si le film fait partie d'une saga)

### Logs serveur à vérifier :
```
🔍 Recherche TMDb: 'Nom du film' (2023) [titre BDD - manuel ou nettoyé]
📥 Téléchargement poster: https://image.tmdb.org/t/p/w500/...
✅ Poster téléchargé: C:\...\data\thumbs\...
✅ Enrichi: Nom du film (2023) - genre
   | Note: 8.5/10
   | Résumé: 250 caractères
   | Acteurs: Acteur 1, Acteur 2, ...
   | Collection: Nom de la collection #1
```

## 🧪 Test 2 : Modifier le titre puis re-scanner

### Étapes :
1. Trouvez un film avec un titre mal formaté (ex: "The Matrix 1999 1080p")

2. Ouvrez le mode édition

3. Changez le titre en "The Matrix"

4. Changez l'année en "1999"

5. Cliquez sur "Re-scanner avec TMDB"

### Résultat attendu :
- ✅ Message : "💾 Sauvegarde du titre/année..."
- ✅ Puis : "🔍 Recherche sur TMDb..."
- ✅ Puis : "✓ Métadonnées TMDb récupérées !"
- ✅ Le titre reste "The Matrix" (pas écrasé par TMDB)
- ✅ Toutes les métadonnées sont remplies

### Logs serveur à vérifier :
```
🔍 Recherche TMDb: 'The Matrix' (1999) [titre BDD - manuel ou nettoyé]
✅ Enrichi: The Matrix (1999) - science fiction
```

## 🧪 Test 3 : Film déjà complet

### Étapes :
1. Trouvez un film qui a TOUTES les métadonnées :
   - ✅ Titre
   - ✅ Année
   - ✅ Genre
   - ✅ Résumé
   - ✅ Acteurs
   - ✅ Note
   - ✅ Affiche

2. Ouvrez le mode édition

3. Cliquez sur "Re-scanner avec TMDB"

### Résultat attendu :
- ✅ Message : "🔍 Recherche sur TMDb..."
- ✅ Les métadonnées sont rafraîchies (même si déjà présentes)
- ✅ Le poster est re-téléchargé (version la plus récente)

### Logs serveur :
```
🔍 Recherche TMDb: 'Nom du film' (2023) [titre BDD - manuel ou nettoyé]
✅ Enrichi: Nom du film (2023) - genre
   | Note: 8.5/10
   | Résumé: 250 caractères
   | Acteurs: ...
```

## ❌ Cas d'échec attendu

### Film introuvable sur TMDB

**Étapes** :
1. Film avec un titre très obscur ou incorrect
2. Re-scanner avec TMDB

**Résultat** :
- ⚠️ Message : "Aucune métadonnée trouvée"
- Logs serveur : `❌ Aucune métadonnée trouvée pour: titre recherché`

**Solution** : Utiliser l'option "URL TMDb" pour forcer un film spécifique

## 🐛 Si ça ne fonctionne toujours pas

### Vérifications :

1. **Clé API TMDb**
   - Ouvrir `settings.yaml`
   - Vérifier que `tmdb_api_key` est renseigné

2. **Connexion Internet**
   - Tester : `https://api.themoviedb.org/3/configuration?api_key=VOTRE_CLE`

3. **Logs serveur**
   - Chercher les erreurs contenant "TMDb" ou "Erreur"
   - Vérifier le titre exact utilisé pour la recherche

4. **Cache du navigateur**
   - Recharger la page avec Ctrl+F5
   - Vider le cache si nécessaire

5. **Titre trop complexe**
   - Essayer de simplifier le titre manuellement
   - Retirer les caractères spéciaux
   - Utiliser seulement le nom principal du film

## ✅ Checklist de validation finale

- [ ] Test 1 réussi : Métadonnées vides sont remplies
- [ ] Test 2 réussi : Titre modifié est préservé
- [ ] Test 3 réussi : Film complet est rafraîchi
- [ ] Pas d'écrasement des données existantes
- [ ] Logs serveur montrent bien les recherches
- [ ] Les posters sont téléchargés
- [ ] Les collections sont détectées

## 📞 Support

Si tous les tests échouent :
1. Vérifier les logs dans `server/logs/`
2. Chercher les erreurs Python (traceback)
3. Vérifier la connexion à l'API TMDb
4. S'assurer que la clé API est valide
