# 📝 GUIDE D'UTILISATION - HOMEFLIX

## 🚀 Démarrage Rapide

### Méthode 1 : Double-clic (Recommandée)
1. Double-cliquez sur **`DEMARRER.bat`** ou **`DEMARRER.ps1`**
2. Attendez que les serveurs démarrent (automatique)
3. Le navigateur s'ouvre automatiquement sur http://localhost:5173

### Méthode 2 : Ligne de commande
```powershell
.\start.ps1
```

## 🛑 Arrêter Homeflix

- Appuyez sur **Ctrl+C** dans la fenêtre PowerShell
- Les serveurs s'arrêtent automatiquement

## 📊 Les serveurs fonctionnent en arrière-plan

Les serveurs Backend et Frontend fonctionnent en **arrière-plan** (pas de fenêtres supplémentaires).
Vous voyez uniquement les **logs en temps réel** dans la fenêtre PowerShell principale.

## 🌐 URLs d'accès

- **Interface Web** : http://localhost:5173
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 📁 Scripts disponibles

| Script | Description |
|--------|-------------|
| `start.ps1` | Script principal optimisé |
| `DEMARRER.bat` | Raccourci Windows (double-clic) |
| `DEMARRER.ps1` | Raccourci PowerShell |

## 🔧 Dépannage

### Le port 8000 ou 5173 est déjà utilisé
Le script libère automatiquement les ports. Si le problème persiste :
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "node"} | Stop-Process -Force
```

### Erreur "Environnement virtuel Python introuvable"
Lancez d'abord l'installation :
```powershell
.\install.ps1
```

### Le backend ne démarre pas
Vérifiez les logs dans la console. Cause fréquente : clé API TMDb invalide dans `settings.yaml`

## 💡 Fonctionnalités

- ✅ Scan automatique des vidéos toutes les 10 minutes
- ✅ Métadonnées enrichies via TMDb
- ✅ Génération automatique de miniatures
- ✅ Streaming vidéo avec support du seek
- ✅ Interface multilingue (FR/EN/DE/ES)

## 📖 Documentation complète

Consultez les fichiers markdown pour plus d'informations :
- `README_UTILISATION.md` - Guide complet
- `RAPPORT_OPTIMISATION.md` - Optimisations appliquées
- `COMMENT_DEMARRER.md` - Guide de démarrage détaillé

---

**Version** : 3.0  
**Dernière mise à jour** : 11 novembre 2025
