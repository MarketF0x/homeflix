# Diagnostic - Problèmes de Codec Vidéo

## Problème actuel

Vidéo bloquée à **8 secondes** avec sauvegardes répétées de la même position.

### Logs observés
```
💾 Sauvegarde progression: vidéo 2101, position 8s, profil 2
✅ Progression sauvegardée
(répété plusieurs fois toutes les 5 secondes)
```

## Causes possibles

### 1. Codec vidéo non supporté par le navigateur
- **Symptôme** : Dimensions vidéo = 0x0
- **Solution** : Basculement automatique vers transcodage FFmpeg
- **Logs à vérifier** :
  ```
  ❌ CODEC VIDÉO NON SUPPORTÉ : Dimensions = 0x0
  🔄 Activation automatique du transcodage pour codec incompatible
  ```

### 2. Erreur de décodage (MEDIA_ERR_DECODE)
- **Code erreur** : 3
- **Cause** : Fichier corrompu ou codec non supporté
- **Solution** : Transcodage FFmpeg

### 3. Format non supporté (MEDIA_ERR_SRC_NOT_SUPPORTED)
- **Code erreur** : 4
- **Cause** : Container ou codec inconnu du navigateur
- **Solution** : Transcodage FFmpeg

### 4. Problème de buffering réseau
- **Symptôme** : ReadyState < 3, NetworkState != 2
- **Solution** : Micro-seek ou rechargement

## Nouveaux diagnostics ajoutés

### Logs détaillés lors des blocages
```javascript
⚠️ Vidéo bloquée détectée (X/15)
   Position: Xs
   ReadyState: X (0-4)
   NetworkState: X (0-3)
   Buffer: Xs
   Erreur: message d'erreur ou "Aucune"
```

### Détection améliorée des erreurs

#### A. Lors du chargement (loadedmetadata)
- Vérification dimensions vidéo (width/height)
- Affichage du chemin et extension
- Mode actuel (DIRECT/TRANSCODAGE)

#### B. Pendant la lecture (playing)
- Vérification codec en temps réel
- Détection des défaillances pendant la lecture

#### C. Lors des blocages (stalled check)
- Vérification codec si bloqué
- Basculement automatique vers transcodage
- Logs détaillés de l'état réseau

#### D. Erreurs de l'élément <video>
- **Code 1** : MEDIA_ERR_ABORTED (abandon)
- **Code 2** : MEDIA_ERR_NETWORK (réseau)
- **Code 3** : MEDIA_ERR_DECODE (décodage)
- **Code 4** : MEDIA_ERR_SRC_NOT_SUPPORTED (format)

## ReadyState (état de préparation)

- **0** : HAVE_NOTHING - Aucune donnée
- **1** : HAVE_METADATA - Métadonnées chargées
- **2** : HAVE_CURRENT_DATA - Données pour position actuelle
- **3** : HAVE_FUTURE_DATA - Assez pour jouer un peu
- **4** : HAVE_ENOUGH_DATA - Peut jouer jusqu'à la fin

## NetworkState (état réseau)

- **0** : NETWORK_EMPTY - Pas initialisé
- **1** : NETWORK_IDLE - Source sélectionnée, pas de chargement
- **2** : NETWORK_LOADING - Téléchargement en cours
- **3** : NETWORK_NO_SOURCE - Aucune source valide

## Procédure de diagnostic

### 1. Vérifier les logs dans la console

Ouvrez la console développeur et cherchez :

#### Logs de démarrage
```
🎬 VideoPlayer monté - Profil actuel: XXX ID: X
🎬 VideoPlayer URLs: { baseUrl, directUrl, transcodeUrl, ... }
```

#### Logs de métadonnées
```
⏱️ Durée vidéo: XXXs
✅ Dimensions vidéo OK: XXXxXXX
✅ Codec vidéo compatible - Mode: DIRECT/TRANSCODAGE
```

**OU**

```
❌ CODEC VIDÉO NON SUPPORTÉ : Dimensions = 0x0
   Chemin: C:\...\video.mkv
   Extension: mkv
   Mode actuel: DIRECT
🔄 Activation automatique du transcodage pour codec incompatible
```

#### Logs de blocage
```
⚠️ Vidéo bloquée détectée (1/15) - Position: 8s, ReadyState: 2, NetworkState: 2
   Buffer: 10s, Erreur: Aucune
```

Si répété 15 fois :
```
❌ VIDÉO BLOQUÉE - Tentative de déblocage automatique...
```

Si dimensions = 0x0 détectées lors du blocage :
```
❌ CODEC VIDÉO DÉFAILLANT détecté lors du blocage (dimensions = 0x0)
🔄 Basculement vers TRANSCODAGE pour résoudre le problème de codec
```

### 2. Vérifier l'erreur native de la vidéo

Si une erreur apparaît :
```
❌ Erreur vidéo détectée:
   Code: 3 (MEDIA_ERR_DECODE)
   Message: ...
   Position: 8s
   Mode: DIRECT
🔄 Basculement automatique vers TRANSCODAGE
```

### 3. Vérifier le transcodage FFmpeg côté serveur

Si le transcodage échoue aussi :
```
❌ Erreur : Impossible de décoder la vidéo même en transcodage. 
   Vérifiez FFmpeg sur le serveur.
```

**Actions à faire :**
- Vérifier les logs du serveur Python
- S'assurer que FFmpeg est installé : `ffmpeg -version`
- Vérifier que le chemin du fichier est accessible
- Tester manuellement : `ffmpeg -i "chemin/video.mkv" -t 10 test.mp4`

## Solutions par ordre de priorité

### Solution 1 : Laisser le basculement automatique fonctionner
Le VideoPlayer détecte maintenant automatiquement les problèmes de codec et bascule vers le transcodage.

**Attendez 30 secondes** après l'ouverture de la vidéo pour voir si le basculement se fait.

### Solution 2 : Forcer le transcodage manuellement

Si votre vidéo est dans un format connu pour causer des problèmes (AVI, WMV, FLV), le VideoPlayer devrait déjà forcer le transcodage au démarrage.

Les formats **MP4** et **WEBM** utilisent le streaming direct par défaut.

### Solution 3 : Vérifier FFmpeg côté serveur

```bash
# Windows PowerShell
ffmpeg -version

# Tester le transcodage manuel
ffmpeg -i "C:\chemin\video.mkv" -c:v libx264 -c:a aac -f mp4 -movflags frag_keyframe+empty_moov -t 30 test.mp4
```

### Solution 4 : Vérifier les logs serveur Python

Le serveur devrait afficher des logs lors du transcodage FFmpeg :
```
INFO: Transcodage FFmpeg démarré pour: C:\chemin\video.mkv
INFO: Commande FFmpeg: ffmpeg -i "..." -c:v libx264 ...
```

Si erreur :
```
ERROR: Erreur FFmpeg: ...
```

## Tests recommandés

1. **Vidéo MP4 simple** → Devrait fonctionner en DIRECT
2. **Vidéo MKV H.264** → Peut fonctionner en DIRECT ou bascule en TRANSCODAGE
3. **Vidéo AVI/WMV** → Devrait automatiquement utiliser TRANSCODAGE
4. **Vidéo avec codec exotique** → Détection erreur + basculement TRANSCODAGE

## Fichiers modifiés

- `client/src/VideoPlayer.jsx` : 
  - Logs détaillés de diagnostic
  - Détection améliorée des erreurs de codec
  - Basculement automatique intelligent
  - Gestion des codes d'erreur HTML5 Media

## Prochaines étapes

1. ✅ Ouvrir la console développeur (F12)
2. ✅ Lancer une vidéo problématique
3. ✅ Observer les logs détaillés
4. ✅ Partager les logs pour diagnostic approfondi
