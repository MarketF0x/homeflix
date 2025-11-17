# 🎬 Compatibilité Formats Vidéo - HomeFlix

## Formats supportés nativement par HTML5

✅ **Toujours compatibles** (streaming direct) :
- `.mp4` (H.264/AAC)
- `.webm` (VP8/VP9)
- `.ogg` (Theora)

## Formats avec transcodage automatique

### ⚙️ Transcodage IMMÉDIAT (dès le chargement)
Ces formats sont **rarement** supportés nativement par les navigateurs :
- `.avi` - Format Windows ancien
- `.wmv` - Windows Media Video
- `.flv` - Flash Video
- `.vob` - DVD Video
- `.ogv` - Ogg Video
- `.webm` - WebM (certaines variantes)

➡️ **Action** : Le lecteur charge directement avec FFmpeg

### 🔄 Transcodage À LA DEMANDE (si erreur)
Ces formats sont **parfois** supportés (selon codec vidéo/audio) :
- `.mkv` - Matroska (compatible si H.264/AAC)
- `.mov` - QuickTime (compatible si H.264/AAC)
- `.m4v` - iTunes Video

➡️ **Action** : 
1. Essai de lecture directe
2. Si erreur → Basculement automatique vers FFmpeg

## Comment ça fonctionne ?

### 1. Détection du format
```javascript
const videoExt = video.path.split('.').pop();
const needsTranscode = ['avi', 'wmv', 'flv', 'vob'].includes(videoExt);
```

### 2. Basculement automatique
```javascript
onError={(e) => {
  if (e.target.error.code === 3) { // MEDIA_ERR_DECODE
    setUseTranscode(true); // Activer FFmpeg
  }
}
```

### 3. URLs générées
- **Direct** : `/api/stream?path=video.mkv`
- **Transcodé** : `/api/stream/transcode?path=video.mkv`

## Indicateurs visuels

### Badge orange (coin supérieur droit)
```
⚙️ Transcodage FFmpeg actif
```
Signifie que la vidéo est convertie en temps réel.

### Message de basculement
```
🔄 Format non supporté - Activation du transcodage FFmpeg...
```
Apparaît brièvement lors du passage au transcodage.

## Avantages de cette approche

✅ **Performance** : MKV avec H.264 → lecture directe (pas de transcodage)
✅ **Compatibilité** : AVI/WMV → transcodage automatique
✅ **Transparence** : L'utilisateur voit un badge quand FFmpeg est utilisé
✅ **Fallback** : Si direct échoue, bascule vers transcodage
✅ **Économie** : Pas de transcodage inutile pour formats compatibles

## Résolution de problèmes

### Vidéo ne se charge pas
1. Vérifier les logs console (F12)
2. Chercher : `🎬 VideoPlayer - Mode:`
3. Si "Streaming direct" → Vérifier codec vidéo (doit être H.264)
4. Si "TRANSCODAGE FFmpeg" → Vérifier que FFmpeg est installé

### FFmpeg non installé
```bash
# Windows (Chocolatey)
choco install ffmpeg

# Vérifier installation
ffmpeg -version
```

### Performance lente
- **MKV avec H.265** : Sera transcodé → Plus lent
- **MKV avec H.264** : Lecture directe → Rapide
- **AVI** : Toujours transcodé → Moyen

## Recommandations

### Pour la meilleure performance
1. **Privilégier** : MP4 (H.264/AAC)
2. **Acceptable** : MKV (H.264/AAC)
3. **Éviter** : AVI, WMV, FLV

### Conversion recommandée
Pour convertir vos vidéos en MP4 optimal :
```bash
ffmpeg -i input.mkv -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k output.mp4
```

## Architecture technique

```
┌─────────────┐
│   Client    │
│ (VideoPlayer)│
└──────┬──────┘
       │
       ├─► Essai 1: /api/stream (direct)
       │   ✓ Succès → Lecture
       │   ✗ Erreur décodage → 
       │
       └─► Essai 2: /api/stream/transcode (FFmpeg)
           ✓ Succès → Lecture avec badge
           ✗ Erreur → Message erreur
```

## Logs utiles

```javascript
// Console logs à surveiller
🎬 VideoPlayer - Mode: Streaming direct
🎬 VideoPlayer - Mode: TRANSCODAGE FFmpeg (format incompatible)
🔄 Erreur de décodage détectée - Basculement automatique
✅ Vidéo prête à être lue
```
