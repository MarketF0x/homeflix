# Solution au problème "Audio sans vidéo"

## Problème identifié

Certains fichiers vidéo (comme Chappie) ne lisent que l'audio sans afficher la vidéo dans le navigateur. Ce problème est causé par des **codecs vidéo non supportés** nativement par les navigateurs web.

## Codecs problématiques courants

- **HEVC/H.265** : Utilisé dans de nombreux fichiers récents, non supporté par la plupart des navigateurs
- **VC-1** : Ancien codec Microsoft (WMV, certains AVI)
- **MPEG-4 Part 2 (DivX/XviD)** : Anciens formats
- **VP8/VP9** : Parfois problématique selon le navigateur

## Solutions implémentées

### 1. Détection automatique au chargement ✅

Le lecteur détecte maintenant automatiquement si la vidéo ne s'affiche pas :
- Vérification des dimensions vidéo (`videoWidth` et `videoHeight`)
- Si dimensions = 0 × 0 → Codec vidéo non supporté
- **Basculement automatique vers le transcodage FFmpeg**

### 2. Détection sur erreur de décodage ✅

Si le navigateur retourne une erreur de décodage (code 3 ou 4) :
- Activation automatique du transcodage FFmpeg
- Conversion temps réel en H.264 (compatible tous navigateurs)

### 3. Option manuelle dans le menu paramètres ✅

Un nouveau menu "Mode de lecture" permet de :
- **Streaming direct** : Qualité originale (par défaut)
- **Transcodage FFmpeg** : À activer manuellement si problème détecté

## Comment utiliser

### Si vous rencontrez le problème :

1. **Ouvrez le lecteur vidéo** pour le fichier problématique
2. **Cliquez sur l'icône ⚙️ Paramètres** (en bas à droite)
3. Dans la section **"Mode de lecture"**, sélectionnez **"Transcodage FFmpeg"**
4. La vidéo se rechargera automatiquement avec transcodage

### Détection automatique

Dans la plupart des cas, le système détecte automatiquement le problème et bascule vers le transcodage sans intervention manuelle.

## Indicateurs de transcodage actif

Quand le transcodage est activé, vous verrez :
- Le menu "Piste audio source" avec les pistes du fichier original
- Le menu "Sous-titres source" si disponibles
- Message : "🔄 Activation du transcodage..." pendant le chargement

## Formats automatiquement transcodés

Ces formats déclenchent le transcodage dès le départ :
- `.avi` (ancien codec)
- `.wmv` (Windows Media)
- `.flv` (Flash Video)
- `.vob` (DVD)
- `.ogv` (Ogg Video)
- `.webm` (si codec VP8/VP9 incompatible)

## Performances

- **Streaming direct** : Pas de conversion, latence minimale
- **Transcodage FFmpeg** : 
  - Conversion temps réel en H.264
  - Délai de démarrage : 5-15 secondes
  - Qualité excellente préservée
  - Compatible 100% navigateurs

## Fichiers testés

✅ MKV avec H.264 : Streaming direct
✅ MKV avec HEVC : Transcodage auto
✅ AVI avec DivX : Transcodage auto
✅ MP4 avec H.264 : Streaming direct

## Notes techniques

Le transcodage utilise FFmpeg avec ces paramètres :
- Codec vidéo : `libx264` (H.264)
- Preset : `ultrafast` (latence minimale)
- Codec audio : `aac` (compatible universel)
- Format : HLS (HTTP Live Streaming)

## Support

Si vous rencontrez toujours des problèmes :
1. Vérifiez que FFmpeg est bien installé (requis pour le transcodage)
2. Consultez les logs du serveur pour plus de détails
3. Essayez de basculer manuellement vers le transcodage via le menu paramètres
