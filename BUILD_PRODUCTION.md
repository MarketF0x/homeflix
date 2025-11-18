# 🏗️ Guide de Build Production - Homeflix

## 📦 Créer un Build de Production

### Étape 1 : Préparer l'Environnement

```powershell
# Nettoyer les builds précédents
Remove-Item -Recurse -Force .\client\dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\electron\dist -ErrorAction SilentlyContinue

# Installer les dépendances (si nécessaire)
cd client
npm install
cd ..
```

### Étape 2 : Build du Client

```powershell
# Build optimisé pour production
npm run build

# Le résultat est dans client/dist/
```

**Optimisations automatiques :**
- ✅ Minification JavaScript et CSS
- ✅ Suppression des `console.log`
- ✅ Tree-shaking des imports inutilisés
- ✅ Code splitting intelligent
- ✅ Compression des assets
- ✅ Hashing des fichiers pour cache busting

### Étape 3 : Déployer vers Electron

```powershell
# Option 1 : Build + Deploy automatique
npm run build:deploy

# Option 2 : Deploy uniquement (si build déjà fait)
npm run deploy:electron
```

### Étape 4 : Tester le Build

```powershell
# Démarrer l'application
.\homeflix.ps1
```

---

## 📋 Checklist Avant Distribution

### ✅ Code

- [ ] Tous les `console.log` sont supprimés en production
- [ ] Pas de clés API en dur dans le code
- [ ] Gestion d'erreurs robuste partout
- [ ] Tests passent avec succès

### ✅ Configuration

- [ ] `settings.yaml` contient des valeurs par défaut sécurisées
- [ ] `.env.production` est configuré correctement
- [ ] Pas de données sensibles dans le dépôt

### ✅ Documentation

- [ ] `README.md` est à jour
- [ ] `GUIDE_UTILISATEUR.md` est complet
- [ ] `LICENSE` est présent et correct
- [ ] `CHANGELOG.md` est à jour

### ✅ Légal

- [ ] Copyright et attribution corrects
- [ ] Licences tierces documentées
- [ ] Conformité RGPD (données locales uniquement)
- [ ] Avertissement TMDb présent

### ✅ Performance

- [ ] Build client < 2 MB (gzippé)
- [ ] Temps de chargement initial < 3s
- [ ] Pas de memory leaks
- [ ] Images optimisées

### ✅ Sécurité

- [ ] Dépendances à jour (npm audit)
- [ ] Pas de vulnérabilités connues
- [ ] HTTPS optionnel configuré
- [ ] Mots de passe correctement hashés

---

## 🚀 Distribution

### Option 1 : Archive ZIP

```powershell
# Créer une archive de distribution
$version = "1.0.0"
$archiveName = "homeflix-v$version.zip"

# Fichiers à inclure
Compress-Archive -Path `
  .\client\dist, `
  .\electron, `
  .\server, `
  .\homeflix.ps1, `
  .\INSTALLER.ps1, `
  .\DESINSTALLER.ps1, `
  .\settings.yaml, `
  .\README.md, `
  .\GUIDE_UTILISATEUR.md, `
  .\LICENSE, `
  .\CHANGELOG.md `
  -DestinationPath $archiveName -Force

Write-Host "✅ Archive créée : $archiveName"
```

### Option 2 : Installateur Windows (Inno Setup)

Utilisez le script fourni :

```powershell
cd installer
.\build-installer.ps1
```

L'installateur sera créé dans `installer\Output\`

---

## 🔍 Vérification du Build

### Vérifier la Taille

```powershell
# Taille du bundle client
Get-ChildItem -Recurse .\client\dist | Measure-Object -Property Length -Sum

# Détails par type
Get-ChildItem -Recurse .\client\dist | 
  Group-Object Extension | 
  Select-Object Name, Count, @{Name="Size (MB)"; Expression={($_.Group | Measure-Object Length -Sum).Sum / 1MB}}
```

### Tester les Performances

```powershell
# Ouvrir DevTools dans Chrome
# Network → Disable cache → Reload
# Lighthouse → Generate report
```

**Objectifs :**
- Performance Score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s

### Vérifier les Dépendances

```powershell
# Client
cd client
npm audit
npm outdated

# Serveur
cd ..\server
pip list --outdated
```

---

## 🛠️ Optimisations Avancées

### Réduire la Taille du Bundle

```javascript
// vite.config.js - Déjà configuré !
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'vendor': ... // autres dépendances
      }
    }
  }
}
```

### Compression Gzip

Activé automatiquement par Vite en production.

### Lazy Loading

```javascript
// Exemple : charger VideoPlayer uniquement quand nécessaire
const VideoPlayer = lazy(() => import('./VideoPlayer'));
```

---

## 📊 Analyse du Bundle

### Visualiser le Bundle

```powershell
cd client
npm install --save-dev rollup-plugin-visualizer
npm run build
```

Ouvrir `client/dist/stats.html` pour voir la répartition.

### Identifier les Dépendances Lourdes

```powershell
cd client
npx webpack-bundle-analyzer dist/stats.json
```

---

## 🔒 Sécurité en Production

### Variables d'Environnement

**Ne jamais inclure :**
- Clés API privées
- Secrets de chiffrement
- Mots de passe

**Utiliser à la place :**
- Fichier `settings.yaml` (configuré par l'utilisateur)
- Variables d'environnement système
- Configuration lors de l'installation

### HTTPS (Optionnel)

Pour activer HTTPS :

1. Générer des certificats :

```powershell
# Utiliser mkcert (recommandé pour dev local)
mkcert -install
mkcert localhost 127.0.0.1 ::1

# Placer dans certs/
mkdir certs
Move-Item localhost*.pem certs/
Rename-Item certs/localhost+2.pem cert.pem
Rename-Item certs/localhost+2-key.pem key.pem
```

2. Vite détectera automatiquement les certificats

---

## 📝 Versioning

### Semantic Versioning

- **MAJOR.MINOR.PATCH** (ex: 1.0.0)
- **MAJOR** : Changements incompatibles
- **MINOR** : Nouvelles fonctionnalités compatibles
- **PATCH** : Corrections de bugs

### Mise à Jour de Version

```powershell
# Mettre à jour package.json
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.1 → 1.1.0
npm version major  # 1.1.0 → 2.0.0

# Créer un tag Git
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

---

## ✅ Validation Finale

Avant de distribuer :

1. ✅ **Tester sur machine propre** (sans dépendances dev)
2. ✅ **Tester l'installateur** de bout en bout
3. ✅ **Vérifier la désinstallation** complète
4. ✅ **Tester tous les scénarios utilisateur**
5. ✅ **Vérifier les logs** (pas d'erreurs)
6. ✅ **Valider les performances** (Lighthouse)
7. ✅ **Scanner les vulnérabilités** (npm audit)
8. ✅ **Vérifier la conformité légale**

---

## 🎯 Distribution Continue

### GitHub Releases

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
      - name: Build
        run: npm run build
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: homeflix-*.zip
```

---

**Votre application est maintenant prête pour la commercialisation ! 🚀**
