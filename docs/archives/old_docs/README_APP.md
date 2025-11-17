# 🎬 Homeflix - Application de Bureau

## 🚀 Lancement Rapide

### Option 1 : Application Native (Recommandé)

**Windows :**
```powershell
.\start-homeflix-app.ps1
```

L'application s'ouvrira dans une **fenêtre native indépendante** avec :
- ✅ Démarrage automatique du serveur
- ✅ Icône dans la barre des tâches
- ✅ Actualisation simple (Ctrl+R)
- ✅ Plein écran (F11)
- ✅ Zoom (Ctrl +/-/0)
- ✅ Arrêt propre du serveur à la fermeture

### Option 2 : Serveur + Navigateur Web

**Windows :**
```powershell
.\start.ps1
```

Puis ouvrir http://localhost:8000 dans votre navigateur.

---

## 📋 Prérequis

### Pour l'Application Native
- **Node.js 18+** : [Télécharger](https://nodejs.org/)
- **Python 3.10+** : Installé
- **Dépendances Python** : Installées

### Installation des Dépendances Node.js

Lors du premier lancement, les dépendances Electron seront installées automatiquement.

Pour une installation manuelle :
```powershell
cd electron
npm install
```

---

## 🎯 Fonctionnalités de l'Application

### Fenêtre Native
- Application Windows indépendante
- Pas besoin d'ouvrir un navigateur
- Interface optimisée
- Gestion du plein écran

### Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+R` | Actualiser la page |
| `Ctrl+Shift+R` | Forcer l'actualisation (cache) |
| `Ctrl+Q` | Quitter l'application |
| `F11` | Basculer plein écran |
| `F12` | Outils de développement |
| `Ctrl+Plus` | Zoomer |
| `Ctrl+Moins` | Dézoomer |
| `Ctrl+0` | Réinitialiser le zoom |

### Menu Intégré
- **Fichier** : Actualiser, Quitter
- **Affichage** : Plein écran, Zoom, DevTools
- **Aide** : À propos, Documentation

---

## 📦 Créer un Exécutable (.exe)

Pour créer un installeur Windows :

```powershell
cd electron
npm install
npm run build:win
```

L'installeur sera créé dans `electron/dist/Homeflix Setup.exe`

**Distribuer l'application :**
1. Partager `Homeflix Setup.exe`
2. L'utilisateur n'a besoin que de Python installé
3. Double-clic sur l'exe pour installer
4. L'app apparaît dans le menu Démarrer

---

## 🛠️ Dépannage

### "Node.js n'est pas installé"
Télécharger et installer : https://nodejs.org/

### "Serveur non disponible"
Vérifier que Python est installé :
```powershell
python --version
```

Vérifier les dépendances :
```powershell
pip install -r requirements.txt
```

### L'application ne démarre pas
1. Ouvrir PowerShell dans le dossier homeflix
2. Lancer manuellement :
```powershell
cd electron
npm start
```
3. Regarder les erreurs dans la console

### Page blanche ou erreur 404
1. Attendre 5-10 secondes (le serveur démarre)
2. Appuyer sur `Ctrl+R` pour actualiser
3. Vérifier que le port 8000 est libre

---

## 📁 Structure du Projet

```
homeflix/
├── electron/                    # Application de bureau
│   ├── main.js                 # Process principal Electron
│   ├── preload.js              # Script de preload sécurisé
│   ├── package.json            # Config npm
│   ├── icon.png                # Icône de l'app
│   └── README.md               # Doc Electron
├── server/                      # Backend Python FastAPI
├── client/                      # Frontend React
├── start-homeflix-app.ps1      # 🚀 LANCER L'APP NATIVE
├── start.ps1                   # Lancer serveur + navigateur
└── README_APP.md               # Cette documentation
```

---

## 🔄 Mises à Jour

### Mettre à jour l'application

1. **Mettre à jour le code :**
   - Télécharger la nouvelle version
   - Remplacer les fichiers

2. **Mettre à jour les dépendances :**
```powershell
# Python
pip install -r requirements.txt --upgrade

# Node.js (si modification d'Electron)
cd electron
npm update
```

3. **Rebuild le frontend :**
```powershell
cd client
npm run build
```

### Auto-update (Future)
Dans les versions futures, l'app vérifiera automatiquement les mises à jour au démarrage.

---

## 🎨 Personnalisation

### Changer le port du serveur

Éditer `electron/main.js` :
```javascript
const SERVER_PORT = 8000; // Changer ici
```

### Modifier la taille de la fenêtre

Éditer `electron/main.js` dans `createWindow()` :
```javascript
width: 1400,  // Largeur
height: 900,  // Hauteur
```

### Changer l'icône

Remplacer `electron/icon.png` par votre icône (512x512 recommandé)

---

## 🔐 Sécurité

L'application Electron est configurée avec les meilleures pratiques de sécurité :

- ✅ **Context Isolation** : Code renderer isolé
- ✅ **No Node Integration** : Pas d'accès Node.js dans le renderer
- ✅ **Web Security** : Protection XSS activée
- ✅ **Preload Script** : API exposées de manière sécurisée
- ✅ **Liens externes** : Ouverts dans le navigateur par défaut

---

## 📊 Performance

**Consommation :**
- Mémoire : ~150-200 MB (Chromium embarqué + serveur Python)
- CPU : Minimal au repos, pic lors du streaming
- Disque : ~200 MB (app installée)

**Temps de démarrage :**
- Lancement app : 1-2 secondes
- Démarrage serveur : 2-3 secondes
- **Total** : 3-5 secondes

---

## 🆘 Support

**Documentation complète :**
- Application Electron : `electron/README.md`
- Installation : `GUIDE_DEMARRAGE.md`
- Profils : `GUIDE_PROFILS.md`
- Compression : `GUIDE_COMPRESSION.md`

**Logs de debug :**
- Ouvrir DevTools : `F12` dans l'app
- Console Electron : Visible dans le terminal de lancement

---

## 🎉 Avantages de l'App Native

✅ **Plus simple** : Un seul clic au lieu de 2 (serveur + navigateur)  
✅ **Plus rapide** : Démarrage automatique du serveur  
✅ **Plus propre** : Pas d'onglet navigateur qui traîne  
✅ **Plus intégré** : Icône barre des tâches, alt+tab  
✅ **Plus sûr** : Serveur s'arrête avec l'app  
✅ **Actualisation facile** : Ctrl+R comme un site normal  

---

**Version** : 2.0.0  
**Plateforme** : Windows, macOS, Linux  
**Technologies** : Electron 28 + React + FastAPI + SQLite
