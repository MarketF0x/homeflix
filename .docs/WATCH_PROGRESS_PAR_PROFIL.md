# 👤 Gestion de la Reprise de Lecture par Profil

## 📋 Vue d'Ensemble

Ce document décrit l'implémentation du système de reprise de lecture personnalisé par profil utilisateur dans Homeflix.

**Date d'implémentation** : Novembre 2025  
**Statut** : ✅ Implémenté et testé

---

## 🎯 Objectif

Chaque profil utilisateur doit avoir sa propre liste "À reprendre" et ses propres positions de lecture. Lorsque deux utilisateurs regardent le même film, chacun reprend à sa position personnelle.

**Avant** : La position de lecture était globale (tous les profils partageaient la même position)  
**Après** : Chaque profil a ses propres positions de lecture indépendantes

---

## 🗄️ Architecture Base de Données

### Nouvelle Table : `watch_progress`

```sql
CREATE TABLE watch_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    UNIQUE (profile_id, video_id)
);

CREATE INDEX idx_watch_progress_profile ON watch_progress(profile_id);
CREATE INDEX idx_watch_progress_video ON watch_progress(video_id);
CREATE INDEX idx_watch_progress_updated ON watch_progress(updated_at);
```

### Caractéristiques

- **Contrainte UNIQUE** : Un seul enregistrement par couple (profil, vidéo)
- **CASCADE DELETE** : Suppression automatique des progressions si le profil ou la vidéo est supprimé
- **Index** : Optimisation des requêtes par profil, vidéo et date

---

## 🔧 Implémentation Backend

### 1. Modèle SQLAlchemy (`server/core/models.py`)

```python
class WatchProgress(Base):
    __tablename__ = "watch_progress"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('profile_id', 'video_id', name='_profile_video_uc'),)
    
    profile = relationship("Profile")
    video = relationship("Video")
```

### 2. API Endpoints (`server/api/videos.py`)

#### POST `/api/progress` - Sauvegarder la progression

**Payload** :
```json
{
  "id": 123,
  "position": 3600,
  "profile_id": 1
}
```

**Comportement** :
- Crée ou met à jour l'entrée dans `watch_progress`
- Supprime l'entrée si >90% regardé (vidéo terminée)
- Limite à 10 vidéos en reprise par profil (supprime les plus anciennes)
- Maintient `video.last_position` pour compatibilité

#### GET `/api/progress/{video_id}?profile_id=X` - Récupérer la progression

**Réponse** :
```json
{
  "position": 3600,
  "updated_at": "2025-11-20T14:30:00"
}
```

### 3. Endpoint Catégories (`server/main.py`)

L'endpoint `/api/categories` a été modifié pour filtrer "À reprendre" par profil :

```python
# Récupérer les progressions de ce profil
from core.models import WatchProgress
progress_entries = s.query(WatchProgress).filter(
    WatchProgress.profile_id == profile_id
).order_by(WatchProgress.updated_at.desc()).limit(10).all()

# Construire la liste "to_resume" avec les positions par profil
for v in filtered:
    if v.id in video_ids_with_progress:
        position = video_ids_with_progress[v.id]
        if not v.duration_seconds or position < (v.duration_seconds * 0.9):
            v.last_position = position  # Injecté temporairement pour l'affichage
            to_resume.append(v)
```

---

## 💻 Implémentation Frontend

### 1. VideoPlayer - Chargement de la Position (`client/src/VideoPlayer.jsx`)

**useEffect de chargement** :
```javascript
useEffect(() => {
  const fetchSavedPosition = async () => {
    if (!currentProfile?.id) return;
    
    try {
      const response = await fetch(
        `${API}/progress/${video.id}?profile_id=${currentProfile.id}`
      );
      if (response.ok) {
        const data = await response.json();
        if (data.position && data.position > 0) {
          setSavedPosition(data.position);
          setCurrentTime(data.position);
        }
      }
    } catch (error) {
      console.warn('⚠️ Erreur chargement position:', error);
    }
  };
  
  fetchSavedPosition();
}, [video.id, currentProfile?.id]);
```

**Application de la position** :
```javascript
useEffect(() => {
  const videoElement = videoRef.current;
  if (!videoElement) return;

  // Charger la position sauvegardée (maintenant par profil)
  if (savedPosition && savedPosition > 0) {
    videoElement.currentTime = savedPosition;
  }
  // ...
}, [video, savedPosition]);
```

### 2. Sauvegarde de la Progression

**Fonction saveProgress** :
```javascript
const saveProgress = async (position) => {
  try {
    const profileId = currentProfile?.id;
    if (!profileId) {
      console.warn("Aucun profil sélectionné, progression non sauvegardée");
      return;
    }
    
    await fetch(`${API}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: video.id,
        position: position,
        profile_id: profileId,  // ✅ Ajout du profil
      }),
    });
  } catch (e) {
    console.error("Erreur sauvegarde progression:", e);
  }
};
```

**Intervalle de sauvegarde** : Toutes les 5 secondes + à la fermeture

### 3. Passage du Profil (`client/src/VideoDetail.jsx`)

```jsx
<VideoPlayer 
  video={video} 
  onClose={() => setShowPlayer(false)} 
  currentProfile={currentProfile}  // ✅ Ajout du prop
/>
```

---

## 🔄 Migration des Données

### Script : `server/migrate_watch_progress.py`

**Actions** :
1. Crée la table `watch_progress` si elle n'existe pas
2. Crée les index pour optimisation
3. Vérifie si la table `videos` existe (système sans cache)
4. Migre les positions existantes vers le profil principal (si applicable)
5. Conserve les colonnes `last_position` pour compatibilité

**Exécution** :
```powershell
cd server
python migrate_watch_progress.py
```

**Sortie attendue** :
```
🔄 Migration: Reprise de lecture par profil
============================================================
✅ Table 'watch_progress' existe déjà
```

ou si nouvelle installation :
```
📦 Création de la table 'watch_progress'...
   ✓ Table créée
📊 Création des index...
   ✓ Index créés
🔄 Migration des données existantes...
   ℹ️  Table 'videos' non trouvée
   → Système sans cache vidéo - aucune donnée à migrer
   → Le système démarre avec une table watch_progress vide
✅ Migration terminée avec succès!
```

---

## ✅ Vérifications

### 1. Structure Base de Données

```powershell
cd server
python check_db.py
```

Vérifier que `watch_progress` existe avec les colonnes :
- `id` (INTEGER)
- `profile_id` (INTEGER)
- `video_id` (INTEGER)
- `position` (INTEGER)
- `updated_at` (DATETIME)

### 2. Test Backend

```powershell
# Sauvegarder une position
curl -X POST http://localhost:8000/api/progress \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "position": 300, "profile_id": 1}'

# Récupérer la position
curl http://localhost:8000/api/progress/1?profile_id=1
```

### 3. Test Frontend

1. Se connecter avec le profil principal
2. Lancer une vidéo et avancer à 2 minutes
3. Fermer le lecteur
4. Changer de profil
5. Ouvrir la même vidéo → Doit démarrer à 0:00
6. Retourner au profil principal
7. Ouvrir la vidéo → Doit reprendre à 2 minutes

---

## 📊 Flux de Données

```
┌─────────────────┐
│  App.jsx        │
│  currentProfile │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VideoDetail.jsx │
│ (passe profil)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VideoPlayer.jsx │
│ ┌─────────────┐ │
│ │ useEffect   │ │──────┐
│ │ (mount)     │ │      │ GET /api/progress/{id}?profile_id=X
│ └─────────────┘ │      │
│                 │      ▼
│ ┌─────────────┐ │ ┌──────────────────┐
│ │ saveProgress│ │ │ Backend API      │
│ │ (interval)  │─┼─┤ /api/progress    │
│ └─────────────┘ │ │ watch_progress   │
└─────────────────┘ └──────────────────┘
         │                   │
         │ POST              │
         │ {id, position,    │
         │  profile_id}      │
         └───────────────────┘
```

---

## 🚀 Avantages

✅ **Expérience personnalisée** : Chaque utilisateur reprend où il s'est arrêté  
✅ **Indépendance** : Les enfants peuvent regarder leurs films sans perturber les parents  
✅ **Limite intelligente** : 10 vidéos max en reprise par profil (les plus récentes)  
✅ **Compatibilité** : Ancien champ `last_position` conservé pour transition douce  
✅ **Performance** : Index optimisés pour requêtes rapides  
✅ **Nettoyage automatique** : Suppression des progressions à >90% (vidéos terminées)

---

## 🔧 Maintenance

### Nettoyage Manuel des Progressions

```sql
-- Supprimer toutes les progressions d'un profil
DELETE FROM watch_progress WHERE profile_id = 2;

-- Supprimer les progressions d'une vidéo
DELETE FROM watch_progress WHERE video_id = 123;

-- Supprimer les progressions obsolètes (>30 jours)
DELETE FROM watch_progress 
WHERE updated_at < datetime('now', '-30 days');
```

### Vérification Intégrité

```sql
-- Nombre de progressions par profil
SELECT profile_id, COUNT(*) as count 
FROM watch_progress 
GROUP BY profile_id;

-- Progressions orphelines (vidéos supprimées)
SELECT * FROM watch_progress 
WHERE video_id NOT IN (SELECT id FROM videos);
```

---

## 📝 Notes Techniques

### Pourquoi Deux Systèmes ?

- **`watch_progress`** : Système moderne, par profil, avec index et contraintes
- **`videos.last_position`** : Ancien système, conservé pour :
  - Compatibilité avec code existant
  - Fallback si `profile_id` est `null`
  - Transition douce sans casser l'existant

### Optimisations Possibles

1. **Cleanup automatique** : Cron job pour supprimer progressions >30 jours
2. **Cache Redis** : Stocker les 10 dernières progressions en mémoire
3. **Sync temps réel** : WebSocket pour synchroniser entre appareils
4. **Analytics** : Tracker les habitudes de visionnage par profil

---

## 🐛 Dépannage

### Problème : Position non sauvegardée

**Vérifier** :
1. `currentProfile` est bien défini dans VideoPlayer
2. Console navigateur : "Aucun profil sélectionné" ?
3. Requête POST `/api/progress` retourne 200 OK

### Problème : Position globale au lieu de par profil

**Vérifier** :
1. Backend reçoit bien `profile_id` dans le payload
2. Table `watch_progress` existe avec données
3. Frontend charge depuis `/api/progress/{id}` et non `video.last_position`

### Problème : "À reprendre" vide

**Vérifier** :
1. Endpoint `/api/categories` reçoit `profile_id` en paramètre
2. Requête SQL filtre bien par `profile_id`
3. Au moins une vidéo a `position > 0` et `< 90%` pour ce profil

---

## 📚 Références

- Modèle : `server/core/models.py` → `WatchProgress`
- API : `server/api/videos.py` → `save_progress()`, `get_progress()`
- Frontend : `client/src/VideoPlayer.jsx` → `saveProgress()`, `useEffect()`
- Migration : `server/migrate_watch_progress.py`
- Vérification : `server/check_db.py`

---

**Auteur** : Système Homeflix  
**Version** : 1.0  
**Dernière mise à jour** : Novembre 2025
