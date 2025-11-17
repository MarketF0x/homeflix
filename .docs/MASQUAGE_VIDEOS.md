# Fonctionnalité de Masquage de Vidéos par Profil

## 📋 Vue d'ensemble

Cette fonctionnalité permet aux **profils secondaires** de masquer des vidéos sans les supprimer réellement du système. Les vidéos masquées restent visibles pour les autres profils.

## 🎯 Comportement selon le type de profil

### Profil Principal (is_main = 1)
- **Action**: Suppression réelle
- **Icône**: 🗑️ (poubelle)
- **Texte**: "Supprimer cette vidéo"
- **Effet**: La vidéo est supprimée de la base de données et peut aussi supprimer le fichier physique

### Profil Secondaire (is_main = 0)
- **Action**: Masquage uniquement
- **Icône**: 👁️‍🗨️ (œil barré)
- **Texte**: "Masquer cette vidéo"
- **Effet**: La vidéo est masquée pour ce profil mais reste visible pour les autres

## 🗄️ Base de données

### Nouvelle table: `hidden_videos`
```sql
CREATE TABLE hidden_videos (
    profile_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    hidden_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (profile_id, video_id),
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
)
```

**Index**: `idx_hidden_profile` sur `profile_id` pour des requêtes rapides

## 🔌 API Endpoints

### Masquer une vidéo
```
POST /api/profiles/hide-video
Body: { "profile_id": int, "video_id": int }
```

### Afficher une vidéo masquée
```
POST /api/profiles/unhide-video
Body: { "profile_id": int, "video_id": int }
```

### Liste des vidéos masquées
```
GET /api/profiles/{profile_id}/hidden-videos
```

### Supprimer/Masquer une vidéo
```
DELETE /api/videos/{video_id}?delete_file=bool&profile_id=int
```
- Si `profile_id` est fourni ET que c'est un profil secondaire → masque la vidéo
- Sinon → suppression réelle

### Lister les vidéos (avec filtrage)
```
GET /api/videos?mode=mixed&profile_id=int
GET /api/categories?mode=mixed&profile_id=int
```
- Si `profile_id` est fourni, les vidéos masquées pour ce profil sont exclues

## 🎨 Frontend

### Modifications dans VideoDetail.jsx
- Reçoit maintenant `currentProfile` en prop
- Affiche l'icône et le texte appropriés selon le type de profil
- Le bouton de suppression change dynamiquement

### Modifications dans App.jsx
- Passe `currentProfile` à tous les appels API (fetchCategories, deleteVideo)
- Recharge les catégories quand le profil change
- Transmet `currentProfile` au composant VideoDetail

### Modifications dans api.js
- `fetchVideos()` et `fetchCategories()` acceptent maintenant `profileId`
- `deleteVideo()` accepte `profileId` comme paramètre optionnel

## 📝 Migration

Pour créer la table `hidden_videos` :

```powershell
cd server
python migrate_hidden_videos.py
```

## ✨ Cas d'usage

1. **Enfant avec profil secondaire** : Peut masquer des films d'horreur sans les supprimer
2. **Utilisateur temporaire** : Peut masquer des contenus sans affecter les autres
3. **Profil invité** : Peut personnaliser sa vue sans modifier la bibliothèque principale

## 🔒 Sécurité

- Les profils secondaires **ne peuvent pas** masquer des vidéos si leur profil est principal
- Les vidéos masquées sont automatiquement supprimées si le profil est supprimé (CASCADE)
- Chaque profil a sa propre liste de vidéos masquées indépendante

## 🚀 Déploiement

1. Exécuter la migration : `python migrate_hidden_videos.py`
2. Redémarrer le serveur backend
3. Recharger le frontend (CTRL+F5)
4. La fonctionnalité est immédiatement active pour tous les profils secondaires
