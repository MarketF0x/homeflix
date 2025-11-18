import { useState, useRef, useEffect, useCallback, useLayoutEffect } from "react";
import { thumbURL, API, getApiBaseUrl } from "./config.js";
import { useI18n } from "./i18n";

export default function VideoPlayer({ video, onClose, currentProfile }) {
  // Qualité dynamique pour le transcodage (fast si buffer faible)
  const [transcodeQuality, setTranscodeQuality] = useState("medium");
  // LOG CRITIQUE : Afficher le profil reçu

  const { language } = useI18n(); // Récupère la langue choisie par l'utilisateur
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);  // Initialisé à 0, chargé depuis l'API
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [loadInfo, setLoadInfo] = useState(null); // Message d'information (non-erreur)
  const [audioTracks, setAudioTracks] = useState([]);
  const [subtitleTracks, setSubtitleTracks] = useState([]);
  const [currentAudioTrack, setCurrentAudioTrack] = useState(0);
  const [currentSubtitleTrack, setCurrentSubtitleTrack] = useState(-1); // -1 = désactivé
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const [bufferProgress, setBufferProgress] = useState(0);
  const [isStalled, setIsStalled] = useState(false);
  const [stalledTime, setStalledTime] = useState(0);
  const [savedPosition, setSavedPosition] = useState(null);  // Position chargée depuis l'API
  const [playbackRate, setPlaybackRate] = useState(1); // Vitesse de lecture (0.5x à 2x)
  const [isPiP, setIsPiP] = useState(false); // Picture-in-Picture
  
  // Utiliser useRef pour retryCount car il est utilisé dans des closures (setTimeout)
  const retryCountRef = useRef(0);
  const lastBufferCheckRef = useRef(0);
  const retryDelayRef = useRef(1000); // Délai retry exponentiel
  const hasAttemptedPlayRef = useRef(false); // Empêcher les tentatives multiples de lecture au montage
  
  // Déterminer si on doit forcer le transcodage dès le départ
  const videoExt = video.path.toLowerCase().split('.').pop();
  // ✅ STRATÉGIE: Utiliser le streaming direct UNIQUEMENT pour MP4 et WEBM (formats web natifs)
  // Tous les autres formats (MKV, AVI, etc.) passent par le transcodage FFmpeg
  const needsTranscodeByDefault = !['mp4', 'webm'].includes(videoExt);
  
  const [useTranscode, setUseTranscode] = useState(needsTranscodeByDefault); // État pour basculer vers transcodage
  const [selectedAudioTrack, setSelectedAudioTrack] = useState(1); // Index de la piste audio choisie (commence à 1 généralement)
  const [selectedSubtitleTrack, setSelectedSubtitleTrack] = useState(-1); // -1 = pas de sous-titre
  const [availableTracks, setAvailableTracks] = useState(null); // Pistes disponibles du fichier source
  
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const controlsTimeoutRef = useRef(null);
  const loadingTimeoutRef = useRef(null);
  const stalledCheckRef = useRef(null);

  // Construire l'URL de la vidéo avec l'API dynamique
  // Stratégie intelligente : 
  // - MKV : essayer direct (H.264 dans MKV fonctionne sur navigateurs modernes)
  // - AVI/WMV/FLV : transcodage direct (rarement supportés)
  
  // ✅ Utiliser directement getApiBaseUrl() pour avoir la bonne URL de base
  const baseUrl = getApiBaseUrl();
  
  // ✅ STRATÉGIE INTELLIGENTE :
  // - MP4/WEBM : Toujours streaming direct (natifs HTML5)
  // - MKV : Essayer direct d'abord (H.264 dans MKV fonctionne souvent)
  // - AVI/WMV/FLV : Transcodage direct (rarement supportés nativement)
  const directUrl = `${baseUrl}/api/stream?path=${encodeURIComponent(video.path)}`;
  const transcodeUrl = `${baseUrl}/api/stream/transcode?path=${encodeURIComponent(video.path)}&audio_track=${selectedAudioTrack}${selectedSubtitleTrack >= 0 ? `&subtitle_track=${selectedSubtitleTrack}` : ''}&quality=${transcodeQuality}`;
  // Utiliser transcodage si demandé, sinon streaming direct
  const videoUrl = useTranscode ? transcodeUrl : directUrl;
  
  // 🔍 Log de diagnostic des URLs de streaming

  // Fonction de sauvegarde de la progression (définie avant les useEffect pour être accessible)
  const saveProgress = useCallback(async (position) => {
    try {
      const profileId = currentProfile?.id;
      if (!profileId) {

        return;
      }

      const response = await fetch(`${API}/progress`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: video.id,
          position: position,
          profile_id: profileId,
        }),
      });
      
      if (!response.ok) {

      } else {

      }
    } catch (e) {

    }
  }, [currentProfile?.id, video.id]);

  // Bloquer le scroll de la page principale quand le player est ouvert
  // useLayoutEffect s'exécute AVANT le paint pour éviter le flash
  useLayoutEffect(() => {
    window.scrollTo(0, 0); // Scroll instantané en haut
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  // Gestion du bouton retour pour fermer le lecteur
  useEffect(() => {
    const handlePopState = (e) => {
      e.preventDefault();

      onClose();
    };

    // Ajouter un état à l'historique pour le lecteur
    window.history.pushState({ videoPlayer: true }, "", "");
    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [onClose]);

  // Charger la position sauvegardée depuis l'API (par profil)
  useEffect(() => {
    const fetchSavedPosition = async () => {
      if (!currentProfile?.id) return;
      
      try {
        const response = await fetch(`${API}/progress/${video.id}?profile_id=${currentProfile.id}`);
        if (response.ok) {
          const data = await response.json();
          if (data.position && data.position > 0) {
            setSavedPosition(data.position);
            setCurrentTime(data.position);
          }
        }
      } catch (error) {

      }
    };
    
    fetchSavedPosition();
  }, [video.id, currentProfile?.id]);

  // Charger les pistes audio/sous-titres disponibles au montage
  useEffect(() => {
    const fetchTracks = async () => {
      try {

        const response = await fetch(`${baseUrl}/api/stream/tracks?path=${encodeURIComponent(video.path)}`);
        if (response.ok) {
          const tracks = await response.json();

          setAvailableTracks(tracks);
          
          // Auto-sélectionner la première piste audio française si disponible
          const frenchTrack = tracks.audio.find(t => t.language === 'fre' || t.language === 'fr');
          if (frenchTrack) {
            setSelectedAudioTrack(frenchTrack.index);
          } else if (tracks.audio.length > 0) {
            setSelectedAudioTrack(tracks.audio[0].index);
          }
        } else {

        }
      } catch (error) {

      }
    };
    
    fetchTracks();
  }, [video.path, baseUrl]);

  // Effet pour recharger la vidéo quand on bascule vers transcodage OU change de piste
  // ⚠️ NE PAS INCLURE videoUrl dans les dépendances car il change tout le temps
  useEffect(() => {
    if (videoRef.current) {
      const currentPos = videoRef.current.currentTime || 0;

      setIsLoading(true);
      setLoadError(null);
      
      // Réinitialiser la ref pour permettre une nouvelle tentative de lecture
      hasAttemptedPlayRef.current = false;
      
      videoRef.current.load();
      
      const handleCanPlay = () => {

        if (currentPos > 0) {
          videoRef.current.currentTime = currentPos;
        }
        setIsLoading(false);
        videoRef.current.play().catch(() => {});
        videoRef.current.removeEventListener('canplay', handleCanPlay);
      };
      
      const handleError = () => {

        setIsLoading(false);
        videoRef.current.removeEventListener('error', handleError);
      };
      
      videoRef.current.addEventListener('canplay', handleCanPlay);
      videoRef.current.addEventListener('error', handleError);
      
      return () => {
        if (videoRef.current) {
          videoRef.current.removeEventListener('canplay', handleCanPlay);
          videoRef.current.removeEventListener('error', handleError);
        }
      };
    }
  }, [useTranscode, selectedAudioTrack, selectedSubtitleTrack, transcodeQuality]);

  // Messages informatifs progressifs - MASQUÉS dès que la vidéo démarre
  useEffect(() => {
    // Si la vidéo joue, masquer immédiatement tous les messages
    if (isPlaying && !isLoading) {
      setLoadInfo(null);
      return;
    }
    
    if (!isLoading) {
      setLoadInfo(null);
      return;
    }

    // Message à 10 secondes
    const timeout10 = setTimeout(() => {
      if (isLoading && !isPlaying) {
        setLoadInfo("⏳ Chargement en cours...");
      }
    }, 10000);

    // Message à 30 secondes
    const timeout30 = setTimeout(() => {
      if (isLoading && !isPlaying) {
        setLoadInfo("⏳ Vidéo volumineuse - buffering initial...");
      }
    }, 30000);

    return () => {
      clearTimeout(timeout10);
      clearTimeout(timeout30);
    };
  }, [isLoading, isPlaying]); // Ajouter isPlaying comme dépendance

  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    // Charger la position sauvegardée (maintenant chargée depuis l'API par profil)
    if (savedPosition && savedPosition > 0) {
      videoElement.currentTime = savedPosition;
    }

    // Détecter les pistes audio disponibles
    const detectAudioTracks = () => {
      const tracks = videoElement.audioTracks;
      if (tracks && tracks.length > 0) {
        const trackList = Array.from(tracks).map((track, index) => ({
          index,
          label: track.label || `Piste audio ${index + 1}`,
          language: track.language || 'unknown',
          enabled: track.enabled
        }));
        setAudioTracks(trackList);

        // AUTO-SÉLECTION : Prioriser la langue choisie dans les paramètres
        autoSelectPreferredAudioTrack(tracks, trackList);
      } else {

        // PROBLÈME : Pas de piste audio détectée
        // Solution : Basculer vers transcodage FFmpeg
        if (!useTranscode) {

          setLoadInfo('🔄 Activation transcodage audio...');
          setUseTranscode(true);
          setRetryCount(0);
          return; // Le useEffect va recharger la vidéo
        }
        
        // Même sans pistes multiples, on affiche la piste par défaut
        setAudioTracks([{ index: 0, label: 'Audio par défaut', language: 'unknown', enabled: true }]);
      }
    };

    // Fonction pour auto-sélectionner la piste audio dans la langue choisie
    const autoSelectPreferredAudioTrack = (tracks, trackList) => {
      // Mapping des codes de langue (ISO 639-1 et ISO 639-2)
      const languageMap = {
        'fr': ['fr', 'fra', 'fre'],
        'en': ['en', 'eng'],
        'de': ['de', 'deu', 'ger'],
        'es': ['es', 'spa']
      };
      
      // Mots-clés pour chaque langue
      const languageKeywords = {
        'fr': ['français', 'french', 'vf', 'truefrench', 'vff', 'vfq'],
        'en': ['english', 'eng', 'vo', 'original'],
        'de': ['german', 'deutsch', 'allemand'],
        'es': ['spanish', 'español', 'espagnol', 'castellano']
      };
      
      const preferredCodes = languageMap[language] || [language];
      const keywords = languageKeywords[language] || [];
      
      // Priorité 1 : Code de langue ISO
      let preferredTrackIndex = trackList.findIndex(t => 
        t.language && preferredCodes.some(code => t.language.toLowerCase() === code)
      );
      
      // Priorité 2 : Mots-clés dans le label
      if (preferredTrackIndex === -1 && keywords.length > 0) {
        preferredTrackIndex = trackList.findIndex(t => 
          t.label && keywords.some(kw => t.label.toLowerCase().includes(kw))
        );
      }
      
      if (preferredTrackIndex !== -1) {
        // Désactiver toutes les pistes
        for (let i = 0; i < tracks.length; i++) {
          tracks[i].enabled = false;
        }
        // Activer la piste préférée
        tracks[preferredTrackIndex].enabled = true;
        setCurrentAudioTrack(preferredTrackIndex); // Mettre à jour l'état pour l'interface

      } else {

        setCurrentAudioTrack(0);
      }
    };

    // Détecter les sous-titres disponibles
    const detectSubtitles = () => {
      const tracks = videoElement.textTracks;
      if (tracks && tracks.length > 0) {
        const trackList = Array.from(tracks).map((track, index) => ({
          index,
          label: track.label || `Sous-titre ${index + 1}`,
          language: track.language || 'unknown',
          kind: track.kind
        }));
        setSubtitleTracks(trackList);

        // AUTO-SÉLECTION : Prioriser les sous-titres dans la langue choisie
        autoSelectPreferredSubtitles(tracks, trackList);
      }
    };

    // Fonction pour auto-sélectionner les sous-titres dans la langue choisie
    const autoSelectPreferredSubtitles = (tracks, trackList) => {
      // Mapping des codes de langue
      const languageMap = {
        'fr': ['fr', 'fra', 'fre'],
        'en': ['en', 'eng'],
        'de': ['de', 'deu', 'ger'],
        'es': ['es', 'spa']
      };
      
      const languageKeywords = {
        'fr': ['français', 'french'],
        'en': ['english', 'eng'],
        'de': ['german', 'deutsch', 'allemand'],
        'es': ['spanish', 'español', 'espagnol']
      };
      
      const preferredCodes = languageMap[language] || [language];
      const keywords = languageKeywords[language] || [];
      
      // Priorité 1 : Code de langue ISO
      let preferredSubIndex = trackList.findIndex(t => 
        t.language && preferredCodes.some(code => t.language.toLowerCase() === code)
      );
      
      // Priorité 2 : Mots-clés dans le label
      if (preferredSubIndex === -1 && keywords.length > 0) {
        preferredSubIndex = trackList.findIndex(t => 
          t.label && keywords.some(kw => t.label.toLowerCase().includes(kw))
        );
      }
      
      if (preferredSubIndex !== -1) {
        // Désactiver tous les sous-titres
        for (let i = 0; i < tracks.length; i++) {
          tracks[i].mode = 'hidden';
        }
        // Le sous-titre préféré est prêt mais pas affiché par défaut
        setCurrentSubtitleTrack(preferredSubIndex); // Préparer pour activation facile

      } else {

        setCurrentSubtitleTrack(-1);
      }
    };

    // Écouter l'événement loadedmetadata pour détecter les pistes
    const handleLoadedMetadata = () => {
      detectAudioTracks();
      detectSubtitles();
      
      // Mettre à jour la durée dès que les métadonnées sont chargées
      if (!isNaN(videoElement.duration) && isFinite(videoElement.duration)) {
        setDuration(videoElement.duration);

      }
      
      // DÉTECTION PROBLÈME VIDÉO : Vérifier si la vidéo a une dimension valide
      // Si width/height = 0, le codec vidéo n'est pas supporté
      if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {

        if (!useTranscode && retryCountRef.current === 0) {

          setLoadInfo('🔄 Codec vidéo incompatible détecté - activation transcodage...');
          setUseTranscode(true);
          retryCountRef.current = 1; // Marquer qu'on a essayé
          return;
        } else if (useTranscode && retryCountRef.current < 2) {
          // Tenter le streaming direct en dernier recours

          setLoadInfo('🔄 Échec transcodage - tentative lecture directe...');
          setUseTranscode(false);
          retryCountRef.current = 2;
          return;
        } else {
          setLoadError('❌ Erreur : Impossible de lire cette vidéo. Le fichier est probablement corrompu ou utilise un codec non supporté par FFmpeg.');

        }
      } else {

        retryCountRef.current = 0; // Réinitialiser si la vidéo fonctionne
      }
    };
    
    videoElement.addEventListener('loadedmetadata', handleLoadedMetadata);

    // ✅ OPTIMISATION BUFFER : Toujours preload auto pour maximiser le buffering
    videoElement.preload = "auto";

    // ✅ MONITORING BUFFER AVANCÉ : Surveillance du buffer range
    const updateBufferProgress = () => {
      if (videoElement.buffered.length > 0) {
        const bufferedEnd = videoElement.buffered.end(videoElement.buffered.length - 1);
        const duration = videoElement.duration;
        if (duration > 0) {
          const bufferPercent = (bufferedEnd / duration) * 100;
          setBufferProgress(bufferPercent);
          // Afficher un log utilisateur si le buffer est faible
          if (bufferPercent < 10 && !videoElement.paused && videoElement.readyState < 3) {
            setLoadInfo("⚠️ Votre connexion semble lente, le chargement peut prendre du temps. Merci de patienter...");

            // Compteur de buffer faible
            if (!window._bufferLowCount) window._bufferLowCount = 0;
            window._bufferLowCount++;
            // Si le buffer est faible 3 fois de suite, passer en qualité 'fast'
            if (window._bufferLowCount >= 3 && useTranscode && transcodeQuality !== "fast") {
              setTranscodeQuality("fast");
              setLoadInfo("⏩ Mode rapide activé pour améliorer la fluidité (qualité réduite)");
              window._bufferLowCount = 0;
            }
          } else {
            // Si le buffer est bon, réinitialiser le compteur
            window._bufferLowCount = 0;
          }
        }
      }
    };

    videoElement.addEventListener('progress', updateBufferProgress);
    videoElement.addEventListener('timeupdate', updateBufferProgress);

    // ✅ RETRY EXPONENTIEL : Gestion intelligente des erreurs réseau et de décodage
    const handleNetworkError = (e) => {
      const error = videoElement.error;
      
      if (error) {

        // MEDIA_ERR_SRC_NOT_SUPPORTED (code 4) ou MEDIA_ERR_DECODE (code 3)
        if (error.code === 3 || error.code === 4) {

          if (!useTranscode && retryCountRef.current === 0) {

            setLoadInfo('🔄 Format non supporté - activation transcodage...');
            setUseTranscode(true);
            retryCountRef.current = 1;
            return;
          } else if (useTranscode && retryCountRef.current < 2) {
            // Si le transcodage échoue, tenter le streaming direct en dernier recours

            setLoadInfo('🔄 Échec transcodage - tentative lecture directe...');
            setUseTranscode(false);
            retryCountRef.current = 2; // Marquer qu'on a tout essayé
            return;
          } else {
            // Tout a échoué
            setLoadError('❌ Erreur : Impossible de lire cette vidéo. Le fichier est probablement corrompu ou utilise un codec non supporté.');

            return;
          }
        }
      }

      // Calculer délai exponentiel : 1s, 2s, 4s, 8s, 16s max
      const delay = Math.min(retryDelayRef.current, 16000);
      retryCountRef.current += 1;
      
      if (retryCountRef.current <= 5) {

        setLoadInfo(`🔄 Reconnexion en cours (${retryCountRef.current}/5)...`);
        
        setTimeout(() => {
          const currentPos = videoElement.currentTime;
          videoElement.load();
          
          videoElement.addEventListener('loadeddata', () => {
            videoElement.currentTime = currentPos;
            videoElement.play().catch(() => {});
          }, { once: true });
          
          retryDelayRef.current *= 2; // Doubler le délai pour le prochain retry
        }, delay);
      } else {
        setLoadError('❌ Impossible de charger la vidéo après 5 tentatives');
        retryCountRef.current = 0;
        retryDelayRef.current = 1000;
      }
    };
    
    // Helper pour afficher le nom du code d'erreur
    const getErrorCodeName = (code) => {
      const codes = {
        1: 'MEDIA_ERR_ABORTED',
        2: 'MEDIA_ERR_NETWORK',
        3: 'MEDIA_ERR_DECODE',
        4: 'MEDIA_ERR_SRC_NOT_SUPPORTED'
      };
      return codes[code] || 'UNKNOWN';
    };

    videoElement.addEventListener('error', handleNetworkError);

    // ✅ MEILLEURE GESTION DES ÉTATS DE CHARGEMENT
    const handleCanPlay = () => {

      setIsLoading(false);
      setLoadInfo(null);
    };

    const handleCanPlayThrough = () => {

      setIsLoading(false);
      setLoadInfo(null);
      retryCountRef.current = 0; // Réinitialiser les retries
      retryDelayRef.current = 1000;
    };

    const handleWaiting = () => {

      setIsLoading(true);
    };

    const handlePlaying = () => {

      setIsPlaying(true);
      setIsLoading(false);
      setLoadInfo(null);
      
      // Vérification supplémentaire du codec après le début de lecture
      if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {

        if (!useTranscode) {

          setLoadInfo('🔄 Problème de codec - passage en transcodage...');
          setUseTranscode(true);
        }
      }
    };

    const handlePause = () => {

      setIsPlaying(false);
    };

    const handleStalled = () => {

      setIsLoading(true);
    };

    const handleSuspend = () => {

    };

    videoElement.addEventListener('canplay', handleCanPlay);
    videoElement.addEventListener('canplaythrough', handleCanPlayThrough);
    videoElement.addEventListener('waiting', handleWaiting);
    videoElement.addEventListener('playing', handlePlaying);
    videoElement.addEventListener('pause', handlePause);
    videoElement.addEventListener('stalled', handleStalled);
    videoElement.addEventListener('suspend', handleSuspend);

    // Tenter de lire automatiquement (une seule fois au montage)
    if (!hasAttemptedPlayRef.current) {
      hasAttemptedPlayRef.current = true;
      
      const playPromise = videoElement.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {

            setIsPlaying(true);
            detectAudioTracks(); // Détecter les pistes après le début de lecture
            detectSubtitles();
            
            // Vérification supplémentaire après 3 secondes de lecture
            setTimeout(() => {
              if (videoElement && (videoElement.videoWidth === 0 || videoElement.videoHeight === 0)) {

                if (!useTranscode && retryCountRef.current === 0) {

                  setLoadInfo('🔄 Problème vidéo détecté - activation transcodage...');
                  setUseTranscode(true);
                  retryCountRef.current = 1;
                }
              }
            }, 3000);
          })
          .catch((error) => {

            setIsLoading(false);
            // Le navigateur bloque l'autoplay, l'utilisateur devra cliquer
          });
      }
    }

    // Sauvegarder la progression toutes les 5 secondes
    const saveInterval = setInterval(() => {
      if (videoElement.currentTime > 0) {
        saveProgress(Math.floor(videoElement.currentTime));
      }
    }, 5000);

    // Détection et récupération automatique des blocages
    let lastTime = 0;
    let stalledCount = 0;
    let isBuffering = true; // Ignorer les premiers instants de buffering
    
    // ✅ Pour le transcodage, donner plus de temps avant de détecter un blocage
    // (le transcodage FFmpeg peut prendre 10-15s à démarrer)
    const stalledThreshold = useTranscode ? 15 : 5; // 30s pour transcodage, 10s pour direct
    
    const stalledCheckInterval = setInterval(() => {
      if (!videoElement.paused && !videoElement.ended) {
        // Attendre que la vidéo ait commencé à jouer avant de détecter les blocages
        if (videoElement.currentTime > 0) {
          isBuffering = false;
        }
        
        if (!isBuffering && videoElement.currentTime === lastTime) {
          stalledCount++;

          if (stalledCount >= stalledThreshold) {
            // Blocage confirmé après stalledThreshold vérifications

            setIsStalled(true);
            setStalledTime(stalledCount * 2);
            
            // Vérifier si c'est un problème de codec
            if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {

              if (!useTranscode) {

                setLoadInfo('🔄 Problème de codec détecté - activation transcodage...');
                setUseTranscode(true);
                stalledCount = 0;
                return;
              } else {
                setLoadError('❌ Erreur : Codec vidéo non supporté même avec le transcodage');
              }
            }
            
            // Forcer le rechargement du buffer avec micro-seek
            const currentPos = videoElement.currentTime;
            videoElement.currentTime = currentPos + 0.1;
            
            // Si toujours bloqué après 20 secondes, recharger
            if (stalledCount >= 10) {

              videoElement.load();
              setTimeout(() => {
                videoElement.currentTime = currentPos;
                videoElement.play().catch(() => {});
              }, 1000);
              stalledCount = 0;
            }
          }
        } else {
          // La vidéo progresse normalement - désactiver immédiatement le message
          if (stalledCount > 0 || isStalled) {

            stalledCount = 0;
            setIsStalled(false);
            setStalledTime(0);
          }
        }
        lastTime = videoElement.currentTime;
      } else {
        // Vidéo en pause ou terminée - désactiver le message stalled
        if (isStalled) {
          setIsStalled(false);
          setStalledTime(0);
        }
        stalledCount = 0;
      }
    }, 2000); // Vérifier toutes les 2 secondes

    stalledCheckRef.current = stalledCheckInterval;

    // ✅ LISTENERS PICTURE-IN-PICTURE
    const handleEnterPiP = () => {
      setIsPiP(true);

    };

    const handleLeavePiP = () => {
      setIsPiP(false);

    };

    videoElement.addEventListener('enterpictureinpicture', handleEnterPiP);
    videoElement.addEventListener('leavepictureinpicture', handleLeavePiP);

    return () => {
      clearInterval(saveInterval);
      clearInterval(stalledCheckInterval);
      videoElement.removeEventListener('loadedmetadata', handleLoadedMetadata);
      videoElement.removeEventListener('progress', updateBufferProgress);
      videoElement.removeEventListener('timeupdate', updateBufferProgress);
      videoElement.removeEventListener('error', handleNetworkError);
      videoElement.removeEventListener('canplay', handleCanPlay);
      videoElement.removeEventListener('canplaythrough', handleCanPlayThrough);
      videoElement.removeEventListener('waiting', handleWaiting);
      videoElement.removeEventListener('playing', handlePlaying);
      videoElement.removeEventListener('pause', handlePause);
      videoElement.removeEventListener('stalled', handleStalled);
      videoElement.removeEventListener('suspend', handleSuspend);
      videoElement.removeEventListener('enterpictureinpicture', handleEnterPiP);
      videoElement.removeEventListener('leavepictureinpicture', handleLeavePiP);
      
      // ✅ CLEANUP PiP : Sortir du mode PiP à la fermeture
      if (document.pictureInPictureElement) {
        document.exitPictureInPicture().catch(() => {});
      }
      
      // Sauvegarder une dernière fois à la fermeture
      if (videoElement.currentTime > 0) {
        saveProgress(Math.floor(videoElement.currentTime));
      }
    };
  }, [video.id, video.path, savedPosition, saveProgress, useTranscode, transcodeQuality]);  // Dépendances stabilisées

  const togglePlay = () => {
    const videoElement = videoRef.current;
    if (isPlaying) {
      videoElement.pause();
    } else {
      videoElement.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    const videoElement = videoRef.current;
    if (!videoElement) return;
    
    setCurrentTime(videoElement.currentTime);
    
    // Mettre à jour la durée si elle est valide
    if (!isNaN(videoElement.duration) && isFinite(videoElement.duration)) {
      setDuration(videoElement.duration);
    }
  };

  const handleSeek = (e) => {
    const videoElement = videoRef.current;
    if (!videoElement) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const newTime = pos * videoElement.duration;
    
    // Vérifier que la nouvelle position est valide
    if (!isNaN(newTime) && isFinite(newTime) && newTime >= 0) {
      videoElement.currentTime = newTime;
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    videoRef.current.volume = newVolume;
  };

  const toggleFullscreen = () => {
    const player = playerRef.current;
    if (!document.fullscreenElement) {
      player.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const skip = (seconds) => {
    const videoElement = videoRef.current;
    if (!videoElement) return;
    
    const newTime = videoElement.currentTime + seconds;
    
    // Vérifier que la nouvelle position est dans les limites
    if (!isNaN(newTime) && isFinite(newTime)) {
      if (newTime >= 0 && newTime <= videoElement.duration) {
        videoElement.currentTime = newTime;
      } else if (newTime < 0) {
        videoElement.currentTime = 0;
      } else if (newTime > videoElement.duration) {
        videoElement.currentTime = videoElement.duration;
      }
    }
  };

  const changeAudioTrack = (trackIndex) => {
    const videoElement = videoRef.current;
    const tracks = videoElement.audioTracks;
    
    if (tracks && tracks.length > 0) {
      // Désactiver toutes les pistes
      for (let i = 0; i < tracks.length; i++) {
        tracks[i].enabled = false;
      }
      // Activer la piste sélectionnée
      if (tracks[trackIndex]) {
        tracks[trackIndex].enabled = true;
        setCurrentAudioTrack(trackIndex);

      }
    }
    setShowSettingsMenu(false);
  };

  const changeSubtitleTrack = (trackIndex) => {
    const videoElement = videoRef.current;
    const tracks = videoElement.textTracks;
    
    if (tracks) {
      // Désactiver toutes les pistes
      for (let i = 0; i < tracks.length; i++) {
        tracks[i].mode = 'hidden';
      }
      // Activer la piste sélectionnée (-1 = désactivé)
      if (trackIndex >= 0 && tracks[trackIndex]) {
        tracks[trackIndex].mode = 'showing';
      }
      setCurrentSubtitleTrack(trackIndex);

    }
    setShowSettingsMenu(false);
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return "0:00";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    }
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const handleMouseMove = () => {
    setShowControls(true);
    clearTimeout(controlsTimeoutRef.current);
    controlsTimeoutRef.current = setTimeout(() => {
      setShowControls(false);
    }, 5000); // 5 secondes avant de masquer les contrôles
  };

  const handleKeyPress = (e) => {
    switch (e.key) {
      case " ":
      case "k":
        e.preventDefault();
        togglePlay();
        break;
      case "f":
        e.preventDefault();
        toggleFullscreen();
        break;
      case "ArrowLeft":
        e.preventDefault();
        skip(-10);
        break;
      case "ArrowRight":
        e.preventDefault();
        skip(10);
        break;
      case "j": // Saut arrière 10s (standard YouTube)
        e.preventDefault();
        skip(-10);
        break;
      case "l": // Saut avant 10s (standard YouTube)
        e.preventDefault();
        skip(10);
        break;
      case "ArrowUp":
        e.preventDefault();
        setVolume(Math.min(1, volume + 0.1));
        videoRef.current.volume = Math.min(1, volume + 0.1);
        break;
      case "ArrowDown":
        e.preventDefault();
        setVolume(Math.max(0, volume - 0.1));
        videoRef.current.volume = Math.max(0, volume - 0.1);
        break;
      case "m":
        e.preventDefault();
        setVolume(volume === 0 ? 1 : 0);
        videoRef.current.volume = volume === 0 ? 1 : 0;
        break;
      case "p": // Picture-in-Picture
        e.preventDefault();
        togglePiP();
        break;
      case "<": // Ralentir (Shift + ,)
        e.preventDefault();
        changePlaybackRate(-0.25);
        break;
      case ">": // Accélérer (Shift + .)
        e.preventDefault();
        changePlaybackRate(0.25);
        break;
      case "Escape":
        if (isPiP) {
          document.exitPictureInPicture();
        } else {
          onClose();
        }
        break;
    }
  };

  // Nouvelles fonctions pour PiP et vitesse
  const togglePiP = async () => {
    if (!document.pictureInPictureEnabled) {

      return;
    }

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        setIsPiP(false);
      } else if (videoRef.current) {
        await videoRef.current.requestPictureInPicture();
        setIsPiP(true);
      }
    } catch (err) {

    }
  };

  const changePlaybackRate = (delta) => {
    const newRate = Math.max(0.25, Math.min(2, playbackRate + delta));
    setPlaybackRate(newRate);
    if (videoRef.current) {
      videoRef.current.playbackRate = newRate;
    }

  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [isPlaying, volume]);

  // Gestion de la molette de la souris pour le volume
  const handleWheel = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const delta = e.deltaY > 0 ? -0.05 : 0.05; // Molette vers le bas = volume -, vers le haut = volume +
    const newVolume = Math.max(0, Math.min(1, volume + delta));
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  useEffect(() => {
    const playerElement = playerRef.current;
    if (playerElement) {
      // Empêcher le scroll de la page en arrière-plan
      playerElement.addEventListener('wheel', handleWheel, { passive: false });
      return () => {
        playerElement.removeEventListener('wheel', handleWheel);
      };
    }
  }, [volume]);

  // NOUVEAU : Activer manuellement les sous-titres quand une piste est sélectionnée
  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    // Attendre que la vidéo soit chargée
    const activateSubtitles = () => {
      const textTracks = videoElement.textTracks;

      if (textTracks.length > 0) {
        // Afficher toutes les pistes détectées
        for (let i = 0; i < textTracks.length; i++) {
          const track = textTracks[i];

          // Activer la première piste (celle ajoutée via <track default>)
          if (i === 0) {
            track.mode = 'showing';

          } else {
            track.mode = 'hidden';
          }
        }
      } else {

      }
    };

    // Essayer immédiatement
    activateSubtitles();

    // Et aussi après loadedmetadata au cas où
    videoElement.addEventListener('loadedmetadata', activateSubtitles);

    return () => {
      videoElement.removeEventListener('loadedmetadata', activateSubtitles);
    };
  }, [selectedSubtitleTrack, useTranscode]);

  // Fermer le menu paramètres si clic en dehors
  useEffect(() => {
    if (!showSettingsMenu) return;
    function handleClickOutside(event) {
      const menu = document.querySelector('.settings-menu-youtube');
      if (menu && !menu.contains(event.target)) {
        setShowSettingsMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSettingsMenu]);

  return (
    <div
      ref={playerRef}
      className={`video-player-overlay ${showControls ? 'show-cursor' : ''}`}
      onMouseMove={handleMouseMove}
      onClick={togglePlay}
    >
      <video
        key={`video-${useTranscode ? 'transcode' : 'direct'}-audio${selectedAudioTrack}-sub${selectedSubtitleTrack}`}
        ref={videoRef}
        className="video-player-element"
        src={videoUrl}
        preload="auto"
        playsInline
        crossOrigin="anonymous"
        // ✅ PERFORMANCE : Activer l'accélération matérielle
        style={{
          willChange: 'transform',
          transform: 'translateZ(0)',
        }}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        onClick={(e) => {
          e.stopPropagation();
          togglePlay();
        }}
        onDoubleClick={(e) => {
          e.stopPropagation();
          toggleFullscreen(); // Double-clic = plein écran (standard YouTube/Netflix)
        }}
        onLoadedMetadata={() => {

          // Métadonnées chargées mais pas encore prêt à jouer
        }}
        onLoadStart={() => {

          setIsLoading(true);
        }}
        onProgress={() => {
          // Le navigateur est en train de télécharger les données
          const video = videoRef.current;
          if (video && video.buffered.length > 0) {
            const bufferedEnd = video.buffered.end(video.buffered.length - 1);
            const duration = video.duration;
            if (duration > 0) {
              const percentBuffered = (bufferedEnd / duration) * 100;
              setBufferProgress(Math.round(percentBuffered));
              
              // Log détaillé seulement tous les 5%
              if (Math.round(percentBuffered) % 5 === 0) {

              }
              
              // Auto-play quand on a au moins 3% de buffer (environ 10-30s selon la vidéo)
              if (percentBuffered >= 3 && isLoading && !video.paused) {

                setIsLoading(false);
                setLoadInfo(null);
              }
            }
          }
        }}
        onWaiting={() => {
          // N'afficher le message de buffering que si la vidéo a déjà commencé
          if (videoRef.current && videoRef.current.currentTime > 0) {

            setLoadInfo('⏸️ Buffering...');
          }
        }}
        onStalled={() => {
          // Ne déclencher l'alerte que si la vidéo a déjà commencé
          if (videoRef.current && videoRef.current.currentTime > 0) {

            setIsStalled(true);
          }
        }}
        onSuspend={() => {

          // C'est normal, le navigateur suspend le téléchargement quand il a assez de buffer
        }}
        onCanPlay={() => {

          setIsLoading(false);
          setLoadError(null);
          setLoadInfo(null);  // Masquer immédiatement les messages
          setIsStalled(false);
          setIsPlaying(true); // Indiquer que la lecture est prête
          if (loadingTimeoutRef.current) {
            clearTimeout(loadingTimeoutRef.current);
          }
        }}
        onCanPlayThrough={() => {

          setIsLoading(false);
          setLoadInfo(null);  // Masquer tous les messages
          setLoadError(null);
        }}
        onError={(e) => {

          setIsLoading(false);
          
          const errorCode = e.target.error?.code;
          let errorMessage = '';
          
          switch(errorCode) {
            case 1: // MEDIA_ERR_ABORTED
              errorMessage = '❌ Chargement annulé';
              // Tentative de rechargement automatique (max 2 fois)
              if (retryCount < 2) {

                setRetryCount(retryCount + 1);
                setTimeout(() => {
                  if (videoRef.current) {
                    videoRef.current.load();
                    videoRef.current.play().catch(() => {});
                  }
                }, 1000);
                setLoadInfo('🔄 Rechargement automatique...');
                return;
              } else {
                errorMessage = '❌ Chargement échoué après plusieurs tentatives - Réessayez manuellement';
              }
              break;
            case 2: // MEDIA_ERR_NETWORK
              errorMessage = '🌐 Erreur réseau - Vérifiez votre connexion';
              // Tentative de rechargement automatique
              if (retryCountRef.current < 2) {

                retryCountRef.current = retryCountRef.current + 1;
                setTimeout(() => {
                  if (videoRef.current) {
                    videoRef.current.load();
                    videoRef.current.play().catch(() => {});
                  }
                }, 2000);
                setLoadInfo('🔄 Reconnexion en cours...');
                return;
              }
              break;
            case 3: // MEDIA_ERR_DECODE
              // Erreur de décodage - basculer automatiquement vers le transcodage
              if (!useTranscode) {

                setLoadInfo('🔄 Format non supporté - Activation du transcodage FFmpeg...');
                setUseTranscode(true); // Basculer vers transcodage
                retryCountRef.current = 0; // Réinitialiser le compteur
                return; // Ne pas afficher d'erreur, juste basculer
              } else {
                errorMessage = '❌ Impossible de décoder la vidéo même avec transcodage';
              }
              break;
            case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
              // Format non supporté - essayer le transcodage
              if (!useTranscode) {

                setLoadInfo('🔄 Format non compatible - Activation du transcodage FFmpeg...');
                setUseTranscode(true); // Basculer vers transcodage
                retryCountRef.current = 0; // Réinitialiser le compteur
                return; // Ne pas afficher d'erreur, juste basculer
              } else {
                errorMessage = '📹 Format vidéo non supporté même avec transcodage - Vérifiez le fichier';
              }
              break;
            default:
              errorMessage = `❌ Erreur inconnue (${errorCode}) - Impossible de charger la vidéo`;
          }
          
          setLoadError(errorMessage);
        }}
        onPlaying={() => {

          setIsLoading(false);
          setIsStalled(false);
          setLoadInfo(null); // Masquer tous les messages de chargement/buffering
        }}
      >
        {/* Charger les sous-titres via <track> si sélectionné */}
        {useTranscode && selectedSubtitleTrack >= 0 && (
          <track
            kind="subtitles"
            src={`${baseUrl}/api/stream/subtitle?path=${encodeURIComponent(video.path)}&subtitle_track=${selectedSubtitleTrack}`}
            srcLang={availableTracks?.subtitles?.find(t => t.index === selectedSubtitleTrack)?.language || 'fr'}
            label={availableTracks?.subtitles?.find(t => t.index === selectedSubtitleTrack)?.title || 'Sous-titres'}
            default
            onLoad={(e) => {

              // Vérifier que la piste est bien en mode "showing"
              const track = e.target.track;
              if (track && track.mode !== 'showing') {

                track.mode = 'showing';
              }
            }}
            onError={(e) => {

            }}
          />
        )}
      </video>

      {/* Indicateur de chargement avec progression */}
      {isLoading && !loadError && !loadInfo && (
        <div className="video-loading">
          <div className="spinner"></div>
          <p>Chargement de la vidéo...</p>
          {bufferProgress > 0 && (
            <div className="buffer-progress">
              <div className="buffer-bar" style={{ width: `${bufferProgress}%` }}></div>
              <span className="buffer-text">{bufferProgress}% buffered</span>
            </div>
          )}
        </div>
      )}

      {/* Message d'information (vidéo volumineuse) */}
      {loadInfo && (
        <div className="video-info">
          <div className="spinner"></div>
          <p>{loadInfo}</p>
          {bufferProgress > 0 && (
            <div className="buffer-progress">
              <div className="buffer-bar" style={{ width: `${bufferProgress}%` }}></div>
              <span className="buffer-text">{bufferProgress}% buffered</span>
            </div>
          )}
        </div>
      )}

      {/* Indicateur de vidéo bloquée (stalled) - DÉSACTIVÉ */}
      {/* {isStalled && !loadError && (
        <div className="video-stalled">
          <div className="spinner"></div>
          <p>🔄 Récupération en cours...</p>
          <p style={{ fontSize: '14px', opacity: 0.7, marginTop: '10px' }}>
            La vidéo semble bloquée, tentative de déblocage automatique...
          </p>
        </div>
      )} */}

      {/* Message d'erreur */}
      {loadError && (
        <div className="video-error">
          <h2>❌ Erreur</h2>
          <p>{loadError}</p>
          <button onClick={onClose} className="error-close-btn">Fermer</button>
        </div>
      )}

      {/* Bouton play central quand en pause */}
      {!isPlaying && (
        <div className="center-play-button" onClick={togglePlay}>
          <button className="big-play-btn" aria-label="Lecture">
            <svg viewBox="0 0 92 92" width="54" height="54" fill="none">
              <circle cx="46" cy="46" r="40" fill="rgba(255,107,53,0.22)" />
              <polygon points="38,30 38,62 64,46" fill="#fff" style={{filter:'drop-shadow(0 2px 8px rgba(255,107,53,0.25))'}} />
            </svg>
          </button>
        </div>
      )}

      {/* Contrôles */}
      <div className={`video-controls ${showControls ? "visible" : ""}`}>
        {/* Barre de progression */}
        <div className="progress-container" onClick={handleSeek}>
          <div className="progress-bar">
            <div
              className="progress-filled"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
        </div>

        {/* Ligne unique de contrôle - Style Premium */}
        <div className="controls-bottom-bar">
          {/* Gauche : Lecture et volume */}
          <div className="controls-group controls-left">
            <button
              className="control-btn-minimal play-btn"
              onClick={(e) => {
                e.stopPropagation();
                togglePlay();
              }}
              title={isPlaying ? "Pause (Espace)" : "Lecture (Espace)"}
            >
              {isPlaying ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" rx="1"/>
                  <rect x="14" y="4" width="4" height="16" rx="1"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              )}
            </button>

            <button
              className="control-btn-minimal skip-btn"
              onClick={(e) => {
                e.stopPropagation();
                skip(-10);
              }}
              title="Reculer de 10s (←)"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.99 5V1l-5 5 5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6h-2c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
                <text x="12" y="15" fontSize="7" textAnchor="middle" fill="currentColor" fontWeight="bold">10</text>
              </svg>
            </button>

            <button
              className="control-btn-minimal skip-btn"
              onClick={(e) => {
                e.stopPropagation();
                skip(10);
              }}
              title="Avancer de 10s (→)"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/>
                <text x="12" y="15" fontSize="7" textAnchor="middle" fill="currentColor" fontWeight="bold">10</text>
              </svg>
            </button>

            <div className="volume-group" onClick={(e) => e.stopPropagation()}>
              <button
                className="control-btn-minimal volume-btn"
                onClick={() => {
                  const newVol = volume === 0 ? 1 : 0;
                  setVolume(newVol);
                  videoRef.current.volume = newVol;
                }}
                title={volume === 0 ? "Réactiver le son (M)" : "Couper le son (M)"}
              >
                {volume === 0 ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                  </svg>
                ) : volume < 0.5 ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 9v6h4l5 5V4l-5 5H7z"/>
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
                  </svg>
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={volume}
                onChange={handleVolumeChange}
                className="volume-slider-minimal"
              />
            </div>

            <div className="time-display-minimal">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          {/* Droite : Paramètres, Plein écran, Fermer */}
          <div className="controls-group controls-right">
            {/* Menu Paramètres (Audio & Sous-titres) - Style YouTube */}
            <div className="settings-menu-container">
              <button
                className="control-btn-minimal settings-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSettingsMenu(!showSettingsMenu);
                }}
                title="Paramètres"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
                </svg>
              </button>
              
              {showSettingsMenu && (
                <div className="settings-menu-youtube" onClick={(e) => e.stopPropagation()}>
                  <div className="settings-flex-row">
                    {/* PISTES AUDIO */}
                    {availableTracks && availableTracks.audio.length > 0 && (
                      <div className="settings-section">
                        <div className="settings-section-header" style={{color: '#ff6b35'}}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                          </svg>
                          Piste audio
                        </div>
                        {availableTracks.audio.map((track) => (
                          <button
                            key={`source-audio-${track.index}`}
                            className={`settings-item ${selectedAudioTrack === track.index ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedAudioTrack(track.index);

                            }}
                          >
                            <span className="item-label">{track.title || `Audio ${track.index}`}</span>
                            {track.language !== 'unknown' && (
                              <span className="item-badge">{track.language.toUpperCase()}</span>
                            )}
                            <span className="item-info">{track.channels} canaux</span>
                            {selectedAudioTrack === track.index && (
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="check-mark">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                              </svg>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    {/* SOUS-TITRES */}
                    {availableTracks && availableTracks.subtitles.length > 0 && (
                      <div className="settings-section">
                        <div className="settings-section-header" style={{color: '#4CAF50'}}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM4 12h4v2H4v-2zm10 6H4v-2h10v2zm6 0h-4v-2h4v2zm0-4H10v-2h10v2z"/>
                          </svg>
                          Sous-titres
                        </div>
                        <button
                          className={`settings-item ${selectedSubtitleTrack === -1 ? 'active' : ''}`}
                          onClick={() => {
                            setSelectedSubtitleTrack(-1);

                          }}
                        >
                          <span className="item-label">Désactivé</span>
                          {selectedSubtitleTrack === -1 && (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="check-mark">
                              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                          )}
                        </button>
                        {availableTracks.subtitles.map((track) => (
                          <button
                            key={`source-subtitle-${track.index}`}
                            className={`settings-item ${selectedSubtitleTrack === track.index ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedSubtitleTrack(track.index);

                            }}
                          >
                            <span className="item-label">{track.title || `Sous-titre ${track.index}`}</span>
                            {track.language !== 'unknown' && (
                              <span className="item-badge">{track.language.toUpperCase()}</span>
                            )}
                            {selectedSubtitleTrack === track.index && (
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="check-mark">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                              </svg>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    {/* MODE DE LECTURE */}
                    <div className="settings-section">
                      <div className="settings-section-header">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                        Mode de lecture
                      </div>
                      <button
                        className={`settings-item ${!useTranscode ? 'active' : ''}`}
                        onClick={() => {
                          if (useTranscode) {

                            setUseTranscode(false);
                            setShowSettingsMenu(false);
                          }
                        }}
                      >
                        <span className="item-label">Streaming direct</span>
                        <span className="item-info">Qualité originale</span>
                        {!useTranscode && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="check-mark">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                          </svg>
                        )}
                      </button>
                      <button
                        className={`settings-item ${useTranscode ? 'active' : ''}`}
                        onClick={() => {
                          if (!useTranscode) {

                            setLoadInfo('🔄 Activation du transcodage...');
                            setUseTranscode(true);
                            retryCountRef.current = 0;
                            setShowSettingsMenu(false);
                          }
                        }}
                      >
                        <span className="item-label">Transcodage FFmpeg</span>
                        <span className="item-info" style={{color: '#ffa500'}}>Utiliser si problème vidéo</span>
                        {useTranscode && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="check-mark">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  {/* ...le reste du menu paramètres... */}
                </div>
              )}
            </div>

            {/* Bouton Picture-in-Picture */}
            {document.pictureInPictureEnabled && (
              <button
                className="control-btn-minimal pip-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  togglePiP();
                }}
                title={isPiP ? "Quitter PiP" : "Picture-in-Picture (P)"}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  {isPiP ? (
                    <path d="M19 7h-8v6h8V7zm2-4H3c-1.1 0-2 .9-2 2v14c0 1.1.9 1.98 2 1.98h18c1.1 0 2-.88 2-1.98V5c0-1.1-.9-2-2-2zm0 16.01H3V4.98h18v14.03z"/>
                  ) : (
                    <path d="M19 11h-8v6h8v-6zm4-6v14c0 1.1-.9 2-2 2H3c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2h18c1.1 0 2 .9 2 2zm-2 0H3v14h18V5z"/>
                  )}
                </svg>
              </button>
            )}

            <button
              className="control-btn-minimal fullscreen-btn"
              onClick={(e) => {
                e.stopPropagation();
                toggleFullscreen();
              }}
              title={isFullscreen ? "Quitter le plein écran (F)" : "Plein écran (F)"}
            >
              {isFullscreen ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                </svg>
              )}
            </button>

            {/* Bouton Fermer */}
            <button
              className="control-btn-minimal close-btn"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              title="Fermer (Echap)"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Titre de la vidéo */}
      <div className={`video-title ${showControls ? "visible" : ""}`}>
        <h2>{video.title}</h2>
      </div>
    </div>
  );
}

