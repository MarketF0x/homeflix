# 🗜️ Guide de Compression des Vidéos Volumineuses

## Pourquoi compresser ?

Les **gros fichiers MKV** (> 1,5 GB) nécessitent un **transcodage en temps réel** qui peut prendre 20-60 secondes avant de démarrer. En les **pré-compressant en MP4 H.264**, vous obtenez :

✅ **Lecture instantanée** (pas de transcodage)  
✅ **Économie d'espace** (65-75% de réduction)  
✅ **Même qualité visuelle** (imperceptible à l'œil)  
✅ **Compatible tous navigateurs**

---

## 📊 Niveaux de Qualité

| Niveau | CRF | Résolution | Audio | Réduction | Qualité |
|--------|-----|------------|-------|-----------|---------|
| **Haute** | 20 | 1080p | 192k | ~50% | Excellente |
| **Moyenne** | 23 | 1080p | 128k | ~65% | Très bonne ⭐ |
| **Rapide** | 26 | 720p | 128k | ~75% | Bonne |

💡 **Recommandation** : Niveau **Moyenne** (CRF 23) - meilleur compromis qualité/taille

---

## 🚀 Option 1 : Compresser UNE vidéo (test)

**Idéal pour tester avant de compresser toutes les vidéos**

### Utilisation

```powershell
# Méthode 1 : Avec chemin en argument
python compress_one_video.py "I:\FILM\Les Tortues Ninja 2.mkv"

# Méthode 2 : Mode interactif
python compress_one_video.py
# Puis entrez le chemin quand demandé
```

### Exemple

```
📁 Chemin de la vidéo : I:\FILM\Les Tortues ninja 2 1991.mkv

📐 Qualité :
1. Haute
2. Moyenne [RECOMMANDÉ]
3. Rapide

Votre choix : 2

🎬 Compression de : Les Tortues ninja 2 1991.mkv
📏 Taille actuelle : 2.42 GB
⚙️  Qualité : Bonne qualité (~65% réduction)
💾 Sortie : Les Tortues ninja 2 1991.mp4

⏳ Compression en cours...
   frame=12345 fps=45 time=00:15:30 ...

✅ Compression réussie !
   Avant : 2.42 GB
   Après : 0.85 GB
   Réduction : 65%
   Espace libéré : 1.57 GB
```

---

## 🗂️ Option 2 : Compresser TOUTES les vidéos volumineuses

**Scanne automatiquement tous vos dossiers vidéo et compresse les fichiers > 1,5 GB**

### Utilisation

```powershell
python compress_large_videos.py
```

### Processus

1. **Scan automatique** des dossiers configurés dans `settings.yaml`
2. **Liste toutes les vidéos** > 1,5 GB (MKV, AVI, MOV, FLV, WMV)
3. **Choix de la qualité** (haute/moyenne/rapide)
4. **Estimation** de l'espace libéré
5. **Compression batch** de toutes les vidéos
6. **Sauvegarde automatique** des originaux en `.original`

### Exemple

```
🔍 Recherche des vidéos > 1.5 GB...

📊 12 vidéo(s) volumineuse(s) trouvée(s) :

  1. Les Tortues ninja 2 1991.mkv
     Taille : 2.42 GB
     
  2. Jurassic Park 1993.mkv
     Taille : 3.15 GB
     
  3. Matrix Reloaded 2003.mkv
     Taille : 2.87 GB

💾 Taille totale : 28.45 GB

📐 Choisissez la qualité : 2

💡 Estimation après compression :
   Taille finale : ~9.96 GB
   Espace libéré : ~18.49 GB (65%)

🚀 Lancer la compression ? (o/N) : o

[1/12] Les Tortues ninja 2 1991.mkv
✅ Compressé : 2.42 GB → 0.85 GB (65% de réduction)
💾 Original sauvegardé : Les Tortues ninja 2 1991.mkv.original

[2/12] Jurassic Park 1993.mkv
...
```

---

## ⚙️ Paramètres de Compression

### Qualité **Moyenne** (recommandée)

```
-c:v libx264         # Codec H.264 (universel)
-preset medium       # Bon compromis vitesse/qualité
-crf 23              # Qualité excellente
-vf scale=1920:-2    # Maintient 1080p
-c:a aac             # Audio AAC
-b:a 128k            # Audio 128 kbps
-movflags +faststart # Optimisé streaming
```

**Résultat** :
- Taille : -65%
- Qualité : Imperceptible à l'œil nu
- Vitesse : ~30-60 min pour 1h de vidéo

---

## 🛡️ Sécurité

### Les originaux sont CONSERVÉS

- ✅ Fichier original renommé en `.mkv.original`
- ✅ Vous pouvez le supprimer après avoir vérifié
- ✅ Pas de perte de données

### Supprimer les .original après vérification

```powershell
# Voir tous les .original
Get-ChildItem -Recurse -Filter *.original | Select-Object FullName, @{N='Size(GB)';E={[math]::Round($_.Length/1GB,2)}}

# Supprimer tous les .original (après vérification !)
Get-ChildItem -Recurse -Filter *.original | Remove-Item -Verbose
```

---

## 📈 Comparaison Avant/Après

### Fichier MKV 2,4 GB (1080p)

| Aspect | Avant (MKV) | Après (MP4 CRF 23) |
|--------|-------------|-------------------|
| **Taille** | 2,42 GB | 0,85 GB (-65%) |
| **Format** | MKV H.264 | MP4 H.264 |
| **Résolution** | 1920x1080 | 1920x1080 |
| **Démarrage** | 20-40 secondes | **Instantané** ✅ |
| **Transcodage** | Oui (lent) | Non (direct) |
| **Qualité** | Excellente | Excellente |

### Économie d'espace (exemple réel)

```
Collection de 20 films MKV 1080p :
- Avant : 45 GB
- Après : 16 GB (CRF 23)
- Libéré : 29 GB (64%)
```

---

## ❓ FAQ

### La qualité est-elle vraiment préservée ?

**Oui** ! Avec **CRF 23**, la différence est **imperceptible à l'œil nu**. CRF (Constant Rate Factor) :
- CRF 18 = qualité quasi-lossless (énorme)
- **CRF 23 = sweet spot** (excellente qualité, taille raisonnable) ⭐
- CRF 28 = bonne qualité (plus petit)

### Combien de temps ça prend ?

**Environ 30-60 minutes par heure de vidéo** (dépend de votre processeur)

Exemple :
- Film 1h30 : ~45-90 min de compression
- Film 2h30 : ~75-150 min de compression

💡 Lancez la compression **le soir** et laissez tourner la nuit !

### Puis-je compresser d'autres formats ?

**Oui** ! Le script gère :
- MKV
- AVI
- MOV
- FLV
- WMV

Les **MP4** sont déjà optimisés, pas besoin de les recompresser.

### Quel niveau choisir ?

| Si vous avez... | Choisissez |
|-----------------|------------|
| Beaucoup d'espace disque | **Haute** (CRF 20) |
| Besoin d'économiser de l'espace | **Moyenne** (CRF 23) ⭐ |
| Peu d'espace + vieux PC | **Rapide** (CRF 26, 720p) |

---

## 🎯 Workflow Recommandé

### 1. **Test sur 1 vidéo**

```powershell
python compress_one_video.py "I:\FILM\Gros_Film.mkv"
```

Vérifiez la qualité et le temps de compression.

### 2. **Compression batch**

Si satisfait :

```powershell
python compress_large_videos.py
```

Choisissez qualité **Moyenne**, confirmez, et allez boire un café ☕

### 3. **Vérification**

Testez quelques vidéos compressées dans HomeFlix.

### 4. **Nettoyage**

Supprimez les `.original` :

```powershell
Get-ChildItem -Recurse -Filter *.original | Remove-Item
```

### 5. **Re-scan**

Relancez HomeFlix, les nouvelles MP4 seront détectées automatiquement !

---

## 💡 Astuces

### Compresser seulement les fichiers > 2 GB

Modifiez `compress_large_videos.py` ligne 127 :

```python
large_videos = scan_large_videos(video_dirs, min_size_gb=2.0)  # 1.5 → 2.0
```

### Compresser en 720p pour gagner encore plus d'espace

Utilisez le niveau **Rapide** (CRF 26, 720p) :
- Réduction : ~75%
- Qualité : Bonne (720p reste très correct)
- Idéal pour séries TV ou vieux films

### Arrêter la compression en cours

Appuyez sur **Ctrl+C** dans le terminal. Le fichier en cours sera supprimé, les précédents sont conservés.

---

## 📝 Notes Techniques

### Pourquoi MP4 et pas WebM ?

- **MP4 H.264** : Compatible 100% navigateurs
- **WebM VP9** : Meilleure compression mais support limité
- **MP4** = choix universel ✅

### Pourquoi movflags +faststart ?

Permet de **commencer à lire avant la fin du téléchargement**. Essentiel pour le streaming !

### CRF vs Bitrate fixe ?

**CRF** (Constant Rate Factor) = qualité constante, taille variable  
**Bitrate fixe** = taille prédictible, qualité variable

CRF est **meilleur pour les films** (qualité homogène).

---

## 🆘 Dépannage

### "FFmpeg non installé"

```powershell
python check_and_install_ffmpeg.py
```

### "Erreur : fichier de sortie invalide"

- Vérifiez l'espace disque disponible
- Le fichier source est peut-être corrompu

### Compression très lente

- Normal pour gros fichiers !
- Utilisez preset **"fast"** au lieu de **"medium"**
- Réduisez en 720p

### Le MP4 est pixelisé

Vous avez choisi CRF trop élevé. Recommencez avec CRF plus bas :
- CRF 26 → CRF 23
- CRF 23 → CRF 20

---

**Bon compression ! 🎬✨**
