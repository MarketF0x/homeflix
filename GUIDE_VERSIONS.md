# 🎬 HOMEFLIX - Guide de Gestion des Versions

## 📋 Vue d'ensemble

Homeflix dispose maintenant de **DEUX VERSIONS COMPLÈTEMENT SÉPARÉES** :

### 🟢 VERSION STABLE (Electron)

- **Utilisation** : Utilisation quotidienne, visionnage de films/séries
- **Caractéristiques** :
  - Application Electron (fenêtre dédiée)
  - Isolée et stable
  - Ne change pas sauf mise à jour volontaire
  - Accès direct aux disques Windows (F:, G:, H:, I:)
  - Serveur Python intégré dans l'application

### 🔵 VERSION DÉVELOPPEMENT (DEV)

- **Utilisation** : Tests, modifications, expérimentations
- **Caractéristiques** :
  - Code source direct
  - Rechargement à chaud (hot reload)
  - Modifications en temps réel
  - Ports : 5173 (frontend) et 8000 (backend)

---

## 🚀 Démarrage Rapide

### Version STABLE (Recommandé pour utilisation quotidienne)

```powershell
# Première utilisation - construire la version stable
.\homeflix-stable.ps1 build

# Démarrer l'application
.\homeflix-stable.ps1 start

# Vérifier le statut
.\homeflix-stable.ps1 status

# Reconstruire après modifications (mise à jour depuis DEV)
.\homeflix-stable.ps1 rebuild
```

**L'application s'ouvre dans une fenêtre Electron dédiée**

---

### Version DEV (Pour développement et tests)

```powershell
# Démarrer
.\homeflix-dev.ps1

# Démarrer sans nettoyage
.\homeflix-dev.ps1 -SkipCleanup
```

**Accès** : <http://localhost:5173>

**Note** : Les serveurs s'ouvrent dans des fenêtres PowerShell séparées. Fermez-les pour arrêter.

---

## 🔄 Workflow Recommandé

### Utilisation Normale

1. **Démarrez la version STABLE** pour regarder vos films/séries
2. La version stable reste identique jusqu'à ce que vous décidiez de la mettre à jour

### Développement et Tests

1. **Démarrez la version DEV** dans un terminal séparé
2. Faites vos modifications dans le code
3. Testez en temps réel (hot reload automatique)
4. Une fois satisfait, mettez à jour la version stable

### Mettre à jour la version STABLE après développement

Quand vos modifications en DEV sont prêtes :

```powershell
# Reconstruire la version stable avec les nouvelles modifications
.\homeflix-stable.ps1 rebuild
```

Cela va :

1. Copier le code actuel vers `homeflix-stable/`
2. Builder le frontend
3. Préparer l'application Electron

---

## 📂 Structure des Versions

### Dossier Version STABLE : `homeflix-stable/`

```text
homeflix-stable/
├── server/           # Backend Python (copie figée)
├── client/           # Frontend React (copie figée)
│   └── dist/        # Build production
├── electron/         # Application Electron
└── settings.yaml     # Configuration
```

### Dossier Version DEV : Racine du projet

Le code source actuel que vous pouvez modifier librement.

---

## 🎯 Différences Clés

| Aspect | Version STABLE | Version DEV |
|--------|----------------|-------------|
| **Type** | Application Electron | Serveurs localhost |
| **Interface** | Fenêtre dédiée | Navigateur web |
| **Port Backend** | Intégré | 8000 |
| **Port Frontend** | Intégré | 5173 |
| **Accès disques** | ✅ Direct (F:, G:, H:, I:) | ✅ Direct |
| **Modifications** | ❌ Figée | ✅ Temps réel |
| **Utilisation** | 🎬 Quotidienne | 🔧 Développement |

---

## 🛠️ Commandes Utiles

### Version STABLE

```powershell
# Construire pour la première fois
.\homeflix-stable.ps1 build

# Démarrer
.\homeflix-stable.ps1 start

# Vérifier l'installation
.\homeflix-stable.ps1 status

# Mettre à jour avec les changements de DEV
.\homeflix-stable.ps1 rebuild
```

### Version DEV

```powershell
# Démarrer
.\homeflix-dev.ps1

# Arrêter
.\stop-dev.ps1

# Nettoyer l'environnement
.\scripts\cleanup-dev.ps1
```

---

## 🔧 Résolution de Problèmes

### La version STABLE ne démarre pas

1. **Vérifier qu'elle est construite**

   ```powershell
   .\homeflix-stable.ps1 status
   ```

2. **Reconstruire**

   ```powershell
   .\homeflix-stable.ps1 rebuild
   ```

3. **Vérifier Node.js**

   ```powershell
   node --version
   npm --version
   ```

### Les vidéos ne s'affichent pas dans STABLE

La version STABLE utilise le même `settings.yaml` que la version DEV, donc vos chemins de vidéos (F:, G:, H:, I:) sont automatiquement reconnus.

Si problème :

1. Vérifiez `homeflix-stable/settings.yaml`
2. Les chemins doivent être identiques à la version DEV

### Conflit de versions

⚠️ **Ne démarrez qu'UNE SEULE version à la fois**

Si la version DEV tourne, arrêtez-la avant de lancer STABLE :

```powershell
.\stop-dev.ps1
```

---

## 📦 Prérequis

### Version STABLE

- Node.js 20+ (npm)
- Python 3.10+ (déjà installé pour DEV)
- ~500 MB d'espace disque

### Version DEV

- Python 3.10 (environnement virtuel `.venv310`)
- Node.js 20+
- FFmpeg installé

---

## 🎯 Quand utiliser quelle version ?

| Situation | Version à utiliser |
|-----------|-------------------|
| Regarder un film/série | 🟢 STABLE |
| Ajouter de nouveaux films | 🟢 STABLE |
| Utilisation quotidienne | 🟢 STABLE |
| Tester une nouvelle fonctionnalité | 🔵 DEV |
| Modifier le code | 🔵 DEV |
| Déboguer un problème | 🔵 DEV |
| Expérimenter sans risque | 🔵 DEV |

---

## 📝 Notes Importantes

1. **Les deux versions partagent la même base de données** (`server/homeflix.db`)
2. Les modifications en DEV n'affectent PAS la version STABLE
3. Pour mettre à jour STABLE, utilisez `rebuild` après vos tests
4. La version STABLE est une **copie isolée** dans `homeflix-stable/`
5. Vous pouvez supprimer `homeflix-stable/` sans affecter votre code DEV

---

## 🆘 Support

En cas de problème :

1. Vérifiez le statut : `.\homeflix-stable.ps1 status`
2. Reconstruisez : `.\homeflix-stable.ps1 rebuild`
3. Consultez `DEMARRAGE_RAPIDE.md` pour plus d'informations

---

## 🎬 Démarrage Conseillé

**Pour commencer immédiatement :**

```powershell
# 1. Construire la version STABLE (première fois)
.\homeflix-stable.ps1 build

# 2. Lancer l'application
.\homeflix-stable.ps1 start
```

L'application Electron s'ouvrira dans une fenêtre dédiée.

**Bon visionnage ! 🍿**
