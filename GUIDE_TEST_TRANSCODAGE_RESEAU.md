# 🧪 Guide de Test - Correctif Transcodage Réseau

## 🎯 Objectif
Tester que le transcodage de fichiers AVI fonctionne correctement en accès réseau.

---

## ✅ Prérequis

### 1. Serveurs en cours d'exécution
- ✅ **Backend** sur port 8000 (PID 22484)
- ✅ **Frontend Vite** sur port 5173 (démarré)

Vérification :
```powershell
# Backend
netstat -ano | findstr :8000 | findstr LISTENING
# Résultat attendu : TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING

# Frontend
netstat -ano | findstr :5173 | findstr LISTENING
# Résultat attendu : TCP    0.0.0.0:5173           0.0.0.0:0              LISTENING
```

### 2. Modifications appliquées
- ✅ `client/src/config.js` - Détection hostname en mode DEV
- ✅ `client/src/VideoPlayer.jsx` - Utilisation de `getApiBaseUrl()`
- ✅ Hot Module Reload effectué

---

## 🧪 Tests à Effectuer

### Test 1 : Accès depuis un appareil distant

1. **Depuis votre téléphone/tablette/autre PC**, ouvrez :
   ```
   http://100.72.164.87:5173
   ```
   OU
   ```
   http://192.168.1.5:5173
   ```

2. **Ouvrir la console du navigateur** (sur PC) :
   - Firefox : `F12` → Onglet "Console"
   - Chrome : `F12` → Onglet "Console"

3. **Vérifier les logs de configuration** :
   ```
   🌐 API Base URL: http://100.72.164.87:8000
   🌐 API URL configurée: http://100.72.164.87:8000/api
   🌐 Hostname: 100.72.164.87
   ```
   
   ✅ **Vérification** : Le `API Base URL` doit contenir votre IP avec le port **8000**

4. **Lancer une vidéo AVI** (ex: `Jumanji.avi`) :
   - Rechercher le fichier dans l'interface
   - Cliquer pour lire la vidéo
   
5. **Vérifier les logs du VideoPlayer** :
   ```javascript
   🎬 VideoPlayer URLs: {
     baseUrl: "http://100.72.164.87:8000",
     directUrl: "http://100.72.164.87:8000/api/stream?path=H%3A%5CFilm%5CJumanji.avi...",
     transcodeUrl: "http://100.72.164.87:8000/api/stream/transcode?path=H%3A%5CFilm%5CJumanji.avi&audio_track=1...",
     videoUrl: "http://100.72.164.87:8000/api/stream/transcode?path=H%3A%5CFilm%5CJumanji.avi&audio_track=1...",
     useTranscode: true
   }
   ```
   
   ✅ **Vérification** : Toutes les URLs doivent pointer vers le port **8000**

6. **Observer la lecture vidéo** :
   - ✅ La vidéo démarre
   - ✅ Pas d'erreur `NS_ERROR_CONNECTION_REFUSED`
   - ✅ Le transcodage fonctionne

---

### Test 2 : Accès local (localhost)

1. **Sur le PC serveur**, ouvrez :
   ```
   http://localhost:5173
   ```

2. **Vérifier les logs de configuration** :
   ```
   🌐 API Base URL: (vide)
   🌐 API URL configurée: /api
   🌐 Hostname: localhost
   ```
   
   ✅ **Vérification** : Le `API Base URL` doit être **vide** (proxy Vite actif)

3. **Lancer une vidéo AVI** :
   
4. **Vérifier les logs du VideoPlayer** :
   ```javascript
   🎬 VideoPlayer URLs: {
     baseUrl: "",
     directUrl: "/api/stream?path=H%3A%5CFilm%5CJumanji.avi...",
     transcodeUrl: "/api/stream/transcode?path=H%3A%5CFilm%5CJumanji.avi&audio_track=1...",
     videoUrl: "/api/stream/transcode?path=H%3A%5CFilm%5CJumanji.avi&audio_track=1...",
     useTranscode: true
   }
   ```
   
   ✅ **Vérification** : Les URLs doivent être **relatives** (`/api/...`) - proxy Vite actif

5. **Observer la lecture vidéo** :
   - ✅ La vidéo démarre
   - ✅ Le transcodage fonctionne

---

## 🔍 Diagnostic en cas d'Erreur

### Erreur : `NS_ERROR_CONNECTION_REFUSED` persiste

**Vérifier que les URLs pointent vers 8000** :
```javascript
// Dans la console navigateur
console.log(window.location.hostname); // Doit afficher votre IP
```

**Vérifier le backend** :
```powershell
# Sur le serveur
netstat -ano | findstr :8000 | findstr LISTENING
# Doit afficher : TCP    0.0.0.0:8000
```

**Redémarrer le frontend** :
```powershell
# Dans le terminal Vite, appuyer sur Ctrl+C
cd client
npm run dev
```

### Erreur : `MediaError code: 4`

**Vérifier que FFmpeg est installé** :
```powershell
ffmpeg -version
```

**Vérifier les logs du backend** :
- Regarder le terminal où le backend tourne
- Chercher les messages d'erreur liés à FFmpeg

### Erreur : Vidéo ne démarre pas

**Vérifier le chemin du fichier** :
```
H:\Film\Jumanji.avi
```
- Le backend doit avoir accès au disque `H:`
- Le fichier doit exister

**Vérifier les permissions** :
- Le serveur Python doit pouvoir lire le fichier

---

## 📊 Résultat Attendu

| Scénario | baseUrl | URL de transcodage | Résultat |
|----------|---------|-------------------|----------|
| Accès local (`localhost`) | `""` (vide) | `/api/stream/transcode?...` | ✅ Proxy Vite → 8000 |
| Accès réseau (`100.72.164.87`) | `http://100.72.164.87:8000` | `http://100.72.164.87:8000/api/stream/transcode?...` | ✅ Direct vers 8000 |
| Accès réseau (`192.168.1.5`) | `http://192.168.1.5:8000` | `http://192.168.1.5:8000/api/stream/transcode?...` | ✅ Direct vers 8000 |

---

## ✅ Critères de Validation

- [ ] Accès distant : URLs pointent vers port 8000
- [ ] Accès local : URLs relatives (proxy Vite)
- [ ] Fichier AVI lit correctement en transcodage
- [ ] Aucune erreur `NS_ERROR_CONNECTION_REFUSED`
- [ ] Changement de piste audio fonctionne
- [ ] Changement de qualité fonctionne (fast/medium/high)

---

## 🎉 Si tout fonctionne

**Le problème est résolu !** Les fichiers AVI (et autres formats nécessitant du transcodage) sont maintenant lisibles en accès réseau.

**Prochaines étapes** :
1. Tester avec d'autres formats (WMV, FLV, etc.)
2. Tester sur différents appareils (téléphone, tablette)
3. Tester les sous-titres embarqués
4. Builder pour production : `npm run build`

---

**Date du test** : _________________  
**Testeur** : _________________  
**Résultat** : ☐ SUCCÈS ☐ ÉCHEC  
**Notes** : ___________________________________________
