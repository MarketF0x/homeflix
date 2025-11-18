# 🧪 Test de Diagnostic - Transcodage HTTP

## Objectif
Vérifier que le serveur backend renvoie bien un flux vidéo MP4 valide lors du transcodage.

## Test 1 : Vérifier la réponse HTTP

### Dans Firefox/Chrome, ouvrir la Console (F12) et exécuter :

```javascript
// Remplacer par le chemin de votre fichier AVI
const testUrl = 'http://100.72.164.87:8000/api/stream/transcode?path=H:\\Film\\Jumanji.avi&audio_track=1&quality=medium';

fetch(testUrl, { method: 'HEAD' })
  .then(response => {
    console.log('✅ Headers de la réponse:');
    console.log('Status:', response.status);
    console.log('Content-Type:', response.headers.get('Content-Type'));
    console.log('Accept-Ranges:', response.headers.get('Accept-Ranges'));
    console.log('Connection:', response.headers.get('Connection'));
    console.log('Transfer-Encoding:', response.headers.get('Transfer-Encoding'));
    
    // Toutes les headers
    for (let [key, value] of response.headers) {
      console.log(`${key}: ${value}`);
    }
  })
  .catch(err => console.error('❌ Erreur:', err));
```

### Résultat attendu :
```
Status: 200
Content-Type: video/mp4
Accept-Ranges: none
Connection: keep-alive
```

## Test 2 : Télécharger les premiers octets

```javascript
const testUrl = 'http://100.72.164.87:8000/api/stream/transcode?path=H:\\Film\\Jumanji.avi&audio_track=1&quality=medium';

fetch(testUrl)
  .then(response => response.body.getReader())
  .then(reader => {
    let bytesReceived = 0;
    let chunks = [];
    
    const pump = () => {
      return reader.read().then(({ done, value }) => {
        if (done) {
          console.log('✅ Stream terminé');
          return;
        }
        
        bytesReceived += value.length;
        chunks.push(value);
        console.log(`📦 Reçu: ${bytesReceived} octets`);
        
        // Arrêter après 1 MB
        if (bytesReceived > 1024 * 1024) {
          console.log('✅ 1 MB reçu - Stream fonctionne !');
          console.log('📊 Premiers octets (hex):', 
            Array.from(chunks[0].slice(0, 20))
              .map(b => b.toString(16).padStart(2, '0'))
              .join(' ')
          );
          reader.cancel();
          return;
        }
        
        return pump();
      });
    };
    
    return pump();
  })
  .catch(err => console.error('❌ Erreur:', err));
```

### Résultat attendu :
- Les octets devraient commencer par `00 00 00 ...` (signature MP4)
- Devrait recevoir au moins 512 KB rapidement

## Test 3 : Vérifier avec curl (PowerShell)

```powershell
# Télécharger les premiers 1 MB
$url = "http://100.72.164.87:8000/api/stream/transcode?path=H:\Film\Jumanji.avi&audio_track=1&quality=medium"
Invoke-WebRequest -Uri $url -Method GET -OutFile "test_transcode.mp4" -TimeoutSec 30

# Vérifier la taille du fichier
Get-Item test_transcode.mp4 | Select-Object Length, Name

# Essayer de lire avec VLC ou MediaInfo
```

## Test 4 : Vérifier les logs FFmpeg côté serveur

Regarder le terminal où le backend Python tourne pour voir :
```
[VIDEO] TRANSCODAGE demande: H:\Film\Jumanji.avi
[PROCESS] Lancement FFmpeg - Mode: TRANSCODAGE (libx264)
✅ [STREAMING] Premier chunk envoyé - Lecture IMMÉDIATE (512.0 KB)
```

Si vous voyez des erreurs FFmpeg, les noter ici.

## Diagnostic selon les résultats

### Cas 1 : Headers corrects, pas de données reçues
→ Problème FFmpeg côté serveur (codec non supporté, fichier corrompu)

### Cas 2 : Données reçues mais vidéo bloquée
→ Problème de format MP4 fragmenté (signature incorrecte)

### Cas 3 : Timeout ou erreur réseau
→ Problème de firewall ou serveur backend planté

### Cas 4 : Tout fonctionne dans les tests mais pas dans le lecteur
→ Problème de compatibilité avec l'élément `<video>` HTML5
