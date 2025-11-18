# 🔧 Correctif - Erreur "Failed to open media" lors du transcodage

## Problème identifié

L'erreur montre clairement :
```
ReadyState: 0, NetworkState: 3
Erreur: Failed to open media
```

**NetworkState: 3 = NETWORK_NO_SOURCE** - Le serveur FFmpeg ne parvient **PAS** à fournir le flux vidéo.

### Logs observés
```
❌ Erreur : Impossible de décoder la vidéo même en transcodage. Vérifiez FFmpeg sur le serveur.
⚠️ Vidéo bloquée détectée (7/15) - Position: 8s, ReadyState: 0, NetworkState: 3
   Buffer: 0s, Erreur: Failed to open media
```

## Causes possibles

### 1. Fichier vidéo introuvable
Le chemin contient des parenthèses ou caractères spéciaux :
```
I:\FILM\Les Tortues Ninja Trilogie (1990-199...
```

Les parenthèses `()` peuvent causer des problèmes :
- URL encoding/decoding
- Échappement de caractères dans la commande FFmpeg
- Chemin Windows avec espaces

### 2. FFmpeg ne peut pas ouvrir le fichier
- Permissions insuffisantes
- Fichier verrouillé par un autre programme
- Chemin trop long (> 260 caractères sur Windows)
- Codecs du fichier corrompus

### 3. Erreur au lancement de FFmpeg
- FFmpeg crash avant d'envoyer des données
- Paramètres invalides dans la commande
- Mapping audio/vidéo incorrect

## Corrections apportées

### 1. Logs de diagnostic détaillés côté serveur

Ajout de logs pour identifier précisément le problème :

```python
logger.info(f"[VIDEO] TRANSCODAGE demandé")
logger.info(f"   Chemin reçu: {path}")
logger.info(f"   Chemin normalisé: {video_path}")
logger.info(f"   Fichier existe: {video_path.exists()}")

if not video_path.exists():
    logger.error(f"   ❌ FICHIER INTROUVABLE!")
    logger.error(f"   Chemin complet: {video_path.absolute()}")
    logger.error(f"   Dossier parent: {video_path.parent}")
    logger.error(f"   Parent existe: {video_path.parent.exists()}")
```

### 2. Affichage complet de la commande FFmpeg

```python
logger.info(f"   Commande complète:")
for i, arg in enumerate(ffmpeg_cmd):
    if i % 10 == 0 and i > 0:
        logger.info(f"      {' '.join(ffmpeg_cmd[i:i+10])}")
```

### 3. Gestion d'erreur au lancement de FFmpeg

```python
try:
    process = popen_hidden(ffmpeg_cmd, ...)
except Exception as e:
    logger.error(f"❌ [FFMPEG] Impossible de démarrer le processus: {e}")
    raise HTTPException(status_code=500, detail=f"Erreur démarrage FFmpeg: {e}")
```

### 4. Logs détaillés des erreurs FFmpeg stderr

Les 10 dernières lignes d'erreur de FFmpeg seront affichées dans les logs serveur.

## Diagnostic - Étapes suivantes

### Étape 1 : Vérifier les logs du serveur Python

Le serveur Python (port 8000) devrait maintenant afficher des logs détaillés. 

**Où voir les logs :**
- Si lancé dans un terminal : Les logs s'affichent directement
- Si lancé en arrière-plan : Vérifier le fichier de logs ou le terminal d'origine

**Chercher ces lignes :**
```
[VIDEO] TRANSCODAGE demandé
   Chemin reçu: I:\FILM\Les Tortues Ninja Trilogie (1990-199...
   Fichier existe: True/False
```

### Étape 2 : Redémarrer le serveur avec les nouveaux logs

Pour que les nouveaux logs soient actifs :

```powershell
# Arrêter le serveur actuel
Stop-Process -Id 25216

# Relancer le serveur
cd C:\Users\fparo\Desktop\homeflix
.\homeflix.ps1
```

Ou en mode développement :
```powershell
.\homeflix-dev.ps1
```

### Étape 3 : Tester une vidéo

1. Ouvrez la console navigateur (F12)
2. Lancez la vidéo problématique
3. **Observez les logs du serveur Python** dans le terminal

Vous devriez voir :
```
[VIDEO] TRANSCODAGE demandé
   Chemin reçu: I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\Teenage Mutant Ninja Turtles (1990).mkv
   Chemin normalisé: I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\Teenage Mutant Ninja Turtles (1990).mkv
   Fichier existe: True
   ✅ Fichier trouvé - Taille: 1234.5 MB
   
[PROCESS] Lancement FFmpeg - Mode: TRANSCODAGE (libx264)
   Commande complète:
      ffmpeg -analyzeduration 20M -probesize 20M -fflags +genpts+igndts -i I:\FILM\...
      ...
   Fichier source: I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\Teenage Mutant Ninja Turtles (1990).mkv
```

**SI le fichier n'existe pas :**
```
   ❌ FICHIER INTROUVABLE!
   Chemin complet: I:\FILM\...
   Dossier parent: I:\FILM\...
   Parent existe: True/False
```

**SI FFmpeg crash :**
```
❌ [FFMPEG] Arrêt prématuré (rc=1). Détails:
   [error message from FFmpeg]
```

### Étape 4 : Solutions selon l'erreur

#### Si "FICHIER INTROUVABLE"
1. Vérifier que le disque `I:` est bien monté
2. Vérifier les permissions sur le dossier
3. Vérifier que le fichier n'a pas été déplacé/renommé
4. Re-scanner la bibliothèque

#### Si "FFmpeg crash"
1. Tester manuellement la commande FFmpeg affichée dans les logs
2. Vérifier les codecs du fichier : `ffprobe "chemin\fichier.mkv"`
3. Tester un transcodage simple :
```powershell
ffmpeg -i "I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\file.mkv" -t 10 -c:v libx264 -c:a aac test.mp4
```

#### Si "Problème de caractères spéciaux"
Les parenthèses dans le nom de dossier peuvent poser problème. Essayez de :
1. Renommer le dossier temporairement (enlever les parenthèses)
2. Re-scanner la bibliothèque
3. Tester à nouveau

## Test manuel FFmpeg

Pour vérifier si FFmpeg peut lire le fichier :

```powershell
# Test 1 : Afficher les infos
ffprobe "I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\fichier.mkv"

# Test 2 : Transcoder 10 secondes
ffmpeg -i "I:\FILM\Les Tortues Ninja Trilogie (1990-1993)\fichier.mkv" `
  -t 10 `
  -c:v libx264 -preset fast -crf 23 `
  -c:a aac -b:a 128k `
  -f mp4 test.mp4

# Si ça fonctionne, le problème vient d'ailleurs
# Si ça échoue, regarder le message d'erreur FFmpeg
```

## Fichiers modifiés

- `server/main.py` :
  - Logs détaillés du chemin vidéo reçu
  - Logs de la commande FFmpeg complète
  - Gestion d'erreur au lancement de FFmpeg
  - Affichage des erreurs stderr de FFmpeg

## Prochaines étapes

1. ✅ Redémarrer le serveur Python
2. ✅ Lancer la vidéo problématique
3. ✅ **Partager les logs du serveur Python** pour diagnostic précis
4. ✅ Tester manuellement FFmpeg si nécessaire

Les nouveaux logs vont révéler exactement où le problème se situe !
