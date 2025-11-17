# Scripts de Compression - Migration

## ⚠️ OBSOLÈTE - Fichiers Consolidés

Les 3 scripts suivants ont été **consolidés** en un seul module unifié :
- ❌ `compress_one_video.py` (obsolète)
- ❌ `compress_large_videos.py` (obsolète)  
- ❌ `compress_background.py` (obsolète)

## ✅ Nouveau Module Unifié

**Utiliser désormais : `video_compressor.py`**

### Usage

#### 1. Compresser une vidéo unique
```bash
python video_compressor.py compress "chemin/video.mkv" --quality medium
```

Options :
- `--quality` : `high`, `medium`, `fast`
- `--output` : Fichier de sortie personnalisé
- `--overwrite` : Écraser si existe

#### 2. Compresser en batch (gros fichiers du catalogue)
```bash
python video_compressor.py batch --min-size 2.0 --quality medium --limit 10
```

Options :
- `--min-size` : Taille minimale en GB (défaut: 1.5)
- `--quality` : Niveau de qualité
- `--limit` : Limiter le nombre de fichiers

#### 3. Mode daemon (arrière-plan automatique)
```bash
python video_compressor.py daemon --interval 3600
```

Options :
- `--interval` : Intervalle en secondes (défaut: 3600 = 1h)
- `--min-size` : Taille minimale
- `--quality` : Niveau de qualité

## Avantages de la Consolidation

✅ **Un seul fichier** à maintenir  
✅ **Interface CLI cohérente**  
✅ **Meilleure gestion d'erreurs**  
✅ **Code DRY** (pas de duplication)  
✅ **Logging amélioré**

## Migration

Si vous aviez des scripts ou tâches planifiées utilisant les anciens fichiers :

**Ancien :**
```bash
python compress_one_video.py "video.mkv"
```

**Nouveau :**
```bash
python video_compressor.py compress "video.mkv"
```

---

**Ancien :**
```bash
python compress_background.py
```

**Nouveau :**
```bash
python video_compressor.py daemon
```
