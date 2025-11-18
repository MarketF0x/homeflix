# Correctifs VideoPlayer - Novembre 2025

## Problème identifié

Le composant `VideoPlayer` souffrait de **multiples re-renders** provoquant :
- Montages/démontages successifs du composant
- Rechargements répétés de la vidéo
- Erreur `DOMException: The fetching process for the media resource was aborted`
- Vidéos qui ne se lancent pas correctement

### Symptômes observés dans les logs
```
🎬 VideoPlayer monté - Profil actuel: fred ID: 2 (répété plusieurs fois)
Uncaught (in promise) DOMException: The fetching process for the media resource was aborted
```

## Corrections apportées

### 1. Stabilisation des dépendances useEffect (ligne 191)

**Avant :**
```jsx
}, [useTranscode, selectedAudioTrack, selectedSubtitleTrack, videoUrl]);
```

**Problème :** `videoUrl` changeait à chaque modification d'état, causant des rechargements en boucle.

**Après :**
```jsx
}, [useTranscode, selectedAudioTrack, selectedSubtitleTrack, transcodeQuality]);
```

**Bénéfice :** Rechargements uniquement quand nécessaire (changement de mode ou de piste).

---

### 2. Ajout des listeners d'état de lecture (ligne 520)

**Nouveaux listeners ajoutés :**
```jsx
const handleCanPlay = () => {
  console.log('✅ canplay - La vidéo peut commencer à jouer');
  setIsLoading(false);
  setLoadInfo(null);
};

const handleCanPlayThrough = () => {
  console.log('✅ canplaythrough - La vidéo peut être jouée sans interruption');
  setIsLoading(false);
  setLoadInfo(null);
  retryCountRef.current = 0;
  retryDelayRef.current = 1000;
};

const handleWaiting = () => {
  console.log('⏳ waiting - La vidéo est en attente de données...');
  setIsLoading(true);
};

const handlePlaying = () => {
  console.log('▶️ playing - La vidéo a commencé à jouer');
  setIsPlaying(true);
  setIsLoading(false);
  setLoadInfo(null);
};

const handlePause = () => {
  console.log('⏸️ pause - La vidéo est en pause');
  setIsPlaying(false);
};
```

**Bénéfice :** Meilleure détection et gestion des états de chargement de la vidéo.

---

### 3. Protection contre les lectures multiples au montage (ligne 30)

**Ajout d'une référence :**
```jsx
const hasAttemptedPlayRef = useRef(false);
```

**Modification du code de lecture :**
```jsx
// Tenter de lire automatiquement (une seule fois au montage)
if (!hasAttemptedPlayRef.current) {
  hasAttemptedPlayRef.current = true;
  
  const playPromise = videoElement.play();
  // ...
}
```

**Bénéfice :** Évite les tentatives multiples de lecture qui causent l'erreur "aborted".

---

### 4. Réinitialisation de la ref lors des rechargements (ligne 197)

**Dans l'effet de rechargement :**
```jsx
// Réinitialiser la ref pour permettre une nouvelle tentative de lecture
hasAttemptedPlayRef.current = false;
```

**Bénéfice :** Permet la lecture après un basculement de mode ou changement de piste.

---

### 5. Stabilisation des dépendances du useEffect principal (ligne 710)

**Avant :**
```jsx
}, [video, savedPosition, saveProgress]);
```

**Problème :** `video` est un objet qui peut changer de référence.

**Après :**
```jsx
}, [video.id, video.path, savedPosition, saveProgress, useTranscode, transcodeQuality]);
```

**Bénéfice :** Dépendances stables basées sur des valeurs primitives.

---

### 6. Ajout du nettoyage des nouveaux listeners (ligne 710)

**Nettoyage complet dans le return :**
```jsx
videoElement.removeEventListener('canplay', handleCanPlay);
videoElement.removeEventListener('canplaythrough', handleCanPlayThrough);
videoElement.removeEventListener('waiting', handleWaiting);
videoElement.removeEventListener('playing', handlePlaying);
videoElement.removeEventListener('pause', handlePause);
```

**Bénéfice :** Évite les fuites mémoire et les listeners orphelins.

---

## Résultat attendu

✅ **Le VideoPlayer ne se monte plus plusieurs fois**  
✅ **La vidéo se charge une seule fois au démarrage**  
✅ **Plus d'erreur "DOMException: aborted"**  
✅ **Meilleure détection des états de chargement**  
✅ **Transitions fluides entre modes direct/transcodage**  

## Tests recommandés

1. ✅ Lancer une vidéo MP4 (mode direct)
2. ✅ Lancer une vidéo MKV (mode transcodage)
3. ✅ Changer de piste audio pendant la lecture
4. ✅ Changer de piste sous-titre
5. ✅ Vérifier les logs - le montage ne doit apparaître qu'une fois
6. ✅ Vérifier qu'il n'y a plus d'erreur "aborted" dans la console

## Fichiers modifiés

- `client/src/VideoPlayer.jsx` : Corrections des re-renders et amélioration de la gestion des états

## Notes techniques

Les re-renders étaient causés par :
1. Dépendances instables dans les `useEffect` (objets/fonctions recréés)
2. Absence de protection contre les lectures multiples
3. Listeners d'état manquants pour détecter les transitions

Ces corrections stabilisent le cycle de vie du composant et améliorent significativement la fiabilité de la lecture vidéo.
