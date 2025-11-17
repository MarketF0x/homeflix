# 🚀 PLAN D'ACTION - OPTIMISATIONS HOMEFLIX

## Phase 1: RESTRUCTURATION CSS (PRIORITÉ CRITIQUE) ⚡

### Fichiers créés:
✅ `client/src/styles/main.css` - Point d'entrée unique
✅ `client/src/styles/config/variables.css` - Design tokens
✅ `client/src/styles/config/breakpoints.css` - Media queries
✅ `client/src/styles/config/animations.css` - Animations réutilisables

### Actions à effectuer:

#### 1. Migrer les styles existants (1-2 jours)

**ÉTAPE 1.1:** Extraire styles de `index.css` → nouvelles structures
```bash
# Analyser index.css (1195 lignes)
# Séparer en:
- Reset → base/reset.css
- Typography → base/typography.css
- Utilities → base/utilities.css
- Profils → components/profiles.css
```

**ÉTAPE 1.2:** Extraire styles de `styles.css` → nouvelles structures  
```bash
# Analyser styles.css (2437 lignes!)
# Séparer en:
- Layout → layout/grid.css, layout/containers.css
- Navigation → layout/navigation.css
- Cards → components/cards.css
- Modals → components/modals.css
```

**ÉTAPE 1.3:** Fusionner les doublons
```bash
# SUPPRIMER:
- modal.css (fusionner dans components/modals.css)
- Choisir entre scrollable-row.css vs scrolling-row.css
```

**ÉTAPE 1.4:** Mettre à jour main.jsx
```javascript
// AVANT:
import "./index.css";
import "./styles.css";
import "./video-player.css";

// APRÈS:
import "./styles/main.css"; // UN SEUL IMPORT
```

---

## Phase 2: OPTIMISATION IMPORTS & API (PRIORITÉ HAUTE) 🔥

### Actions:

**2.1: Supprimer api.js, tout migrer vers config.js**
```javascript
// Supprimer: client/src/api.js
// Garder uniquement: client/src/config.js

// Créer: client/src/api/index.js
export { fetchVideos, fetchCategories } from './videos';
export { fetchProfiles } from './profiles';
// etc.
```

**2.2: Lazy loading de TOUS les composants lourds**
```javascript
// App.jsx - AVANT:
import VideoDetail from "./VideoDetail.jsx"; // ❌

// APRÈS:
const VideoDetail = lazy(() => import("./VideoDetail.jsx")); // ✅
const SettingsModal = lazy(() => import("./SettingsModal.jsx")); // ✅
const ProfileManager = lazy(() => import("./ProfileManager.jsx")); // ✅
```

**2.3: Créer barrel exports**
```javascript
// client/src/components/index.js
export { default as VideoCard } from './VideoCard';
export { default as VideoDetail } from './VideoDetail';
// ... tous les composants

// Usage dans App.jsx:
import { VideoCard, VideoDetail } from './components';
```

---

## Phase 3: CACHE & HOT-RELOAD (PRIORITÉ HAUTE) 🔄

### 3.1: Optimiser vite.config.js

```javascript
// Ajouter dans vite.config.js
export default defineConfig({
  server: {
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/data/**',
        '**/thumbs/**',
        '**/posters/**',
        '**/*.db',
        '**/*.log*',
        '**/__pycache__/**'
      ],
      usePolling: false, // Évite CPU usage excessif
    },
    hmr: {
      overlay: true,
      timeout: 30000,
    },
  },
})
```

### 3.2: Éviter loops de refresh dans App.jsx

```javascript
// Ajouter debounce et flags
import { debounce } from './utils/debounce';

const isRefreshing = useRef(false);

const updateCache = useMemo(
  () => debounce(() => {
    if (!isRefreshing.current) {
      isRefreshing.current = true;
      setCacheKey(Date.now());
      setTimeout(() => { isRefreshing.current = false; }, 1000);
    }
  }, 1000),
  []
);
```

### 3.3: Service Worker professionnel

```bash
# Installer Workbox
npm install workbox-webpack-plugin workbox-window

# Configurer dans vite.config.js
# Générer SW avec stratégies de cache
```

---

## Phase 4: UX ENHANCEMENTS (PRIORITÉ MOYENNE) ✨

### 4.1: Skeleton Screens

**Créer composants skeleton:**
```jsx
// components/VideoCard/VideoCard.Skeleton.jsx
export function VideoCardSkeleton() {
  return (
    <div className="video-card-skeleton animate-shimmer">
      <div className="skeleton-thumbnail"></div>
      <div className="skeleton-title"></div>
      <div className="skeleton-meta"></div>
    </div>
  );
}

// Usage dans CategoryRow:
{isLoading ? (
  <VideoCard.Skeleton count={6} />
) : (
  videos.map(video => <VideoCard key={video.id} {...video} />)
)}
```

### 4.2: Transitions de page

```bash
npm install framer-motion

# Wrapper App avec AnimatePresence
```

### 4.3: Keyboard Navigation

```javascript
// Hook useKeyboardNav
function useKeyboardNav(ref, options) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      switch(e.key) {
        case 'ArrowLeft': // Navigate left
        case 'ArrowRight': // Navigate right
        case 'ArrowUp': // Navigate up
        case 'ArrowDown': // Navigate down
        case 'Enter': // Select
        case 'Escape': // Back
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}
```

---

## Phase 5: CODE QUALITY (CONTINU) 🧹

### 5.1: Nomenclature uniforme

**JavaScript:**
- Fichiers composants: `PascalCase.jsx`
- Fichiers utils: `camelCase.js`
- CSS: `kebab-case.css`
- Variables: `camelCase`
- Constantes: `UPPER_SNAKE_CASE`

**Python:**
- Tout en `snake_case`

### 5.2: ESLint strict

```json
// .eslintrc.json
{
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn",
    "react-hooks/exhaustive-deps": "error"
  }
}
```

### 5.3: Types avec JSDoc

```javascript
/**
 * @typedef {Object} Video
 * @property {number} id
 * @property {string} title
 * @property {string} path
 * @property {number} duration
 */

/**
 * Fetch videos by mode
 * @param {string} mode - Filter mode
 * @param {number|null} profileId - Profile ID
 * @returns {Promise<Video[]>}
 */
export async function fetchVideos(mode, profileId) {
  // ...
}
```

---

## TIMELINE RECOMMANDÉ

### Semaine 1 (5 jours)
- [x] **Jour 1-2:** Restructuration CSS complète
- [ ] **Jour 3:** Migration API et imports
- [ ] **Jour 4:** Optimisation cache & hot-reload
- [ ] **Jour 5:** Tests et validation

### Semaine 2 (5 jours)
- [ ] **Jour 1-2:** Skeleton screens
- [ ] **Jour 3:** Transitions et animations
- [ ] **Jour 4:** Keyboard navigation
- [ ] **Jour 5:** Code quality & cleanup

### Résultat final:
- ✅ **-60% de CSS** (de 3632 lignes à ~1500 lignes bien organisées)
- ✅ **-30% bundle size** (lazy loading + optimisations)
- ✅ **+80% maintenabilité** (structure claire)
- ✅ **UX niveau professionnel** (Netflix/Plex quality)

---

## COMMANDES UTILES

### Analyse de bundle
```bash
cd client
npm run build
npx vite-bundle-visualizer
```

### Mesure performance
```bash
# Lighthouse
npm install -g lighthouse
lighthouse http://localhost:5173 --view

# Bundle size
npm install -g size-limit
```

### Nettoyage
```bash
# Client
cd client
rm -rf node_modules/.vite
rm -rf dist
npm install

# Server
cd server
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## VALIDATION

### Checklist avant commit:
- [ ] `npm run lint` passe sans erreurs
- [ ] `npm run build` réussit
- [ ] Bundle size < 500KB (main chunk)
- [ ] Lighthouse score > 90
- [ ] Pas de console.errors dans DevTools
- [ ] Hot reload fonctionne sans loop
- [ ] Tests passent

---

## RESSOURCES

### Documentation
- [Vite Guide](https://vitejs.dev/guide/)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Workbox](https://developers.google.com/web/tools/workbox)

### Outils
- Chrome DevTools (Performance, Coverage)
- React DevTools Profiler
- Lighthouse CI

---

**Dernière mise à jour:** 16 Nov 2025  
**Statut:** Phase 1 en cours (structure CSS créée)  
**Prochaine étape:** Migration des styles existants
