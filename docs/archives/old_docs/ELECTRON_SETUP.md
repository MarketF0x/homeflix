# 🚀 Application Electron Homeflix - Guide Complet

## ✅ Installation Terminée

L'application de bureau Homeflix est maintenant configurée !

## 🎬 Lancer l'Application

### Méthode Simple (Recommandée)
```powershell
.\start-homeflix-app.ps1
```

Ce script va :
1. ✅ Vérifier que Node.js et Python sont installés
2. ✅ Installer les dépendances Electron si besoin
3. ✅ Lancer l'application native
4. ✅ Démarrer automatiquement le serveur Python
5. ✅ Ouvrir Homeflix dans une fenêtre indépendante

### Méthode Manuelle
```powershell
cd electron
npm start
```

---

## 🎯 Avantages de l'App Native

| Avant (Navigateur) | Maintenant (App Native) |
|-------------------|------------------------|
| 2 fenêtres (terminal + navigateur) | 1 seule fenêtre |
| Lancer serveur manuellement | Démarrage automatique |
| Onglet navigateur mélangé aux autres | App dédiée barre des tâches |
| Oublier d'arrêter le serveur | Arrêt automatique à la fermeture |
| F5 recharge parfois mal | Ctrl+R fiable |

---

## 🔧 Fonctionnalités

### Raccourcis Clavier
- **Ctrl+R** : Actualiser
- **Ctrl+Shift+R** : Forcer actualisation (vider cache)
- **Ctrl+Q** : Quitter
- **F11** : Plein écran
- **F12** : DevTools (debug)
- **Ctrl +/-/0** : Zoom

### Menu Intégré
- **Fichier** → Actualiser, Quitter
- **Affichage** → Plein écran, Zoom, DevTools
- **Aide** → À propos, Documentation

### Sécurité
- ✅ Isolation contexte (sandbox)
- ✅ Pas d'accès Node.js depuis le renderer
- ✅ Liens externes ouverts dans le navigateur
- ✅ WebSecurity activée

---

## 📦 Créer un Exécutable Windows

Pour distribuer l'application à d'autres utilisateurs :

```powershell
cd electron
npm run build:win
```

**Résultat :** `electron/dist/Homeflix Setup.exe` (~200 MB)

**Installation :**
1. Double-clic sur `Homeflix Setup.exe`
2. L'app s'installe dans `C:\Users\[USER]\AppData\Local\Programs\Homeflix`
3. Raccourci créé dans le menu Démarrer
4. Icône Homeflix dans la barre des tâches

**Prérequis pour l'utilisateur :**
- Python 3.10+ installé
- Dépendances Python installées (`pip install -r requirements.txt`)

---

## 🛠️ Dépannage

### ❌ "Node.js n'est pas installé"
**Solution :** Installer Node.js 18+ depuis https://nodejs.org/

### ❌ "Serveur non disponible"
**Causes possibles :**
1. Python non installé → `python --version`
2. Dépendances manquantes → `pip install -r requirements.txt`
3. Port 8000 occupé → Changer `SERVER_PORT` dans `electron/main.js`

**Test manuel du serveur :**
```powershell
cd c:\Users\fparo\Desktop\homeflix
python server/main.py
```

### ❌ Page blanche ou ne charge pas
**Solutions :**
1. Attendre 5 secondes (serveur démarre)
2. Appuyer sur **Ctrl+R** pour actualiser
3. Ouvrir DevTools (**F12**) pour voir les erreurs
4. Vérifier que `client/dist/` existe (rebuild si besoin)

### ❌ "npm install" échoue
**Solutions :**
```powershell
# Nettoyer le cache
npm cache clean --force

# Supprimer node_modules
Remove-Item electron/node_modules -Recurse -Force

# Réinstaller
cd electron
npm install
```

---

## 📁 Architecture

```
homeflix/
├── electron/
│   ├── main.js              # Process principal (gère serveur + fenêtre)
│   ├── preload.js           # APIs sécurisées
│   ├── package.json         # Config npm + Electron Builder
│   ├── icon.png             # Icône 512x512
│   └── node_modules/        # Dépendances Electron
│
├── server/                   # Backend FastAPI
│   └── main.py              # Point d'entrée serveur
│
├── client/                   # Frontend React
│   └── dist/                # Build production (servi par serveur)
│
├── start-homeflix-app.ps1   # 🚀 LANCEMENT APP NATIVE
├── start.ps1                # Lancement navigateur (ancien)
└── README_APP.md            # Documentation app
```

---

## 🔄 Workflow de Développement

### 1. Modifier le Frontend (React)
```powershell
cd client
npm run build
```

### 2. Modifier le Backend (Python)
Le serveur redémarre automatiquement avec l'app Electron.

### 3. Tester les Changements
- Relancer l'app : **Ctrl+Q** puis `.\start-homeflix-app.ps1`
- Ou simplement **Ctrl+Shift+R** pour forcer le refresh

### 4. Debug
- Ouvrir DevTools : **F12**
- Console Electron : Visible dans le terminal de lancement
- Logs serveur : Affichés dans le terminal

---

## 🎨 Personnalisation

### Changer le Port
**Fichier :** `electron/main.js`
```javascript
const SERVER_PORT = 8000; // Modifier ici
```

### Modifier la Fenêtre
**Fichier :** `electron/main.js` → fonction `createWindow()`
```javascript
mainWindow = new BrowserWindow({
  width: 1400,        // Largeur
  height: 900,        // Hauteur
  minWidth: 1024,     // Largeur minimale
  minHeight: 768,     // Hauteur minimale
  // ...
});
```

### Changer l'Icône
**Remplacer :** `electron/icon.png` (512x512 recommandé)

**Regenerer :**
```powershell
python create_electron_icon.py
```

### Ajouter un Menu
**Fichier :** `electron/main.js` → `menuTemplate`

Exemple :
```javascript
{
  label: 'Nouveau Menu',
  submenu: [
    {
      label: 'Action personnalisée',
      click: () => {
        // Code ici
      }
    }
  ]
}
```

---

## 📊 Performance & Optimisation

### Taille de l'App
- **Installeur** : ~200 MB (inclut Chromium)
- **Installée** : ~250 MB
- **Mémoire runtime** : 150-200 MB

### Temps de Démarrage
- Lancement app : **1-2s**
- Démarrage serveur : **2-3s**
- **Total** : **3-5s** ⚡

### Optimisations Appliquées
- ✅ Preload script pour APIs sécurisées
- ✅ Context isolation (sandbox)
- ✅ Pas de Node.js integration dans renderer
- ✅ WebSecurity activée
- ✅ Hardware acceleration (GPU pour vidéo)

---

## 🚀 Distribution

### Option 1 : Installeur (.exe)
```powershell
cd electron
npm run build:win
```
**Partager :** `electron/dist/Homeflix Setup.exe`

### Option 2 : App Portable
Créer un dossier avec :
- `electron/` (dossier complet)
- `server/` (backend Python)
- `client/dist/` (frontend build)
- `start-homeflix-app.ps1`

**L'utilisateur aura besoin de :**
- Node.js 18+
- Python 3.10+
- Dépendances Python

### Option 3 : Tout-en-un (Futur)
Utiliser PyInstaller pour embarquer Python dans l'exe.

---

## 🔐 Sécurité

### Protection Intégrée
- **Context Isolation** : Renderer isolé du process principal
- **No Node Integration** : Pas d'accès require() dans le renderer
- **Preload Script** : APIs exposées via `contextBridge`
- **WebSecurity** : Protection XSS/injection
- **CSP Headers** : Content Security Policy

### Bonnes Pratiques
- ✅ Jamais exposer `remote` module
- ✅ Valider toutes les entrées IPC
- ✅ Utiliser `shell.openExternal()` pour liens externes
- ✅ Pas de `eval()` ou `new Function()` dans le code

---

## 📚 Ressources

### Documentation
- **README_APP.md** : Guide utilisateur
- **electron/README.md** : Doc technique Electron
- **GUIDE_DEMARRAGE.md** : Installation générale

### Liens Utiles
- Electron : https://www.electronjs.org/
- Electron Builder : https://www.electron.build/
- Node.js : https://nodejs.org/

---

## ✨ Prochaines Étapes

### Améliorations Possibles
- [ ] Auto-update intégré
- [ ] Tray icon (icône barre notification)
- [ ] Mode offline (cache vidéos)
- [ ] Splash screen personnalisé
- [ ] Menu contextuel personnalisé
- [ ] Notifications natives
- [ ] Raccourcis globaux (hotkeys)

---

**Version** : 2.0.0  
**Electron** : 28.0.0  
**Node.js requis** : 18+  
**Python requis** : 3.10+

🎉 **Homeflix est maintenant une vraie application de bureau !**
