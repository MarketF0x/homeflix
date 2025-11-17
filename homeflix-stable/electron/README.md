# Homeflix - Application Electron

Application de bureau pour Homeflix, permettant d'utiliser le serveur de streaming dans une fenêtre native indépendante.

## 🚀 Lancement Rapide

### Windows
```powershell
.\start-homeflix-app.ps1
```

### Linux/Mac
```bash
cd electron
npm install
npm start
```

## 📋 Prérequis

- **Node.js 18+** : https://nodejs.org/
- **Python 3.10+** : Pour le serveur backend
- **Dépendances Python** : Installées via `pip install -r requirements.txt`

## 🎯 Fonctionnalités

### ✅ Fenêtre Native
- Application indépendante du navigateur
- Icône dans la barre des tâches
- Gestion du plein écran (F11)

### ✅ Serveur Intégré
- Démarrage automatique du serveur Python
- Arrêt propre à la fermeture de l'app
- Vérification de disponibilité

### ✅ Raccourcis Clavier
| Raccourci | Action |
|-----------|--------|
| `Ctrl+R` | Actualiser |
| `Ctrl+Shift+R` | Forcer l'actualisation |
| `Ctrl+Q` | Quitter |
| `F11` | Plein écran |
| `F12` | Outils développeur |
| `Ctrl +/-/0` | Zoom |

### ✅ Sécurité
- Isolation du contexte (contextIsolation)
- Pas d'intégration Node dans le renderer
- WebSecurity activée
- Liens externes ouverts dans le navigateur par défaut

## 🔧 Installation Manuelle

```bash
# 1. Aller dans le dossier electron
cd electron

# 2. Installer les dépendances
npm install

# 3. Lancer l'app
npm start
```

## 📦 Créer un Exécutable

### Windows (.exe)
```bash
npm run build:win
```
Résultat : `electron/dist/Homeflix Setup.exe`

### macOS (.dmg)
```bash
npm run build:mac
```
Résultat : `electron/dist/Homeflix.dmg`

### Linux (.AppImage)
```bash
npm run build:linux
```
Résultat : `electron/dist/Homeflix.AppImage`

## 🛠️ Configuration

### Port du serveur
Modifier `SERVER_PORT` dans `main.js` :
```javascript
const SERVER_PORT = 8000; // Changer si besoin
```

### Taille de fenêtre
Modifier dans `createWindow()` :
```javascript
mainWindow = new BrowserWindow({
  width: 1400,  // Largeur
  height: 900,  // Hauteur
  // ...
});
```

## 🐛 Dépannage

### Problème : "Serveur non disponible"
- Vérifier que Python est installé : `python --version`
- Vérifier les dépendances : `pip install -r requirements.txt`
- Regarder les logs dans la console Electron

### Problème : "Page ne charge pas"
- Appuyer sur `Ctrl+Shift+R` (forcer actualisation)
- Vérifier que le port 8000 est libre
- Ouvrir DevTools (F12) pour voir les erreurs

### Problème : "npm install échoue"
- Mettre à jour Node.js : https://nodejs.org/
- Nettoyer le cache : `npm cache clean --force`
- Supprimer `node_modules` et réessayer

## 📁 Structure

```
electron/
├── package.json      # Config npm + Electron Builder
├── main.js           # Process principal Electron
├── preload.js        # Script de preload sécurisé
├── icon.png          # Icône de l'application
└── README.md         # Cette documentation
```

## 🔄 Mises à Jour

Pour mettre à jour l'application :

1. Mettre à jour Electron :
```bash
npm update electron
```

2. Mettre à jour Electron Builder :
```bash
npm update electron-builder
```

3. Rebuilder :
```bash
npm run build:win
```

## 🎨 Personnalisation

### Changer l'icône
Remplacer `icon.png` par votre icône (512x512 recommandé)

### Modifier le menu
Éditer `menuTemplate` dans `main.js`

### Ajouter des fonctionnalités
1. Ajouter handlers IPC dans `main.js`
2. Exposer APIs dans `preload.js`
3. Utiliser `window.homeflix.xxx()` dans le frontend

## 📊 Performance

- **Démarrage** : ~3-5 secondes
- **Mémoire** : ~150-200 MB (Chromium + Python)
- **Taille app** : ~200 MB (inclut Chromium)

## 🔐 Sécurité

- ✅ Context isolation activée
- ✅ Node integration désactivée
- ✅ Web security activée
- ✅ Pas de contenu insecure
- ✅ Preload script isolé

## 📝 License

MIT - Voir LICENSE dans le dossier racine

## 🆘 Support

- GitHub Issues : https://github.com/homeflix/homeflix/issues
- Documentation : Voir fichiers .md dans la racine du projet

---

**Version** : 2.0.0  
**Electron** : 28.0.0  
**Node.js requis** : 18+
