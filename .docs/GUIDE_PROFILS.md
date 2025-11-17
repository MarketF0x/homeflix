# 👥 Système de Gestion des Profils Homeflix

## 📋 Vue d'ensemble

Homeflix intègre désormais un système complet de gestion des profils utilisateurs, permettant de personnaliser l'expérience de visionnage pour chaque membre de la famille.

## ✨ Fonctionnalités

### 🎭 Profils Utilisateurs
- **Profil Principal** : Créé automatiquement avec tous les droits d'administration
- **Profils Secondaires** : Créez autant de profils que nécessaire pour votre famille
- **Personnalisation** : Chaque profil peut avoir un nom unique et un avatar personnalisé

### 🎨 Avatars
Choisissez parmi 12 avatars par défaut :
- **6 avatars personnages** (bleu, rose, vert, orange, violet, cyan)
- **6 avatars abstraits** (formes géométriques colorées)

### 🔒 Restrictions (Profils Secondaires)
- **Masquer le contenu adulte** : Filtrage automatique du contenu inapproprié
- **Mode enfants** : Limite l'affichage au contenu tout public uniquement

## 🚀 Utilisation

### Premier Lancement
1. Au démarrage de l'application, l'écran de sélection des profils s'affiche automatiquement
2. Un profil principal est déjà créé par défaut
3. Sélectionnez le profil principal pour commencer

### Créer un Nouveau Profil
1. Sur l'écran de sélection, cliquez sur **"+ Ajouter un profil"**
2. Saisissez un nom pour le profil (max 20 caractères)
3. Choisissez un avatar parmi les 12 disponibles
4. (Optionnel) Activez les restrictions :
   - ☑️ Masquer le contenu adulte
   - ☑️ Mode enfants
5. Cliquez sur **"Créer"**

### Modifier un Profil
1. Sur l'écran de sélection, survolez un profil secondaire
2. Cliquez sur l'icône **✏️** (Modifier)
3. Modifiez le nom, l'avatar ou les restrictions
4. Cliquez sur **"Modifier"**

### Supprimer un Profil
1. Sur l'écran de sélection, survolez un profil secondaire
2. Cliquez sur l'icône **🗑️** (Supprimer)
3. Confirmez la suppression

⚠️ **Note** : Le profil principal ne peut pas être supprimé ou modifié.

### Changer de Profil
- Cliquez sur l'avatar de profil en haut à droite de l'interface
- Vous serez redirigé vers l'écran de sélection des profils

## 🔧 Installation & Migration

### Migration de la Base de Données
Si vous mettez à jour depuis une version antérieure, exécutez :

```powershell
cd server
..\.venv310\Scripts\python.exe migrate_profiles.py
```

Cette commande :
- Crée la table `profiles` dans la base de données
- Ajoute automatiquement le profil principal par défaut

### Structure de la Base de Données

Table `profiles` :
- `id` : Identifiant unique (INTEGER PRIMARY KEY)
- `name` : Nom du profil (TEXT)
- `avatar` : Fichier avatar (TEXT)
- `is_main` : Profil principal ? (INTEGER 0/1)
- `restrictions` : Restrictions JSON (TEXT)
- `created_at` : Date de création (TIMESTAMP)

## 📁 Architecture

### Backend
- **`server/api/profiles.py`** : API REST pour les profils
  - `GET /api/profiles` : Liste tous les profils
  - `POST /api/profiles` : Crée un nouveau profil
  - `PUT /api/profiles/{id}` : Modifie un profil
  - `DELETE /api/profiles/{id}` : Supprime un profil

- **`server/migrate_profiles.py`** : Script de migration

### Frontend
- **`client/src/ProfileSelector.jsx`** : Écran de sélection des profils
- **`client/src/ProfileManager.jsx`** : Création/modification de profils
- **`client/public/avatars/`** : Images SVG des avatars (12 fichiers)

### Styles
- **`client/src/index.css`** : Styles CSS complets pour les profils

## 🎯 Fonctionnalités Futures

### Phase 1 (Actuelle) ✅
- [x] Création et gestion des profils
- [x] Sélection de profil au démarrage
- [x] Avatars personnalisés
- [x] Restrictions de base

### Phase 2 (À venir)
- [ ] Historique de visionnage par profil
- [ ] Recommandations personnalisées
- [ ] Code PIN pour les profils
- [ ] Limitation du temps d'écran (mode enfants)
- [ ] Statistiques de visionnage par profil

### Phase 3 (À venir)
- [ ] Avatar personnalisé (upload d'image)
- [ ] Thèmes de couleur par profil
- [ ] Favoris par profil
- [ ] Listes de lecture personnalisées

## 🐛 Dépannage

### Le profil principal n'apparaît pas
```powershell
# Exécutez à nouveau la migration
cd server
..\.venv310\Scripts\python.exe migrate_profiles.py
```

### Les avatars ne s'affichent pas
- Vérifiez que le dossier `client/public/avatars/` existe
- Vérifiez que les 12 fichiers SVG sont présents
- Videz le cache du navigateur (Ctrl+Shift+R)

### Impossible de créer un profil
- Vérifiez que le serveur backend est démarré (port 8000)
- Vérifiez les logs du serveur pour les erreurs
- Vérifiez que la table `profiles` existe dans la base de données

## 📝 Notes Techniques

### Format des Restrictions
Les restrictions sont stockées au format JSON dans la base de données :

```json
{
  "hideAdult": true,
  "kidsMode": false
}
```

### Avatars SVG
Les avatars sont au format SVG (vectoriel) pour :
- Taille de fichier minimale
- Qualité parfaite à toutes les résolutions
- Compatibilité universelle

### Sécurité
- Le profil principal (`is_main=1`) est protégé contre la suppression
- Les restrictions sont appliquées côté frontend (pas encore côté backend)
- Les avatars sont servis depuis le dossier public (pas d'upload pour l'instant)

## 🔐 Permissions

| Action | Profil Principal | Profils Secondaires |
|--------|-----------------|---------------------|
| Voir tous les films | ✅ | ✅* |
| Modifier les paramètres | ✅ | ❌ |
| Scanner la bibliothèque | ✅ | ❌ |
| Créer des profils | ✅ | ❌ |
| Supprimer des vidéos | ✅ | ❌ |

*Sous réserve des restrictions configurées

## 🎨 Personnalisation

### Ajouter de Nouveaux Avatars
1. Créez un fichier SVG (200x200px recommandé)
2. Placez-le dans `client/public/avatars/`
3. Ajoutez le nom du fichier dans `ProfileSelector.jsx` :

```javascript
const AVAILABLE_AVATARS = [
  "avatar_01.svg",
  // ... autres avatars
  "mon_avatar.svg", // Votre nouvel avatar
];
```

## 📞 Support

Pour toute question ou problème :
1. Consultez d'abord ce guide
2. Vérifiez les logs du serveur (`server/homeflix.log`)
3. Vérifiez la console du navigateur (F12)

---

**Version** : 1.0  
**Date** : Novembre 2025  
**Auteur** : Homeflix Team
