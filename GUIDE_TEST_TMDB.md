# Guide de test des améliorations TMDB

## 🚀 Comment tester

### Test 1 : Métadonnées vides corrigées

1. **Trouvez un film** avec seulement la jaquette mais métadonnées manquantes
2. **Ouvrez VideoDetail** en cliquant sur le film
3. **Cliquez sur le bouton "Modifier"** (icône crayon)
4. **Cliquez sur "Re-scanner avec TMDB"**
5. **Vérifiez** :
   - ✅ Le résumé est rempli
   - ✅ Les acteurs sont affichés
   - ✅ La note est présente
   - ✅ La collection apparaît (si applicable)

### Test 2 : Nom modifié manuellement

1. **Trouvez un film** avec un nom mal formaté (ex: "The.Matrix.1999.1080p.mkv")
2. **Ouvrez VideoDetail**
3. **Cliquez sur "Modifier"**
4. **Changez le titre** en "The Matrix" (propre, sans caractères spéciaux)
5. **Cliquez sur "Sauvegarder"**
6. **Attendez 2 secondes** (fermeture automatique)
7. **Rouvrez "Modifier"**
8. **Cliquez sur "Re-scanner avec TMDB"**
9. **Vérifiez dans les logs serveur** :
   ```
   🔍 Recherche TMDb: 'The Matrix' (1999) [titre BDD - manuel ou nettoyé]
   ```
10. **Vérifiez dans l'interface** :
    - ✅ Le titre reste "The Matrix"
    - ✅ Toutes les métadonnées sont récupérées
    - ✅ Le poster officiel est téléchargé

### Test 3 : Mise à jour locale immédiate

1. **Modifiez le titre** d'un film
2. **Cliquez sur "Sauvegarder"**
3. **Vérifiez** :
   - ✅ Le titre change IMMÉDIATEMENT dans VideoDetail
   - ✅ Pas de rechargement de page
   - ✅ Le carousel en arrière-plan ne bouge pas
   - ✅ Message de confirmation affiché

### Test 4 : Collection récupérée

1. **Prenez un film de saga** (ex: Harry Potter, Star Wars, Matrix)
2. **Re-scannez avec TMDB**
3. **Vérifiez** :
   - ✅ Le champ "Collection" est rempli
   - ✅ Le nom complet de la saga apparaît

## 📊 Logs à surveiller

Ouvrez les logs du serveur (`server/logs/`) et cherchez :

```
🔍 Recherche TMDb: 'Titre Film' (2023) [titre BDD - manuel ou nettoyé]
```
OU
```
🔍 Recherche TMDb: 'Titre Film' (2023) [nettoyé depuis fichier]
```

**Important** :
- `[titre BDD - manuel ou nettoyé]` = Le titre modifié manuellement est utilisé ✅
- `[nettoyé depuis fichier]` = Aucun titre en BDD, utilise le fichier

### Logs détaillés attendus

```
📥 Téléchargement poster: https://image.tmdb.org/t/p/w500/abc123.jpg
✅ Poster téléchargé: C:\...\data\thumbs\video_123.jpg
✅ Enrichi: The Matrix (1999) - science fiction
   | Note: 8.7/10
   | Résumé: 136 caractères
   | Acteurs: Keanu Reeves, Laurence Fishburne, Carrie-...
   | Collection: The Matrix Collection #1
```

## 🐛 Problèmes potentiels

### Le poster ne se télécharge pas

**Symptôme** : `⚠️ Échec téléchargement poster (HTTP 404)`

**Solution** :
- Vérifiez la clé API TMDb dans `settings.yaml`
- Le poster peut ne pas exister sur TMDb

### Les métadonnées restent vides

**Symptôme** : Après re-scan, certains champs sont toujours vides

**Vérifiez dans les logs** :
```
| Résumé: (vide)
| Acteurs: (vide)
```

**Causes possibles** :
1. Film pas trouvé sur TMDb (essayez avec l'URL manuelle)
2. Clé API invalide
3. Film trop récent ou obscur

**Solution** : Utilisez l'option "URL TMDb" pour forcer un ID spécifique

### Le titre modifié est écrasé

**Symptôme** : Après re-scan, le titre revient à l'ancien

**Vérifiez** :
1. Avez-vous bien cliqué sur "Sauvegarder" AVANT le re-scan ?
2. Regardez les logs pour confirmer `[titre BDD - manuel ou nettoyé]`

## ✅ Checklist de validation

- [ ] Les métadonnées vides sont remplies après re-scan
- [ ] Le poster est téléchargé automatiquement
- [ ] Le titre modifié manuellement est conservé
- [ ] La collection est récupérée pour les films de saga
- [ ] Pas de rechargement de page lors de la sauvegarde
- [ ] Les logs montrent `[titre BDD - manuel ou nettoyé]` après modification
- [ ] Le marqueur `.jpg.manual` est créé dans `data/thumbs/`

## 🎯 Cas d'usage réels

### Scénario A : Film mal nommé automatiquement
```
Fichier: "The.Dark.Knight.2008.REMASTERED.1080p.BluRay.x265-RARBG.mkv"
Titre auto: "The Dark Knight 2008 Remastered 1080p Bluray X265 Rarbg"

1. Modifier → Titre: "The Dark Knight"
2. Sauvegarder
3. Re-scanner avec TMDB
4. Résultat: Toutes les métadonnées + poster officiel
```

### Scénario B : Film avec caractères spéciaux
```
Fichier: "L'Étrange Noël de Mr Jack (1993).mkv"
Titre auto: "L Étrange Noël De Mr Jack"

1. Modifier → Titre: "L'Étrange Noël de Mr Jack"
2. Sauvegarder
3. Re-scanner avec TMDB
4. Résultat: Recherche avec le bon titre accentué
```

### Scénario C : Métadonnées partielles
```
Film a: Titre ✅, Jaquette ✅, mais Résumé ❌, Acteurs ❌, Note ❌

1. Re-scanner avec TMDB
2. Résultat: Tous les champs remplis, poster re-téléchargé
```

## 📝 Notes

- Le re-scan est **non destructif** : conserve les modifications manuelles
- Le poster TMDb écrase toujours le poster existant (pour avoir la meilleure qualité)
- La collection est détectée automatiquement pour les films de saga
- Les logs détaillés aident au diagnostic en cas de problème
