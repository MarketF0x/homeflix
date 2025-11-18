# Guide des Assets - Logo et Screenshots

**Date:** 18 novembre 2025

## 🎨 Logo Homeflix

### Recommandations

**Dimensions recommandées:**
- Logo principal: 512x512 px (PNG avec transparence)
- Favicon: 32x32 px, 64x64 px
- App icon (Electron): 256x256 px, 512x512 px, 1024x1024 px

**Style suggéré:**
- Icône de maison (🏠) avec symbole play (▶️)
- Couleurs: Bleu moderne (#2563eb) et accent (#f59e0b)
- Design minimaliste et professionnel
- Arrière-plan transparent pour polyvalence

**Fichiers à créer:**
```
homeflix/
├── public/
│   ├── logo.svg              # Logo vectoriel
│   ├── logo-512.png          # Logo principal
│   ├── logo-256.png          # Taille moyenne
│   ├── favicon.ico           # Favicon navigateur
│   └── favicon-32.png        # Favicon moderne
├── electron/
│   └── icon.png              # Icône app (512x512)
└── docs/
    └── images/
        ├── logo-banner.png   # Pour README (1200x400)
        └── screenshots/      # Captures d'écran
```

## 📸 Screenshots Recommandés

### 1. Page d'accueil
**Nom:** `homepage.png`  
**Description:** Vue d'ensemble avec cartes vidéos, carrousels, navigation
**Taille:** 1920x1080 px

### 2. Lecteur vidéo
**Nom:** `video-player.png`  
**Description:** Interface du lecteur avec contrôles, sous-titres
**Taille:** 1920x1080 px

### 3. Page de détails
**Nom:** `video-details.png`  
**Description:** Informations film, synopsis, métadonnées TMDB
**Taille:** 1920x1080 px

### 4. Collections
**Nom:** `collections.png`  
**Description:** Gestion des collections personnalisées
**Taille:** 1920x1080 px

### 5. Paramètres
**Nom:** `settings.png`  
**Description:** Interface de configuration, profils
**Taille:** 1920x1080 px

### 6. Vue mobile (optionnel)
**Nom:** `mobile-view.png`  
**Description:** Interface responsive sur mobile
**Taille:** 750x1334 px

## 🛠️ Outils de Création

### Logo
- **Figma** (gratuit) - https://figma.com
- **Canva** (gratuit) - https://canva.com
- **GIMP** (gratuit, open source)
- **Adobe Illustrator** (payant)

### Screenshots
1. **Lancer Homeflix** en mode production
2. **Naviguer** vers les pages importantes
3. **Captures d'écran:**
   - Windows: `Win + Shift + S`
   - Mac: `Cmd + Shift + 4`
   - Extension navigateur: "Awesome Screenshot"

### Optimisation Images
```bash
# Optimiser PNG (lossless)
python optimize_images.py

# Ou manuellement avec TinyPNG
# https://tinypng.com
```

## 📝 Intégration README

Une fois les assets créés, mettez à jour `README.md`:

```markdown
<p align="center">
  <img src="docs/images/logo-banner.png" alt="Homeflix Logo" width="600"/>
</p>

## 📸 Aperçu

<p align="center">
  <img src="docs/images/screenshots/homepage.png" alt="Page d'accueil" width="800"/>
</p>

### Fonctionnalités

<table>
  <tr>
    <td><img src="docs/images/screenshots/video-player.png" width="400"/></td>
    <td><img src="docs/images/screenshots/video-details.png" width="400"/></td>
  </tr>
  <tr>
    <td align="center"><b>Lecteur Vidéo</b></td>
    <td align="center"><b>Détails & Métadonnées</b></td>
  </tr>
</table>
```

## 🎯 Checklist Assets

- [ ] Logo SVG créé
- [ ] Logo PNG 512x512
- [ ] Favicon généré
- [ ] Icône Electron 512x512
- [ ] Screenshot: Page d'accueil
- [ ] Screenshot: Lecteur vidéo
- [ ] Screenshot: Détails vidéo
- [ ] Screenshot: Collections
- [ ] Screenshot: Paramètres
- [ ] Images optimisées (< 500 KB chacune)
- [ ] README mis à jour avec images
- [ ] Commit git avec assets

## 🚀 Déploiement

Une fois les assets prêts:

```bash
# Ajouter au git
git add public/logo* docs/images/

# Commit
git commit -m "feat: Add professional logo and screenshots"

# Push
git push origin dev
```

## 💡 Ressources Gratuites

**Icônes:**
- https://heroicons.com
- https://fontawesome.com
- https://icons8.com

**Palettes de couleurs:**
- https://coolors.co
- https://colorhunt.co

**Inspiration logo:**
- https://dribbble.com (rechercher "media server logo")
- https://logopond.com
