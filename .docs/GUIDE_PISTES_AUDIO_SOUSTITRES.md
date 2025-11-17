# 🎬 Guide : Sélection des pistes audio et sous-titres

## ✅ Modification effectuée

Le backend HomeFlix **préserve maintenant TOUTES les pistes** lors du transcodage :
- 🎥 Toutes les pistes vidéo
- 🔊 Toutes les pistes audio (VF, VO, commentaires, etc.)
- 📝 Tous les sous-titres (FR, EN, JP, forcés, etc.)

### Commande FFmpeg modifiée
```bash
# AVANT (ancienne version)
-c:a aac -b:a 128k  # Ne gardait qu'UNE seule piste audio

# APRÈS (nouvelle version)
-map 0              # ✅ Copie TOUTES les pistes
-c:a aac            # Converti toutes les pistes audio en AAC
-c:s mov_text       # ✅ Converti tous les sous-titres en format MP4
```

---

## 🎮 Comment changer de piste dans le navigateur

### 🌐 Chrome / Edge / Opera
1. **Clic droit** sur la vidéo en lecture
2. Chercher le menu contextuel natif (pas celui de HomeFlix)
3. ⚠️ **LIMITATION** : Chrome ne montre PAS toujours les pistes dans le menu contextuel

**Solution alternative** :
- Appuyer sur **F12** (ouvrir DevTools)
- Console → taper :
```javascript
// Lister les pistes audio
document.querySelector('video').audioTracks

// Lister les sous-titres
document.querySelector('video').textTracks
```

### 🦊 Firefox (RECOMMANDÉ)
Firefox a le **meilleur support natif** :
1. **Clic droit** sur la vidéo
2. Menu **"Pistes audio"** → choisir la langue
3. Menu **"Sous-titres"** → activer/choisir la langue

### 🍎 Safari
Safari gère bien les pistes multiples :
1. Passer la souris sur la vidéo
2. Cliquer sur l'icône **💬** (sous-titres) en bas à droite
3. Cliquer sur l'icône **🔊** (audio) si disponible

---

## 🔧 Solution avancée : Extension navigateur

Pour un contrôle total, installez :

### Chrome/Edge
**Video ControlBar** (gratuit)
- https://chrome.google.com/webstore
- Ajoute des contrôles pour changer audio/sous-titres

### Firefox
**Video Control Extension**
- https://addons.mozilla.org/firefox/
- Menu contextuel enrichi

---

## 📋 Vérifier les pistes disponibles

### Méthode 1 : Avant compression (FFprobe)
```powershell
# Lister toutes les pistes d'un MKV
ffprobe -v quiet -show_streams -select_streams a "chemin\vers\video.mkv" | Select-String "codec_name|TAG:language|TAG:title"

# Lister les sous-titres
ffprobe -v quiet -show_streams -select_streams s "chemin\vers\video.mkv" | Select-String "codec_name|TAG:language|TAG:title"
```

### Méthode 2 : Après compression (vérifier MP4)
```powershell
# Vérifier le MP4 compressé
ffprobe -v quiet -show_streams "chemin\vers\video.mp4" | Select-String "codec_type|codec_name|TAG:language"
```

### Exemple de sortie
```
codec_type=audio
codec_name=aac
TAG:language=fre      # 🇫🇷 Piste audio française
TAG:title=VF

codec_type=audio
codec_name=aac
TAG:language=eng      # 🇬🇧 Piste audio anglaise
TAG:title=VO

codec_type=subtitle
codec_name=mov_text
TAG:language=fre      # 🇫🇷 Sous-titres français
TAG:title=Français

codec_type=subtitle
codec_name=mov_text
TAG:language=jpn      # 🇯🇵 Sous-titres japonais
TAG:title=Japanese
```

---

## 🎯 Cas d'usage typiques

### Bad Boys 3 (VF + VO)
**Avant** : Audio anglais seulement  
**Après** : 
- 🇫🇷 Piste 1 : Français (VF2)
- 🇬🇧 Piste 2 : Anglais (VO)
- 📝 Sous-titres FR disponibles

→ **Dans Firefox** : Clic droit → Pistes audio → Français

### Film japonais (VO + sous-titres)
**Avant** : Sous-titres français absents  
**Après** :
- 🇯🇵 Audio : Japonais (VO)
- 📝 Sous-titres FR
- 📝 Sous-titres EN

→ **Dans Firefox** : Clic droit → Sous-titres → Français

---

## ⚠️ Limitations connues

### Sous-titres VobSub/PGS (Blu-ray)
- Les sous-titres **image** (VobSub, PGS) ne sont **pas supportés** par MP4
- FFmpeg les **convertit automatiquement** en sous-titres texte (mov_text)
- ✅ **Avantage** : Plus légers, fonctionnent partout
- ⚠️ **Inconvénient** : Perte des styles graphiques avancés

### Sous-titres ASS/SSA (anime)
- Les styles complexes (couleurs, positions, effets) sont **simplifiés**
- Convertis en SRT/mov_text basique
- Le texte reste **100% lisible** mais sans effets

### Pistes audio multiples
- Le navigateur choisit **automatiquement** la première piste par défaut
- Ordre de priorité : langue du navigateur > première piste
- Pour **forcer une langue** : voir section "Amélioration future"

---

## 🚀 Amélioration future (optionnel)

Si vous voulez un **sélecteur intégré** dans HomeFlix (sans dépendre du navigateur), je peux ajouter :

### Option A : Boutons de sélection personnalisés
- Interface dans le lecteur HomeFlix
- Boutons "VF / VO" et "Sous-titres FR / EN / OFF"
- Nécessite JavaScript pour manipuler les pistes

### Option B : Lecteur vidéo avancé (Video.js)
- Remplacer `<video>` par Video.js
- Interface complète de gestion des pistes
- ~100 KB de librairie supplémentaire

**Voulez-vous que j'implémente l'une de ces options ?**

---

## 📝 Résumé

✅ **Backend modifié** : Toutes les pistes sont maintenant préservées  
✅ **Compression** : Les scripts `compress_*.py` gardent aussi toutes les pistes (utilisent `-map 0`)  
✅ **Firefox recommandé** : Meilleur support natif des pistes multiples  
⏳ **Chrome/Edge** : Nécessite extension ou DevTools pour sélection avancée  

**Prochaine étape** : Testez la compression de "Tortues Ninja 2" et vérifiez que toutes les pistes audio/sous-titres sont présentes !

