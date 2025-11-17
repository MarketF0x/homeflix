# 🧪 GUIDE DE TEST - OPTIMISATIONS LECTEUR

## 🚀 DÉMARRAGE RAPIDE

### 1. Tester le système
```powershell
# Depuis la racine du projet
python test_video_optimization.py
```

**Résultat attendu:**
```
✅ FFmpeg installé: ffmpeg version X.X.X
✅ NVIDIA NVENC détecté (h264_nvenc)
   OU
💻 Aucun GPU détecté - Utilisation CPU (libx264)
```

---

### 2. Tester avec un fichier vidéo spécifique
```powershell
# Remplacer par le chemin de votre fichier Jumanji
python test_video_optimization.py "D:\Films\Jumanji\Jumanji.mkv"
```

**Analyse automatique:**
- Codec vidéo (H.264, DivX, etc.)
- Résolution (720p, 1080p, 4K)
- Pistes audio et sous-titres
- Vitesse de transcodage

---

## 🎬 TEST DU FILM JUMANJI

### Méthode 1: Via l'interface web

1. **Redémarrer le serveur:**
```powershell
cd server
python main.py
```

2. **Ouvrir Homeflix** dans le navigateur

3. **Ouvrir la console navigateur** (F12)

4. **Lancer le film Jumanji**

5. **Vérifier les logs:**

**✅ SUCCÈS - Exemples de logs:**
```javascript
// Console navigateur
🎬 VideoPlayer monté - Profil actuel: Papa
📊 Preload forcé sur auto
🔄 Rechargement vidéo - Mode: TRANSCODAGE
✅ Dimensions vidéo valides: 1920x1080
✅ Lecture automatique réussie
```

```
// Logs serveur (server/homeflix.log)
[VIDEO] TRANSCODAGE demandé: D:\Films\Jumanji\Jumanji.mkv
   ✅ [VIDEO] Codec H264 compatible - COPIE DIRECTE
   ⚡ Mode COPY activé - Pas de réencodage vidéo
   🎮 GPU NVIDIA détecté - Utilisation NVENC
✅ [STREAMING] Premier chunk envoyé - Lecture peut démarrer (256.0 KB)
```

**❌ ÉCHEC - Exemples de logs:**
```javascript
// Console navigateur
❌ CODEC VIDÉO NON SUPPORTÉ : Dimensions = 0x0
🔄 FALLBACK AUTOMATIQUE : Activation du transcodage FFmpeg...
```

```
// Logs serveur
❌ [ERROR] Erreur transcodage FFmpeg: ...
```

---

### Méthode 2: Test direct avec FFmpeg

**Commande de test manuelle:**
```powershell
# Remplacer CHEMIN_JUMANJI par le vrai chemin
ffmpeg -i "CHEMIN_JUMANJI" -t 30 -c:v libx264 -preset medium -crf 21 -c:a aac test_jumanji.mp4
```

**Résultat attendu:**
```
✅ Transcodage réussi → Fichier test_jumanji.mp4 créé
❌ Erreur → Voir les messages FFmpeg
```

---

## 📊 INTERPRÉTATION DES RÉSULTATS

### Scénario A: Film fonctionne immédiatement
```
✅ Codec compatible (H.264/H.265)
✅ Pas de transcodage nécessaire
✅ Lecture en 2-3 secondes
```
**Action:** Rien à faire ✅

---

### Scénario B: Bascule automatique vers transcodage
```
⚠️  Codec incompatible détecté
🔄 Activation automatique du transcodage
✅ Lecture démarre après 5-10 secondes
```
**Action:** C'est normal pour les vieux formats (DivX, XviD, etc.) ✅

---

### Scénario C: Transcodage lent (> 20 secondes)
```
⚠️  Transcodage actif
💻 CPU uniquement
⏳ Vitesse: 0.8x temps réel
```
**Actions possibles:**
1. Installer pilotes GPU NVIDIA/Intel
2. Réduire qualité (profil "Fast")
3. Préconvertir le film avec Handbrake

---

### Scénario D: Échec total
```
❌ Codec vidéo non supporté même en transcodage
❌ Erreur FFmpeg
```
**Diagnostics:**

**Test 1: Vérifier FFmpeg**
```powershell
ffmpeg -version
```

**Test 2: Tester codec du fichier**
```powershell
ffprobe -i "CHEMIN_JUMANJI"
```

**Test 3: Logs détaillés serveur**
```powershell
Get-Content server\homeflix.log -Tail 100
```

---

## 🔧 RÉSOLUTION PROBLÈMES COURANTS

### Problème: "FFmpeg non installé"
**Solution:**
```powershell
# Vérifier PATH
$env:PATH -split ';' | Select-String ffmpeg

# Réinstaller FFmpeg si nécessaire
# https://www.gyan.dev/ffmpeg/builds/
```

---

### Problème: GPU non détecté
**Solution NVIDIA:**
```powershell
# Vérifier pilotes NVIDIA
nvidia-smi

# Tester NVENC
ffmpeg -h encoder=h264_nvenc
```

**Solution Intel:**
```powershell
# Installer Intel Media SDK
# https://github.com/Intel-Media-SDK/MediaSDK
```

---

### Problème: Transcodage très lent
**Causes possibles:**
1. CPU faible (< 4 cœurs)
2. Fichier très lourd (> 10 GB)
3. Résolution 4K sans GPU

**Solutions:**
1. Activer GPU (voir ci-dessus)
2. Réduire qualité: `quality=fast` dans URL
3. Préconvertir avec Handbrake

---

### Problème: Audio mais pas d'image
**Cause:** Codec vidéo vraiment incompatible

**Diagnostic:**
```powershell
ffprobe -i "CHEMIN_FILM" | Select-String "Video:"
```

**Solutions:**
1. Vérifier que FFmpeg supporte ce codec
2. Mettre à jour FFmpeg vers version récente
3. Convertir le film avec Handbrake

---

## 📝 CHECKLIST VALIDATION

Avant de considérer les optimisations validées :

- [ ] **Test système réussi**
  ```powershell
  python test_video_optimization.py
  # ✅ FFmpeg OK, GPU détecté
  ```

- [ ] **Film Jumanji se lit**
  ```
  ✅ Lecture démarrée en < 10 secondes
  ✅ Pas d'erreurs console navigateur
  ```

- [ ] **Logs serveur corrects**
  ```
  ✅ Voir "COPIE DIRECTE" ou "TRANSCODAGE"
  ✅ Voir "Premier chunk envoyé"
  ✅ Pas d'erreurs FFmpeg
  ```

- [ ] **Test autres films MKV**
  ```
  ✅ Au moins 3 films différents testés
  ✅ Tous fonctionnent
  ```

- [ ] **Test changement piste audio**
  ```
  ✅ Bascule sans erreur
  ✅ Reprend à la bonne position
  ```

---

## 🎯 CRITÈRES DE SUCCÈS

### Performance attendue

| Type fichier | Codec | Démarrage attendu | Mode |
|--------------|-------|-------------------|------|
| **MP4 H.264** | H.264 | 1-2s | Direct |
| **MKV H.264** | H.264 | 2-3s | Copy |
| **MKV H.265** | HEVC | 2-4s | Copy |
| **AVI DivX** | DivX | 5-10s | Transcode |
| **MKV XviD** | XviD | 5-10s | Transcode |

### Avec GPU (NVENC/QSV)
- Transcodage: **3-5x plus rapide**
- 1080p: **< 5 secondes** de démarrage
- 4K: **< 10 secondes** de démarrage

### Sans GPU (CPU)
- Transcodage: **1x vitesse réelle**
- 1080p: **10-15 secondes** de démarrage
- 4K: **20-30 secondes** de démarrage

---

## 🚀 COMMANDES UTILES

### Analyser un fichier vidéo
```powershell
ffprobe -v error -show_entries stream=codec_name,width,height,channels -of json "CHEMIN_FILM"
```

### Tester transcodage GPU
```powershell
# NVIDIA
ffmpeg -i "INPUT.mkv" -t 30 -c:v h264_nvenc -preset medium test.mp4

# Intel
ffmpeg -i "INPUT.mkv" -t 30 -c:v h264_qsv -preset medium test.mp4

# CPU
ffmpeg -i "INPUT.mkv" -t 30 -c:v libx264 -preset medium test.mp4
```

### Voir logs serveur en temps réel
```powershell
Get-Content server\homeflix.log -Wait -Tail 20
```

### Nettoyer fichiers test
```powershell
Remove-Item test*.mp4
```

---

## 📞 RAPPORTER UN PROBLÈME

Si le film ne fonctionne toujours pas :

**1. Collecter informations:**
```powershell
# Analyse fichier
ffprobe -i "CHEMIN_JUMANJI" > jumanji_info.txt

# Logs serveur
Get-Content server\homeflix.log -Tail 100 > server_logs.txt
```

**2. Tester transcodage manuel:**
```powershell
ffmpeg -i "CHEMIN_JUMANJI" -t 10 -c:v libx264 -preset medium test.mp4 2> ffmpeg_error.txt
```

**3. Fournir:**
- Contenu de `jumanji_info.txt`
- Contenu de `server_logs.txt`
- Contenu de `ffmpeg_error.txt`
- Console navigateur (F12 → onglet Console → copier tout)

---

**FIN DU GUIDE**
