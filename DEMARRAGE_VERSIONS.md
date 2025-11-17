# 🎬 DÉMARRAGE RAPIDE - HOMEFLIX

## Choix de la Version

Homeflix dispose de **2 versions séparées** :

### 🟢 VERSION STABLE (Recommandée)

**Application Electron standalone - pour utilisation quotidienne**

```powershell
# Première utilisation - construction
.\homeflix-stable.ps1 build

# Démarrer l'application
.\homeflix-stable.ps1 start
```

👉 L'application Electron s'ouvre dans une fenêtre dédiée

**Avantages** :

- Accès direct à tous vos disques (F:, G:, H:, I:)
- Application Windows native
- Stable et isolée
- Ne change pas jusqu'à mise à jour volontaire

---

### 🔵 VERSION DEV

**Code source modifiable - pour tests et développement**

```powershell
.\homeflix-dev.ps1
```

👉 Ouvrez <http://localhost:5173>

**Avantages** :

- Modifications en temps réel
- Hot reload automatique
- Parfait pour expérimenter

---

## ⚠️ Important

- **Version STABLE** : Utilise un serveur intégré dans l'application
- **Version DEV** : Utilise localhost:5173 et localhost:8000
- Ne démarrez qu'**UNE SEULE version à la fois**

---

## 🛑 Arrêter

**Version STABLE :**
Fermez simplement la fenêtre Electron

**Version DEV :**

```powershell
.\stop-dev.ps1
```

Ou fermez les fenêtres PowerShell des serveurs

---

## 📖 Documentation Complète

Consultez `GUIDE_VERSIONS.md` pour tous les détails
