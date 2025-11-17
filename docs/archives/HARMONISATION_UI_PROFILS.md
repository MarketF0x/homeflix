# Harmonisation UI - Système de Profils

## Vue d'ensemble
Toutes les interfaces du système de gestion de profils ont été harmonisées pour créer une expérience visuelle cohérente avec le reste de l'application Homeflix.

## Palette de couleurs unifiée

### Couleurs principales
- **Violet primaire**: `#7c3aed` → `#a78bfa` (dégradés)
- **Violet secondaire**: `rgba(167, 139, 250, 0.x)` (transparences)
- **Fond sombre**: `#0a0a0a` → `#1a1a2e`
- **Backgrounds modales**: `rgba(26, 26, 46, 0.95)` avec backdrop-filter

### Effets visuels
- Dégradés linéaires cohérents à 135deg
- Ombres portées avec glow violet
- Animations fluides (fadeIn, slideUp, slideDown)
- Backdrop-filter blur(10-20px)

## Composants harmonisés

### 1. ProfileSelector (Écran de sélection)

#### Fond d'écran
```css
background: radial-gradient(ellipse at center, rgba(124, 58, 237, 0.15) 0%, #0a0a0a 100%),
            linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
```

#### Titre principal
- Dégradé de texte blanc → violet
- Effet text-shadow avec glow violet
- Animation slideDown au chargement

#### Cartes de profil
- Bordure violet clair par défaut (`rgba(167, 139, 250, 0.3)`)
- Au survol : bordure violet vif + box-shadow avec glow
- Transform translateY(-5px) au hover
- Icône cadenas animée (lockPulse) pour profils protégés

#### Carte "Ajouter un profil"
- Bordure en pointillés violet
- Icône + qui tourne de 90° au survol
- Fond en dégradé violet transparent

#### Badge "Principal"
- Dégradé violet `#7c3aed` → `#a78bfa`
- Box-shadow violet

#### Bouton "Gérer les profils"
- Style cohérent avec boutons primaires
- Bordure et fond violet avec transparence
- Glow au survol

### 2. PasswordPrompt (Modal de mot de passe)

#### Overlay
```css
background: radial-gradient(ellipse at center, rgba(124, 58, 237, 0.2) 0%, rgba(0, 0, 0, 0.95) 100%);
backdrop-filter: blur(10px);
```

#### Container
- Bordure violet `rgba(167, 139, 250, 0.2)`
- Box-shadow double (noir + violet glow)
- Animation slideUp avec scale

#### Titre
- Même dégradé de texte que ProfileSelector
- Taille 26px, font-weight 700

#### Inputs
- Bordure violet `rgba(167, 139, 250, 0.3)`
- Focus : bordure violet vif + glow shadow
- Background transparent avec légère opacité

#### Question secrète
- Fond dégradé violet transparent
- Bordure violet
- Box-shadow violet subtile

#### Message d'erreur
- Dégradé rouge transparent
- Animation shake
- Box-shadow rouge

#### Boutons
- Primaire : dégradé violet avec glow au survol
- Secondaire : fond transparent avec bordure

### 3. ProfileManager (Gestionnaire de profils)

#### Modal
- Même style d'overlay que PasswordPrompt
- Container avec backdrop-filter blur(20px)
- Border-radius 20px
- Scrollbar personnalisée avec dégradé violet

#### Header
- Background dégradé violet transparent
- Bordure inférieure violet
- Titre avec dégradé de texte

#### Bouton de fermeture (✕)
- Cercle avec bordure violet
- Rotation de 90° au survol
- Glow violet

#### Liste de profils
- Items avec fond dégradé violet transparent
- Bordure violet
- Hover : translation X + box-shadow violet
- Avatar avec bordure violet

#### Formulaire
- Inputs avec même style que PasswordPrompt
- Select personnalisé avec flèches violettes
- Avatar sélectionné : bordure + glow violet + scale

#### Checkboxes de restrictions
- Hover : fond + bordure violet transparent

#### Boutons d'action
- Primaire : dégradé violet #7c3aed → #a78bfa
- Box-shadow avec glow au survol
- Transform translateY(-2px)

## Animations

### Keyframes définies
```css
@keyframes fadeIn { 0% → 100% opacity }
@keyframes slideUp { transform + scale }
@keyframes slideDown { translateY }
@keyframes fadeInUp { opacity + translateY }
@keyframes lockPulse { scale pulse infini }
@keyframes shake { translateX pour erreurs }
```

## Scrollbars personnalisées

### ProfileManager container
- Width: 8px
- Track: noir transparent
- Thumb: dégradé violet

### Liste de profils
- Width: 6px
- Même style de dégradé violet

## Responsive

### Mobile (max-width: 768px)
- Titre réduit à 2.5rem
- Grid de profils : min 140px
- Avatar wrapper : 140px
- Modal plein écran (border-radius 0)
- Avatar grid : min 60px

## Cohérence avec l'application

Tous les éléments du système de profils respectent maintenant :
- ✅ La palette de couleurs violet/noir de Homeflix
- ✅ Les effets de glow et shadow cohérents
- ✅ Les animations fluides et professionnelles
- ✅ Les transitions douces (0.3s ease)
- ✅ Le backdrop-filter pour effet glassmorphism
- ✅ Les dégradés à 135deg
- ✅ Les border-radius arrondis (8-20px)
- ✅ La typographie avec dégradés de texte

## Fichier modifié
`client/src/index.css` - Sections concernées :
- Profile Selector (lignes 57-160)
- Password Prompt (lignes 214-370)
- Profile Manager (lignes 372-710)
- Animations et keyframes ajoutées
- Styles responsive

## Résultat
Une interface utilisateur homogène, moderne et professionnelle qui s'intègre parfaitement au design global de Homeflix, avec une identité visuelle forte basée sur les tons violets et une expérience utilisateur fluide grâce aux animations et transitions.
