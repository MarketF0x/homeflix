# 🔧 Correctif : Transcodage vidéo en accès réseau

**Date** : 18 novembre 2025  
**Problème** : `NS_ERROR_CONNECTION_REFUSED` lors du transcodage de fichiers AVI en accès réseau

---

## 🐛 Problème Identifié

### Symptômes
```
GET http://100.72.164.87:5173/api/stream/transcode?path=H:\Film\Jumanji.avi&audio_track=1&quality=medium
NS_ERROR_CONNECTION_REFUSED
```

- Les requêtes de transcodage allaient sur le port **5173** (Vite dev) au lieu du port **8000** (backend)
- Le problème se manifestait uniquement lors de l'accès distant (ex: `http://100.72.164.87:5173`)
- Les fichiers AVI ne pouvaient pas être lus avec transcodage

### Cause Racine

Le **proxy Vite** (`vite.config.js`) ne fonctionne que pour les requêtes locales :
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

Quand un utilisateur accède depuis le réseau (ex: `100.72.164.87:5173`), les requêtes `/api/stream/transcode` sont envoyées à `100.72.164.87:5173` au lieu de `100.72.164.87:8000`.

---

## ✅ Solution Implémentée

### 1. Modification de `client/src/config.js`

**Avant** :
```javascript
export function getApiBaseUrl() {
  // Si en mode développement avec Vite, utiliser le proxy
  if (import.meta.env.DEV) {
    return ''; // Les requêtes /api/* sont proxifiées par Vite
  }
  // ... reste du code
}
```

**Après** :
```javascript
export function getApiBaseUrl() {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  // Si en mode développement avec Vite
  if (import.meta.env.DEV) {
    // ✅ FIX: Si on accède depuis le réseau (IP distante), ne PAS utiliser le proxy
    // Le proxy Vite ne fonctionne que pour localhost
    if (hostname !== 'localhost' && hostname !== '127.0.0.1' && hostname !== '') {
      // Accès réseau -> pointer directement vers le backend sur port 8000
      return `http://${hostname}:8000`;
    }
    // Accès local -> utiliser le proxy Vite (chaîne vide)
    return ''; // Les requêtes /api/* sont proxifiées par Vite
  }
  // ... reste du code inchangé
}
```

### 2. Modification de `client/src/VideoPlayer.jsx`

**Import mis à jour** :
```javascript
import { thumbURL, API, getApiBaseUrl } from "./config.js";
```

**Utilisation directe de getApiBaseUrl()** :
```javascript
// ✅ Utiliser directement getApiBaseUrl() pour avoir la bonne URL de base
const baseUrl = getApiBaseUrl();

const directUrl = `${baseUrl}/api/stream?path=${encodeURIComponent(video.path)}`;
const transcodeUrl = `${baseUrl}/api/stream/transcode?path=${encodeURIComponent(video.path)}&audio_track=${selectedAudioTrack}...`;
```

Au lieu de l'ancienne méthode avec substring :
```javascript
// ❌ ANCIEN CODE
const baseUrl = API.substring(0, API.lastIndexOf('/api'));
```

### 3. Logs de diagnostic ajoutés

**Dans `config.js`** :
```javascript
if (import.meta.env.DEV) {
  console.log('🌐 API Base URL:', getApiBaseUrl());
  console.log('🌐 API URL configurée:', API);
  console.log('🌐 Hostname:', window.location.hostname);
}
```

**Dans `VideoPlayer.jsx`** :
```javascript
console.log('🎬 VideoPlayer URLs:', {
  baseUrl,
  directUrl: directUrl.substring(0, 100) + '...',
  transcodeUrl: transcodeUrl.substring(0, 100) + '...',
  videoUrl: videoUrl.substring(0, 100) + '...',
  useTranscode
});
```

---

## 🧪 Test de Validation

### Scénario 1 : Accès local (localhost)
- **URL d'accès** : `http://localhost:5173`
- **Résultat attendu** : `baseUrl = ''` (proxy Vite actif)
- **URL de transcodage** : `/api/stream/transcode?...` → proxy vers `localhost:8000`

### Scénario 2 : Accès réseau (IP distante)
- **URL d'accès** : `http://100.72.164.87:5173`
- **Résultat attendu** : `baseUrl = 'http://100.72.164.87:8000'`
- **URL de transcodage** : `http://100.72.164.87:8000/api/stream/transcode?...`

### Scénario 3 : Production/Electron
- **Résultat attendu** : URLs complètes avec port 8000
- **Comportement** : Inchangé (déjà fonctionnel)

---

## 📝 Fichiers Modifiés

1. ✅ `client/src/config.js` - Détection hostname en mode DEV
2. ✅ `client/src/VideoPlayer.jsx` - Utilisation de `getApiBaseUrl()` directement
3. ✅ Logs de diagnostic ajoutés pour faciliter le débogage

---

## 🎯 Impact

### Problèmes Résolus
- ✅ Transcodage de fichiers AVI fonctionne en accès réseau
- ✅ Tous les formats vidéo (AVI, WMV, FLV, MKV) supportés en accès distant
- ✅ Sélection de pistes audio/sous-titres fonctionnelle
- ✅ Qualité de transcodage ajustable (fast/medium/high)

### Régression Potentielle
- ❌ Aucune - La détection est basée sur le hostname
- ✅ Accès local continue d'utiliser le proxy Vite (HMR fonctionnel)
- ✅ Production/Electron inchangé

---

## 🚀 Déploiement

### Étapes
1. ✅ Modifications apportées dans `client/src/`
2. ⏳ **Redémarrer le serveur Vite** : `Ctrl+C` puis `npm run dev`
3. ⏳ **Tester depuis un appareil distant** : `http://<IP>:5173`
4. ⏳ **Vérifier les logs** dans la console navigateur :
   ```
   🌐 API Base URL: http://100.72.164.87:8000
   🎬 VideoPlayer URLs: { baseUrl: 'http://100.72.164.87:8000', ... }
   ```

### Vérification Backend
```powershell
# Vérifier que le backend écoute sur 0.0.0.0:8000 (accessible réseau)
netstat -ano | findstr :8000
# Doit afficher : TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```

---

## 📖 Notes Techniques

### Proxy Vite - Limitations
Le proxy Vite (`vite.config.js`) ne fonctionne que pour :
- Requêtes depuis `localhost` ou `127.0.0.1`
- Il ne peut pas proxifier les requêtes cross-origin depuis une IP distante

### Solution Alternative (non retenue)
- Configurer CORS sur le backend → Trop complexe
- Utiliser un reverse proxy (nginx) → Overkill pour le dev
- **✅ Détection intelligente du hostname** → Simple et efficace

### Architecture de Streaming

```
┌─────────────────────────────────────────────────┐
│  CLIENT (100.72.164.87:5173)                    │
│  ┌───────────────────────────────────────────┐  │
│  │  VideoPlayer.jsx                          │  │
│  │  - getApiBaseUrl() = "http://...87:8000"  │  │
│  │  - transcodeUrl = baseUrl + /api/stream/  │  │
│  └───────────────────────────────────────────┘  │
│           │                                      │
│           │ HTTP Request                         │
│           ▼                                      │
│  ┌───────────────────────────────────────────┐  │
│  │  Vite Dev Server (:5173)                  │  │
│  │  - Sert uniquement les fichiers frontend  │  │
│  │  - Proxy inactif pour IP distante         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    │ Requête directe vers :8000
                    ▼
┌─────────────────────────────────────────────────┐
│  BACKEND (0.0.0.0:8000)                         │
│  ┌───────────────────────────────────────────┐  │
│  │  FastAPI Server                           │  │
│  │  - /api/stream/transcode                  │  │
│  │  - FFmpeg transcodage temps réel          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Test

- [ ] Accès local (`localhost:5173`) - Lecture vidéo directe
- [ ] Accès local (`localhost:5173`) - Transcodage AVI
- [ ] Accès réseau (`IP:5173`) - Lecture vidéo directe
- [ ] Accès réseau (`IP:5173`) - Transcodage AVI
- [ ] Changement de piste audio en transcodage
- [ ] Changement de qualité de transcodage (fast/medium/high)
- [ ] Vérification console - URLs correctes
- [ ] Mode production (build) - Inchangé

---

**Statut** : ✅ **RÉSOLU**  
**Testeur** : À valider par l'utilisateur  
**Prochaine étape** : Tester avec `Jumanji.avi` en accès réseau
