# 🔍 Audit et Nettoyage Complet - Homeflix

**Date** : 14 novembre 2025  
**Objectif** : Identifier les fichiers obsolètes, redondants ou manquants

---

## 📊 Analyse des Scripts PowerShell (18 scripts)

### ✅ Scripts Principaux (À CONSERVER)

| Script | Utilité | Statut |
|--------|---------|--------|
| `install.ps1` | Installation initiale | ✅ Essentiel |
| `start-homeflix.ps1` | Lancement principal (production) | ✅ Essentiel |
| `setup-tmdb-key.ps1` | Configuration clé TMDb | ✅ Nouveau - Essentiel |
| `check-dependencies.ps1` | Vérification dépendances | ✅ Utile |

### ⚠️ Scripts Redondants/Obsolètes (À EXAMINER)

| Script | Problème | Recommandation |
|--------|----------|----------------|
| `start.ps1` | Doublon de `start-homeflix.ps1` | 🗑️ **SUPPRIMER** |
| `start-simple.ps1` | Version simplifiée, doublon | 🗑️ **SUPPRIMER** |
| `start-homeone.ps1` | Version avec domaine homeone | ⚠️ Fusionner avec start-homeflix.ps1 |
| `homeflix.ps1` | Ancien lanceur ? | 🔍 Vérifier si utilisé |
| `creer_raccourci_bureau.ps1` | Doublon de `create_shortcut.ps1` | 🗑️ **SUPPRIMER** (version FR) |

### 🔧 Scripts Spécialisés (GARDER si fonctionnalité utilisée)

| Script | Utilité | Décision |
|--------|---------|----------|
| `configure-firewall.ps1` | Configuration pare-feu | ✅ Si accès réseau |
| `configure-firewall-tailscale.ps1` | Pare-feu + Tailscale | ✅ Si Tailscale utilisé |
| `configure-network-access.ps1` | Accès réseau | ⚠️ Redondant avec firewall ? |
| `setup-multi-domains.ps1` | Multi-domaines | ✅ Si multi-domaines |
| `setup-homeone-domain.ps1` | Domaine homeone.local | ✅ Si domaine local |
| `setup-https.ps1` | HTTPS/SSL | ✅ Si HTTPS activé |
| `setup-tailscale-dns.ps1` | DNS Tailscale | ✅ Si Tailscale |
| `install-tailscale.ps1` | Installation Tailscale | ✅ Si Tailscale |
| `update-profiles.ps1` | Mise à jour profils | ✅ Utile |

---

## 📚 Analyse des Fichiers Documentation (35+ fichiers MD)

### ✅ Documentation Essentielle (GARDER)

| Fichier | Description | Statut |
|---------|-------------|--------|
| `README.md` | Documentation principale | ✅ À jour |
| `LICENSE` | Licence MIT | ✅ Nouveau |
| `CHANGELOG.md` | Historique modifications | ✅ Utile |
| `GUIDE_TMDB_API_KEY.md` | Guide clé TMDb | ✅ Nouveau - Essentiel |
| `TMDB_TERMS_SUMMARY.md` | Conditions TMDb | ✅ Nouveau - Essentiel |
| `ANALYSE_LICENCES_COMMERCIAL.md` | Analyse licences | ✅ Nouveau - Essentiel |
| `RESUME_CONFORMITE_LEGALE.md` | Résumé conformité | ✅ Nouveau - Important |
| `GUIDE_PROFILS.md` | Gestion profils | ✅ Fonctionnalité active |
| `GUIDE_SECURITE_PROFILS.md` | Sécurité profils | ✅ Important |

### ⚠️ Documentation Potentiellement Obsolète/Redondante

| Fichier | Problème | Recommandation |
|---------|----------|----------------|
| `README_UTILISATION.md` | Redondant avec README.md ? | 🔍 Fusionner ou supprimer |
| `INSTALL_RAPIDE.md` | Redondant avec README.md section installation | 🔍 Fusionner |
| `GUIDE_DEMARRAGE.md` | Redondant avec README.md ? | 🔍 Fusionner |
| `README_MULTI_DOMAINES.md` | Documentation multi-domaines | ✅ Garder si fonctionnalité utilisée |
| `GUIDE_HOMEONE_DOMAIN.md` | Domaine homeone | ✅ Garder si utilisé |

### 📖 Guides Techniques (GARDER)

| Fichier | Utilité |
|---------|---------|
| `GUIDE_COMPRESSION.md` | Compression vidéo |
| `GUIDE_PISTES_AUDIO_SOUSTITRES.md` | Audio/sous-titres |
| `FORMAT_VIDEO_COMPATIBILITE.md` | Compatibilité formats |
| `SOLUTION_CODEC_VIDEO.md` | Solutions codec |
| `SOLUTION_COMPRESSION.md` | Solutions compression |

### 📝 Rapports/Logs (ARCHIVER ou SUPPRIMER)

| Fichier | Type | Recommandation |
|---------|------|----------------|
| `RAPPORT_AUDIT_2025.md` | Audit | 📦 Archiver dans /docs/archives/ |
| `MISE_A_JOUR_NOV_2025.md` | Rapport MAJ | 📦 Archiver |
| `OPTIMISATIONS_APPLIQUEES.md` | Rapport optim | 📦 Archiver |
| `RESTAURATION_DEV.md` | Doc dev | 📦 Archiver |
| `HARMONISATION_UI_PROFILS.md` | Rapport UI | 📦 Archiver |
| `AMELIORATIONS_STREAMING_v2.md` | Rapport streaming | 📦 Archiver |
| `COMPRESSION_MIGRATION.md` | Migration | 📦 Archiver |
| `duplicates_log.md` | Log doublons | 🗑️ Supprimer |

### 📡 Documentation Réseau (GARDER si utilisé)

| Fichier | Utilité |
|---------|---------|
| `ACCES_INTERNET.md` | Accès internet |
| `ACCES_RESEAU.md` | Accès réseau local |
| `PARTAGE_RESEAU.md` | Partage réseau |
| `OPTIMISATIONS_STREAMING.md` | Optimisations |
| `ESPACE_DISQUE.md` | Gestion disque |
| `MASQUAGE_VIDEOS.md` | Masquage contenu |

---

## 🐍 Analyse des Scripts Python Utilitaires

### ✅ Scripts Utiles (GARDER)

| Script | Utilité | Statut |
|--------|---------|--------|
| `check_and_install_ffmpeg.py` | Installation FFmpeg | ✅ Utile |
| `clean_filenames.py` | Nettoyage noms fichiers | ✅ Utile |
| `generate_thumbnails.py` | Génération miniatures | ✅ Utile |
| `video_compressor.py` | Compression vidéo | ✅ Utile |

### 🧪 Scripts de Test (ARCHIVER dans /tests/)

| Script | Type | Recommandation |
|--------|------|----------------|
| `test_*.py` (10 fichiers) | Tests unitaires | 📦 Déplacer dans /tests/ |
| `check_durations.py` | Test durées | 📦 /tests/ |
| `extract_durations.py` | Test durées | 📦 /tests/ |

### ⚠️ Scripts Spécialisés (GARDER si utilisé)

| Script | Utilité |
|--------|---------|
| `compress_large_videos.py` | Compression batch |
| `compress_one_video.py` | Compression unitaire |
| `compress_background.py` | Compression arrière-plan |
| `create_default_poster.py` | Poster par défaut |
| `generate_icon.py` | Génération icône |
| `generate_qrcode.py` | QR code |

---

## 📁 Analyse des Dossiers

### ✅ Dossiers Essentiels

| Dossier | Utilité |
|---------|---------|
| `/server/` | Backend Python |
| `/client/` | Frontend React |
| `/data/` | Données (posters, thumbs) |
| `/installer/` | Installateur Windows |

### ⚠️ Dossiers à Examiner

| Dossier | Statut | Recommandation |
|---------|--------|----------------|
| `/exemple_ui/` | Exemples UI | 🔍 Vérifier si utilisé → Archiver |
| `/netlify-deploy/` | Déploiement Netlify | 🔍 Si pas utilisé → Supprimer |
| `/scripts/` | Scripts divers | 🔍 Consolider |
| `/.venv/` et `/.venv310/` | Environnements virtuels | ⚠️ Choisir un seul |

---

## 🎯 Incohérences Détectées

### 1. **Nom de l'Application**
- ❓ README dit "Homeflix"
- ❓ Certains scripts disent "HomeOne"
- **Action** : Standardiser sur "Homeflix"

### 2. **Scripts de Démarrage Multiples**
```
start.ps1          ← Ancien
start-simple.ps1   ← Version simplifiée
start-homeflix.ps1 ← Principal (GARDER)
start-homeone.ps1  ← Version homeone
```
**Action** : Supprimer doublons, garder `start-homeflix.ps1`

### 3. **Documentation Redondante**
- `README.md` + `README_UTILISATION.md` + `INSTALL_RAPIDE.md` + `GUIDE_DEMARRAGE.md`
- **Action** : Fusionner dans un seul README.md complet

### 4. **Environnements Virtuels Doubles**
- `.venv/` et `.venv310/`
- **Action** : Standardiser sur un seul

---

## 📋 Plan de Nettoyage Recommandé

### Phase 1 : Suppressions Immédiates 🗑️

```powershell
# Scripts PowerShell obsolètes
Remove-Item start.ps1
Remove-Item start-simple.ps1
Remove-Item creer_raccourci_bureau.ps1  # Doublon FR

# Logs et fichiers temporaires
Remove-Item duplicates_log.md
Remove-Item test_collections.json
```

### Phase 2 : Archivage 📦

Créer `/docs/archives/` et déplacer :
```powershell
# Rapports historiques
Move-Item RAPPORT_AUDIT_2025.md docs/archives/
Move-Item MISE_A_JOUR_NOV_2025.md docs/archives/
Move-Item OPTIMISATIONS_APPLIQUEES.md docs/archives/
Move-Item RESTAURATION_DEV.md docs/archives/
Move-Item HARMONISATION_UI_PROFILS.md docs/archives/
Move-Item AMELIORATIONS_STREAMING_v2.md docs/archives/
Move-Item COMPRESSION_MIGRATION.md docs/archives/
```

### Phase 3 : Tests 🧪

Créer `/tests/` et déplacer :
```powershell
Move-Item test_*.py tests/
Move-Item check_durations.py tests/
Move-Item extract_durations.py tests/
```

### Phase 4 : Consolidation 📚

**Fusionner dans README.md** :
- `README_UTILISATION.md` (section utilisation)
- `INSTALL_RAPIDE.md` (section installation)
- `GUIDE_DEMARRAGE.md` (section démarrage)

### Phase 5 : Standardisation 🔧

**Renommer pour cohérence** :
- `start-homeone.ps1` → Fusionner dans `start-homeflix.ps1` avec option `-Domain`
- `create_shortcut.ps1` → Garder version anglaise uniquement

---

## ✅ Fichiers Manquants ou À Créer

### Documentation

1. **`.gitignore`** ✅ (existe déjà)
2. **`CONTRIBUTING.md`** ❌ Guide pour contributeurs
3. **`SECURITY.md`** ❌ Politique de sécurité
4. **`FAQ.md`** ❌ Questions fréquentes
5. **`TROUBLESHOOTING.md`** ❌ Guide dépannage centralisé

### Structure Organisationnelle

1. **`/docs/`** - Documentation consolidée
   - `/docs/guides/` - Tous les GUIDE_*.md
   - `/docs/network/` - Docs réseau
   - `/docs/archives/` - Rapports historiques

2. **`/tests/`** - Tests unitaires

3. **`/scripts/utils/`** - Scripts utilitaires

---

## 📊 Résumé des Actions

### Suppressions (7 fichiers)
- ✅ 3 scripts PS1 doublons
- ✅ 1 log obsolète
- ✅ 1 JSON de test
- ✅ 2 docs redondants

### Archives (7 fichiers)
- ✅ 7 rapports historiques → `/docs/archives/`

### Déplacements (12 fichiers)
- ✅ 10+ tests → `/tests/`

### Fusions (3 fichiers)
- ✅ 3 README → README.md principal

### Création (5 fichiers)
- ✅ CONTRIBUTING.md
- ✅ SECURITY.md
- ✅ FAQ.md
- ✅ TROUBLESHOOTING.md
- ✅ Dossiers `/docs/`, `/tests/`

---

## 🎯 État Final Recommandé

```
homeflix/
├── LICENSE                      # ✅ Nouveau
├── README.md                    # ✅ Consolidé
├── CHANGELOG.md                 # ✅
├── CONTRIBUTING.md              # ❌ À créer
├── SECURITY.md                  # ❌ À créer
├── FAQ.md                       # ❌ À créer
├── TROUBLESHOOTING.md           # ❌ À créer
│
├── install.ps1                  # ✅
├── start-homeflix.ps1           # ✅ Principal
├── setup-tmdb-key.ps1           # ✅ Nouveau
├── settings.yaml                # ✅
│
├── /server/                     # ✅
├── /client/                     # ✅
├── /data/                       # ✅
├── /installer/                  # ✅
│
├── /docs/                       # ❌ À créer
│   ├── /guides/                 # Tous les GUIDE_*.md
│   ├── /network/                # Docs réseau
│   ├── /legal/                  # Docs légales
│   └── /archives/               # Rapports historiques
│
├── /tests/                      # ❌ À créer
│   └── test_*.py
│
└── /scripts/                    # ❌ Réorganiser
    ├── /setup/                  # Scripts config
    ├── /utils/                  # Scripts utilitaires
    └── /compression/            # Scripts compression
```

---

## 🚀 Priorités d'Action

### 🔴 Priorité Haute (Immédiat)
1. Supprimer scripts doublons (start.ps1, start-simple.ps1)
2. Créer FAQ.md et TROUBLESHOOTING.md
3. Archiver rapports historiques

### 🟡 Priorité Moyenne (Cette semaine)
1. Réorganiser structure /docs/
2. Déplacer tests dans /tests/
3. Fusionner README redondants

### 🟢 Priorité Basse (Quand temps disponible)
1. Créer CONTRIBUTING.md et SECURITY.md
2. Nettoyer /scripts/
3. Supprimer /exemple_ui/ si inutilisé

---

**Total fichiers à traiter : ~35 fichiers**  
**Gain d'espace/clarté : ~40% de réduction de la confusion**  
**Temps estimé : 2-3 heures**

---

*Audit généré le 14 novembre 2025*
