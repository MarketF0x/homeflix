# 💾 Gestion de l'Espace Disque - Compression

## ❓ Question Importante : Ça prend de la place où ?

### 📦 Processus Complet

#### Étape 1 : AVANT (Original seulement)
```
I:\FILM\
└── Les Tortues Ninja 2.mkv (2,4 GB)

Espace utilisé : 2,4 GB
```

#### Étape 2 : PENDANT (Les deux fichiers)
```
I:\FILM\
├── Les Tortues Ninja 2.mkv (2,4 GB)      ← Original
└── Les Tortues Ninja 2.mp4 (0,85 GB)     ← En création...

Espace utilisé : 3,25 GB (+0,85 GB temporaire)
```

**⚠️ IMPORTANT** : Vous avez besoin d'au moins **35% d'espace libre** pendant la compression !

#### Étape 3 : APRÈS compression (Backup automatique)
```
I:\FILM\
├── Les Tortues Ninja 2.mkv.original (2,4 GB)  ← Renommé
└── Les Tortues Ninja 2.mp4 (0,85 GB)          ← Active

Espace utilisé : 3,25 GB (même chose)
```

#### Étape 4 : APRÈS nettoyage (Vous supprimez .original)
```
I:\FILM\
└── Les Tortues Ninja 2.mp4 (0,85 GB)

Espace utilisé : 0,85 GB ✅ (-65% économisé !)
```

---

## 📊 Exemples Concrets

### Exemple 1 : Collection Moyenne (20 films)

**Avant compression** :
- 20 films MKV × 2 GB = **40 GB**
- Espace disque libre nécessaire : **15 GB** (pour les MP4 temporaires)

**Pendant compression** :
- Originaux : 40 GB
- MP4 en cours : 14 GB
- **Total : 54 GB** (pic maximum)

**Après compression (avec .original)** :
- Fichiers .original : 40 GB
- Fichiers .mp4 : 14 GB
- **Total : 54 GB**

**Après nettoyage (suppression .original)** :
- Fichiers .mp4 : **14 GB**
- **Économie : 26 GB** ✅

---

### Exemple 2 : Grosse Collection (100 films)

**Avant** : 200 GB (100 films × 2 GB)
**Besoin d'espace libre** : ~70 GB
**Pendant** : 270 GB (pic)
**Après nettoyage** : **70 GB** (-130 GB économisés !)

---

## ✅ Stratégies selon l'Espace Disponible

### Scénario 1 : Beaucoup d'espace (> 50% libre)

**Recommandation** : Compresser tout d'un coup

```powershell
python compress_large_videos.py
```

**Avantages** :
- ✅ Fait en une fois
- ✅ Simple
- ✅ Vous gérez le nettoyage ensuite

---

### Scénario 2 : Espace Limité (< 30% libre)

**Recommandation** : Compression par lots + nettoyage immédiat

```powershell
# Lot 1 : Compresser 5 vidéos
python compress_background.py
# Choisir option 2 (5 premières)

# Vérifier et nettoyer immédiatement
Get-ChildItem -Recurse -Filter *.original | Remove-Item

# Lot 2 : Compresser 5 autres
python compress_background.py
# ... etc
```

**Avantages** :
- ✅ Libère de l'espace progressivement
- ✅ Moins risqué
- ✅ Vous vérifiez au fur et à mesure

---

### Scénario 3 : Très Peu d'Espace (< 15% libre)

**Recommandation** : Compression fichier par fichier

```powershell
# Compresser 1 vidéo
python compress_one_video.py "chemin\video1.mkv"

# Vérifier le MP4
# Tester dans HomeFlix

# Supprimer l'original manuellement
Remove-Item "chemin\video1.mkv.original"

# Passer à la suivante
python compress_one_video.py "chemin\video2.mkv"
```

**Avantages** :
- ✅ Contrôle total
- ✅ Minimum d'espace requis
- ✅ Sécurité maximale

---

## 🧮 Calculateur d'Espace Requis

### Formule Simple

```
Espace libre nécessaire = Taille totale MKV × 0.35
```

**Exemples** :
- 10 GB de MKV → Besoin de **3,5 GB** libre
- 50 GB de MKV → Besoin de **17,5 GB** libre
- 100 GB de MKV → Besoin de **35 GB** libre

---

## 📝 Vérifier l'Espace Disponible

### PowerShell

```powershell
# Voir l'espace libre sur tous les disques
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}}, @{N='Used(GB)';E={[math]::Round($_.Used/1GB,2)}}
```

### Exemple de sortie

```
Name Free(GB) Used(GB)
---- -------- --------
C      45.23    180.77
I     150.67    349.33
H      89.12    410.88
```

---

## 🎯 Recommandations Pratiques

### ✅ CE QU'IL FAUT FAIRE

1. **Vérifier l'espace libre AVANT** de lancer la compression
2. **Tester 1-2 vidéos** avant de tout compresser
3. **Garder les .original** pendant quelques jours
4. **Vérifier la qualité** des MP4 avant de supprimer les .original
5. **Supprimer les .original** seulement quand vous êtes sûr

### ❌ CE QU'IL NE FAUT PAS FAIRE

1. ❌ Lancer la compression sans vérifier l'espace
2. ❌ Supprimer les .original immédiatement
3. ❌ Compresser sur un disque presque plein
4. ❌ Interrompre brutalement FFmpeg (Ctrl+C OK, mais pas force kill)

---

## 🔄 Workflow Recommandé (Sécurisé)

### Jour 1 : Compression

```powershell
# 1. Vérifier l'espace
Get-PSDrive I | Select-Object @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}}

# 2. Lancer compression
python compress_background.py

# 3. Aller dormir 😴
```

### Jour 2 : Vérification

```powershell
# 4. Tester 5-10 vidéos compressées dans HomeFlix
# 5. Vérifier la qualité
```

### Jour 3 : Nettoyage (si tout OK)

```powershell
# 6. Lister les .original
Get-ChildItem -Recurse -Filter *.original | Select-Object FullName, @{N='Size(GB)';E={[math]::Round($_.Length/1GB,2)}} | Format-Table

# 7. Supprimer après confirmation
Get-ChildItem -Recurse -Filter *.original | Remove-Item -Verbose
```

**Résultat** : Gain d'espace massif en toute sécurité ! 🎉

---

## 💡 Astuce : Compression Externe

**Si vraiment pas assez d'espace** : Compressez sur un autre disque !

```powershell
# Modifier compress_one_video.py pour sortie sur autre disque
python compress_one_video.py "I:\Film\Video.mkv"
# Puis dans le script, changez output_path vers "D:\Temp\..."
```

Ensuite :
1. Déplacer le MP4 vers I:\
2. Supprimer l'original MKV
3. Renommer le MP4

---

## 📊 Tableau Récapitulatif

| Collection | MKV Total | Espace Libre Requis | MP4 Final | Gain |
|------------|-----------|---------------------|-----------|------|
| Petite (10 films) | 20 GB | 7 GB | 7 GB | -13 GB |
| Moyenne (30 films) | 60 GB | 21 GB | 21 GB | -39 GB |
| Grosse (100 films) | 200 GB | 70 GB | 70 GB | -130 GB |
| Énorme (300 films) | 600 GB | 210 GB | 210 GB | -390 GB |

---

## ❓ FAQ Espace Disque

### Pourquoi garder les .original ?

**Sécurité** ! Si :
- Le MP4 est corrompu
- Vous n'aimez pas la qualité
- Problème pendant la compression

Vous pouvez restaurer l'original.

### Combien de temps garder les .original ?

**Recommandation** : 1 semaine

Ça vous laisse le temps de :
- Tester toutes les vidéos
- Vérifier la qualité
- Être sûr que tout fonctionne

### Et si je manque d'espace pendant la compression ?

**FFmpeg s'arrêtera** avec une erreur. Le fichier MP4 incomplet sera supprimé automatiquement. Pas de danger !

### Puis-je compresser vers un autre disque ?

**Oui** ! Modifiez juste `output_path` dans les scripts pour pointer vers un autre disque avec plus d'espace.

---

**En résumé** : OUI ça prend de la place pendant, mais c'est TEMPORAIRE. Une fois les .original supprimés, vous ÉCONOMISEZ 65% ! 🎉
