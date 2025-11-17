import { useEffect, useState, useRef, Suspense, lazy, useMemo, useCallback, useLayoutEffect } from "react";
import CategoryRow from "./CategoryRow.jsx";
import NetworkInfo from "./NetworkInfo.jsx";
import DomainDetector, { useDomainName } from "./DomainDetector.jsx";
import ProfileSelector from "./ProfileSelector.jsx";

// ✅ OPTIMISATION: Lazy loading pour tous les composants non-critiques
const SettingsModal = lazy(() => import("./SettingsModal.jsx"));
const VideoListModal = lazy(() => import("./VideoListModal.jsx"));
const Carousel = lazy(() => import("./Carousel.jsx"));
const VideoDetail = lazy(() => import("./VideoDetail.jsx"));
const AllVideosGrid = lazy(() => import("./AllVideosGrid.jsx"));
const YearGrid = lazy(() => import("./YearGrid.jsx"));
const GenreGrid = lazy(() => import("./GenreGrid.jsx"));
const CollectionsView = lazy(() => import("./CollectionsView.jsx"));
const VideoListGrid = lazy(() => import("./VideoListGrid.jsx"));
const WebGLBackground = lazy(() => import("./WebGLBackground.jsx"));
const SearchSuggestions = lazy(() => import("./components/SearchSuggestions.jsx"));

import { fetchCategories, getRandomVideo, deleteVideo, getApiUrl } from "./config.js";
import { useI18n } from "./i18n.jsx";
import { AnimatePresence } from "framer-motion";
import { useGlobalShortcuts } from "./hooks/useKeyboard.js";
import "./header.css";
import "./footer.css";

// Helper pour obtenir l'URL correcte de l'avatar
function getAvatarUrl(avatar) {
  if (avatar.startsWith("custom_avatars/")) {
    return getApiUrl(`/api/${avatar}`);
  }
  return `/avatars/${avatar}`;
}

export default function App() {
  const { t } = useI18n();
  const { domainName } = useDomainName(); // Détection du nom de domaine
  
  // Mettre à jour le titre de la page avec le nom de domaine
  useEffect(() => {
    document.title = domainName;
  }, [domainName]);
  
  // États de profil
  const [currentProfile, setCurrentProfile] = useState(null);
  
  // ✅ DÉSACTIVÉ : Chargement automatique du profil
  // L'écran de sélection de profil s'affiche toujours au démarrage
  // useEffect(() => {
  //   const loadMainProfile = async () => {
  //     try {
  //       const response = await fetch("http://127.0.0.1:8000/api/profiles");
  //       const data = await response.json();
  //       
  //       if (data.ok && data.profiles.length > 0) {
  //         // Trouver le profil principal (is_main = true)
  //         const mainProfile = data.profiles.find(p => p.is_main);
  //         if (mainProfile) {
  //           console.log("✅ Profil principal chargé automatiquement:", mainProfile.name);
  //           setCurrentProfile(mainProfile);
  //         } else {
  //           // Si aucun profil principal, utiliser le premier
  //           console.log("⚠️ Aucun profil principal, utilisation du premier profil");
  //           setCurrentProfile(data.profiles[0]);
  //         }
  //       }
  //     } catch (error) {
  //       console.error("❌ Erreur chargement profil principal:", error);
  //     }
  //   };
  //   
  //   loadMainProfile();
  // }, []);
  
  // États principaux
  const [categories, setCategories] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  
  // États de filtrage
  const [mode, setMode] = useState("mixed");
  const [filter, setFilter] = useState("all");
  
  // État de recherche
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchModal, setShowSearchModal] = useState(false);
  
  // États UI
  const [loading, setLoading] = useState(false);
  const [cacheKey, setCacheKey] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showModeMenu, setShowModeMenu] = useState(false);
  
  // États de navigation
  const [currentView, setCurrentView] = useState("main");
  const [navigationHistory, setNavigationHistory] = useState(["main"]);
  
  // Sauvegarde de la position de scroll
  const scrollPositionRef = useRef(0);

  // Gestion du bouton retour du navigateur/mobile
  useEffect(() => {
    const handlePopState = (e) => {
      e.preventDefault();
      
      // Si on est sur une vidéo, fermer la vidéo
      if (selectedVideo) {
        handleCloseVideo();
        return;
      }
      
      // Si on a un historique de navigation
      if (navigationHistory.length > 1) {
        const newHistory = [...navigationHistory];
        newHistory.pop(); // Retirer la vue actuelle
        const previousView = newHistory[newHistory.length - 1];
        
        setNavigationHistory(newHistory);
        setCurrentView(previousView);
        
        // Réinitialiser les états de recherche si on revient à main
        if (previousView === "main") {
          setSearchQuery("");
          setSearchResults([]);
        }
      } else {
        // Si plus d'historique, revenir à main
        setCurrentView("main");
        setSearchQuery("");
        setSearchResults([]);
      }
    };

    window.addEventListener("popstate", handlePopState);
    
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [selectedVideo, navigationHistory]);

  // Fermer le menu mode quand on clique à l'extérieur
  useEffect(() => {
    if (!showModeMenu) return;
    
    const handleClickOutside = (e) => {
      const modeMenuButton = e.target.closest('.mode-menu-button');
      const modeMenuContent = e.target.closest('.mode-menu-content');
      
      if (!modeMenuButton && !modeMenuContent) {
        setShowModeMenu(false);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showModeMenu]);

  // ✅ Raccourcis clavier globaux
  useGlobalShortcuts({
    onSearch: () => setShowSearchModal(true),
    onSettings: () => setShowSettings(true),
    enabled: currentProfile !== null
  });

  // Gestionnaire de suppression de vidéo
  const handleDeleteVideo = useCallback(async (video) => {
    try {
      const profileId = currentProfile?.id || null;
      await deleteVideo(video.id, true, profileId); // Passe l'ID du profil
      // Recharger les catégories pour mettre à jour l'affichage
      await load(mode);
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      alert("Impossible de supprimer la vidéo");
    }
  }, [mode, currentProfile]);
  
  // Gestionnaire de mise à jour du cache (pour forcer le rechargement des miniatures)
  const handleUpdateCache = useCallback(async () => {
    // Forcer uniquement le rechargement des images sans recharger les catégories
    // Cela préserve l'ordre actuel des films dans le carousel
    setCacheKey(Date.now());
  }, []);

  // Gestionnaires d'événements optimisés
  const handleCloseVideo = useCallback(() => {
    setSelectedVideo(null);
    
    // Recharger les catégories pour mettre à jour la liste "À reprendre"
    // Uniquement si un profil est sélectionné
    if (currentProfile) {
      load(mode).then(() => {
        // Forcer le rechargement des images du carousel
        setCacheKey(Date.now());
        
        // Restaurer la position de scroll après un court délai
        setTimeout(() => {
          window.scrollTo({
            top: scrollPositionRef.current,
            behavior: 'smooth'
          });
        }, 100);
      });
    } else {
      // Si pas de profil, juste fermer la vidéo
      setCacheKey(Date.now());
    }
  }, [mode, currentProfile]);
  
  // Fonction pour sélectionner une vidéo (sauvegarde la position de scroll)
  const handleSelectVideo = useCallback((video) => {
    // Sauvegarder la position de scroll actuelle
    scrollPositionRef.current = window.scrollY || window.pageYOffset;
    
    // Ajouter un état à l'historique du navigateur pour la vidéo
    window.history.pushState({ video: video.id }, "", "");
    
    setSelectedVideo(video);
  }, []);

  const handleNavigate = useCallback((view) => {
    // Ajouter la nouvelle vue à l'historique
    setNavigationHistory(prev => [...prev, view]);
    
    // Ajouter un état à l'historique du navigateur
    window.history.pushState({ view }, "", "");
    
    setCurrentView(view);
    setSelectedVideo(null);
    if (view !== "main") {
      setSearchQuery("");
      setSearchResults([]);
    }
  }, []);

  const handleRandomVideo = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const video = await getRandomVideo(mode);
      setRandomVideo(video);
      handleNavigate("random");
    } catch (error) {
      console.error("Erreur lors du chargement de la vidéo aléatoire:", error);
      setError(error.message || "Impossible de charger une vidéo aléatoire");
    } finally {
      setLoading(false);
    }
  }, [handleNavigate, mode]);

  // Fonction de recherche
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    
    if (!query.trim() || !categories) {
      setSearchResults([]);
      return;
    }
    
    const searchLower = query.toLowerCase();
    const allVideos = [];
    
    // Collecter toutes les vidéos
    if (categories.carousel) allVideos.push(...categories.carousel);
    if (categories.to_resume) allVideos.push(...categories.to_resume);
    if (categories.watched) allVideos.push(...categories.watched);
    
    Object.values(categories.by_year || {}).forEach(videos => {
      allVideos.push(...videos);
    });
    
    Object.values(categories.by_genre || {}).forEach(videos => {
      allVideos.push(...videos);
    });
    
    // Dédupliquer par ID
    const uniqueVideos = Array.from(
      new Map(allVideos.map(v => [v.id, v])).values()
    );
    
    // Rechercher dans le titre
    const results = uniqueVideos.filter(video =>
      video.title?.toLowerCase().includes(searchLower)
    );
    
    setSearchResults(results);
  }, [categories]);
  
  // États des vues spécifiques - regroupés pour plus de clarté
  const viewStates = useMemo(() => ({
    all: currentView === "all",
    year: currentView === "year",
    genre: currentView === "genre",
    collections: currentView === "collections",
    watched: currentView === "watched",
    resume: currentView === "resume",
    random: currentView === "random",
    settings: currentView === "settings",
  }), [currentView]);

  // État vidéo aléatoire
  const [randomVideo, setRandomVideo] = useState(null);
  const watchedSectionRef = useRef(null);

  const MODES = [
    { value: "mixed", label: t("modes.mixed") },
    { value: "films", label: t("modes.films") },
    { value: "series", label: t("modes.series") },
  ];

  const FILTERS = [
    { value: "all", label: t("nav.all") },
    { value: "watched", label: t("nav.watched") },
    { value: "to_resume", label: t("nav.to_resume") },
    { value: "collections", label: "Collections" },
    { value: "by_year", label: t("nav.by_year") },
    { value: "by_genre", label: t("nav.by_genre") },
    { value: "random", label: t("nav.random") },
  ];

  const [error, setError] = useState(null);

  async function load(modeArg = mode) {
    setLoading(true);
    setError(null);
    try {
      const profileId = currentProfile?.id || null;
      console.log(`📥 Chargement catégories (mode=${modeArg}, profile=${profileId})`);
      const response = await fetchCategories(modeArg, profileId);
      console.log(`📦 Réponse reçue:`, {
        carousel: response?.carousel?.length || 0,
        to_resume: response?.to_resume?.length || 0,
        watched: response?.watched?.length || 0
      });
      if (!response || !response.carousel) {
        throw new Error("Format de données invalide");
      }
      setCategories(response);
    } catch (e) {
      console.error("Erreur détaillée:", e);
      
      // Message d'erreur spécifique pour les connexions réseau
      let errorMessage = e.message;
      if (e.message.includes("Failed to fetch") || e.message.includes("NetworkError")) {
        const isRemote = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        if (isRemote) {
          errorMessage = `❌ Impossible de se connecter au serveur (${window.location.hostname}:8000)\n\n` +
                        `Vérifiez que:\n` +
                        `• Le serveur est démarré sur ${window.location.hostname}\n` +
                        `• Le port 8000 est autorisé dans le pare-feu Windows\n` +
                        `• Vous êtes sur le même réseau Wi-Fi/LAN\n\n` +
                        `💡 Sur le serveur, exécutez: .\\configure-firewall.ps1`;
        } else {
          errorMessage = "❌ Serveur non accessible. Assurez-vous qu'il est démarré (port 8000)";
        }
      }
      
      setError(errorMessage);
      setCategories(null);
    } finally {
      setLoading(false);
    }
  }

  async function playRandom(autoPlay = false) {
    try {
      const video = await getRandomVideo(mode);
      setRandomVideo(video);
      handleNavigate("random");
      if (autoPlay) {
        // Ouvrir automatiquement le lecteur intégré
        setTimeout(() => setSelectedVideo(video), 100);
      }
    } catch (e) {
      alert(t("errors.no_video_mode"));
      console.error(e);
    }
  }

  async function resumeLastVideo(autoPlay = true) {
    try {
      if (!categories || !categories.to_resume || categories.to_resume.length === 0) {
        alert(t("errors.no_resume"));
        return;
      }
      const video = categories.to_resume[0];
      if (autoPlay) {
        setSelectedVideo(video);
      } else {
  handleNavigate("resume");
      }
    } catch (e) {
      alert(t("errors.cannot_resume"));
      console.error(e);
    }
  }

  function handleFilterClick(filterValue) {
    switch (filterValue) {
      case "all":
        handleNavigate("all");
        break;
      case "watched":
        handleNavigate("watched");
        break;
      case "to_resume":
        handleNavigate("resume");
        break;
      case "collections":
        handleNavigate("collections");
        break;
      case "by_year":
        handleNavigate("year");
        break;
      case "by_genre":
        handleNavigate("genre");
        break;
      case "random":
        handleRandomVideo();
        break;
      default:
        setFilter(filterValue);
    }
  }

  // Détection mobile et ajout de classe CSS
  useLayoutEffect(() => {
    const checkMobile = () => {
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
        || window.innerWidth <= 768;
      
      if (isMobile) {
        document.documentElement.classList.add('is-mobile');
        document.body.classList.add('is-mobile');
      } else {
        document.documentElement.classList.remove('is-mobile');
        document.body.classList.remove('is-mobile');
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Bloquer le scroll de la page principale quand une vue secondaire est active
  // useLayoutEffect s'exécute AVANT le paint, évitant le flash visuel
  useLayoutEffect(() => {
    const isSecondaryViewActive = 
      selectedVideo || 
      currentView !== "main" || 
      !currentProfile;
    
    if (isSecondaryViewActive) {
      // Scroll instantané en haut AVANT tout le reste
      window.scrollTo(0, 0);
      
      // Calculer la largeur de la scrollbar avant de la cacher
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      
      // Appliquer toutes les modifications en une seule fois (évite reflow)
      document.documentElement.style.overflow = "hidden";
      document.body.style.overflow = "hidden";
      
      // Compenser la disparition de la scrollbar pour éviter le décalage
      if (scrollbarWidth > 0) {
        document.body.style.paddingRight = `${scrollbarWidth}px`;
        
        // Compenser aussi le header et tous les éléments en position fixed/sticky
        const header = document.querySelector('.netflix-header');
        if (header) {
          header.style.paddingRight = `calc(2% + ${scrollbarWidth}px)`;
        }
      }
    } else {
      document.documentElement.style.overflow = "";
      document.body.style.overflow = "";
      document.body.style.paddingRight = "";
      
      // Retirer la compensation du header
      const header = document.querySelector('.netflix-header');
      if (header) {
        header.style.paddingRight = "";
      }
    }
    
    return () => {
      document.documentElement.style.overflow = "";
      document.body.style.overflow = "";
      document.body.style.paddingRight = "";
      
      const header = document.querySelector('.netflix-header');
      if (header) {
        header.style.paddingRight = "";
      }
    };
  }, [selectedVideo, currentView, currentProfile]);

  useEffect(() => {
    // Ne charger que si un profil est sélectionné
    if (currentProfile) {
      load(mode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, currentProfile]); // Ajouter currentProfile pour recharger quand le profil change

  // Rotation automatique du carousel toutes les 10 minutes
  useEffect(() => {
    const rotationInterval = setInterval(() => {
      load(mode);
      setCacheKey(Date.now());
    }, 600000); // 10 minutes = 600000 ms

    return () => clearInterval(rotationInterval);
  }, [mode]);

  const renderCategories = () => {
    if (loading) {
      return <div className="loading">Chargement en cours...</div>;
    }

    if (error) {
      return (
        <div className="error-message">
          <h2>Erreur de chargement</h2>
          <p>{error}</p>
          <button onClick={() => load(mode)}>Réessayer</button>
        </div>
      );
    }

    if (!categories) return null;

    // Rotation horaire : mélanger les catégories selon l'heure actuelle
    const getRotatedCategories = (categoriesObj, count = 3) => {
      if (!categoriesObj) return [];
      const entries = Object.entries(categoriesObj);
      if (entries.length === 0) return [];
      
      // Utiliser l'heure actuelle comme seed pour la rotation
      const currentHour = new Date().getHours();
      const rotationIndex = currentHour % entries.length;
      
      // Faire tourner le tableau et prendre les premiers éléments
      const rotated = [...entries.slice(rotationIndex), ...entries.slice(0, rotationIndex)];
      return rotated.slice(0, count);
    };

    const rotatedYears = getRotatedCategories(categories.by_year, 3);
    const rotatedGenres = getRotatedCategories(categories.by_genre, 3);

    // Vue par défaut : tout afficher
    return (
      <>
        {/* Afficher "Reprendre la lecture" seulement s'il y a des vidéos */}
        {categories.to_resume && categories.to_resume.length > 0 && (
          <CategoryRow
            title={t("categories.resume")}
            videos={categories.to_resume}
            onSelect={handleSelectVideo}
            cacheKey={cacheKey}
            onDelete={handleDeleteVideo}
          />
        )}
        <div ref={watchedSectionRef}>
          {categories.watched && categories.watched.length > 0 && (
            <CategoryRow
              title={t("categories.watched")}
              videos={categories.watched}
              onSelect={handleSelectVideo}
              cacheKey={cacheKey}
              onDelete={handleDeleteVideo}
            />
          )}
        </div>
        {rotatedYears.map(([year, videos]) => (
          <CategoryRow
            key={year}
            title={`${t("categories.films_of")} ${year}`}
            videos={videos}
            onSelect={handleSelectVideo}
            cacheKey={cacheKey}
            onDelete={handleDeleteVideo}
          />
        ))}
        {rotatedGenres.map(([genre, videos]) => (
          <CategoryRow
            key={genre}
            title={genre.charAt(0).toUpperCase() + genre.slice(1)}
            videos={videos}
            onSelect={handleSelectVideo}
            cacheKey={cacheKey}
            onDelete={handleDeleteVideo}
          />
        ))}
      </>
    );
  };

  return (
    <div className="app">
      <WebGLBackground />
      
      <div className="content">
        {/* Bande supérieure avec logo */}
        <div className="top-banner">
          <h1
            className="logo-banner"
            data-text={"HOMEONE"}
          >
            {"HOMEONE"}
          </h1>
        </div>
        
        <header className="netflix-header">
          <div className="header-left">
            {/* Bouton hamburger pour mobile */}
            <button 
              className="mobile-menu-button"
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              aria-label="Menu"
            >
              ☰
            </button>
            
            {/* Navigation normale (masquée sur mobile) */}
            <nav className="header-nav desktop-nav" role="navigation">
              {FILTERS.map((f) => (
                <button
                  key={f.value}
                  className="nav-item"
                  onClick={() => handleFilterClick(f.value)}
                  role="menuitem"
                >
                  {f.label}
                </button>
              ))}
            </nav>
            
            {/* Menu déroulant mobile */}
            {showMobileMenu && (
              <div className="mobile-menu-dropdown">
                <div className="mobile-menu-overlay" onClick={() => setShowMobileMenu(false)} />
                <nav className="mobile-menu-content">
                  <div className="mobile-menu-header">
                    <span className="mobile-menu-title">MENU</span>
                    <button 
                      className="mobile-menu-close"
                      onClick={() => setShowMobileMenu(false)}
                      aria-label="Fermer"
                    >
                      ✕
                    </button>
                  </div>
                  {FILTERS.map((f) => (
                    <button
                      key={f.value}
                      className="mobile-menu-item"
                      onClick={() => {
                        handleFilterClick(f.value);
                        setShowMobileMenu(false);
                      }}
                    >
                      {f.label}
                    </button>
                  ))}
                </nav>
              </div>
            )}
          </div>
          <div className="header-right">
            <div className="search-container">
              <input
                type="text"
                className="search-input"
                placeholder="🔍 Rechercher..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                onFocus={() => currentView !== "main" && handleNavigate("main")}
              />
            </div>
            {currentProfile && (
              <button
                className="profile-button"
                onClick={() => setCurrentProfile(null)}
                title={`Profil : ${currentProfile.name}`}
              >
                <img
                  src={getAvatarUrl(currentProfile.avatar)}
                  alt={currentProfile.name}
                  className="profile-button-avatar"
                />
              </button>
            )}
            <button
              className="settings-button"
              onClick={() => handleNavigate("settings")}
              title={t("common.settings")}
            >
              ⚙️
            </button>
            
            {/* Bouton burger pour mode (Tous/Films/Séries) avec dropdown */}
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <button 
                className="mode-menu-button"
                onClick={() => setShowModeMenu(!showModeMenu)}
                aria-label="Mode"
                title="Choisir le mode"
              >
                {mode === "mixed" ? "📺" : mode === "films" ? "🎬" : "📺"}
              </button>
              
              {/* Menu déroulant mode */}
              {showModeMenu && (
                <div className="mode-menu-dropdown">
                  <div className="mode-menu-content">
                    <div className="mode-menu-header">
                      <span className="mode-menu-title">MODE</span>
                      <button 
                        className="mode-menu-close"
                        onClick={() => setShowModeMenu(false)}
                        aria-label="Fermer"
                      >
                        ✕
                      </button>
                    </div>
                    {MODES.map((m) => (
                      <button
                        key={m.value}
                        className={`mode-menu-item ${mode === m.value ? 'active' : ''}`}
                        onClick={() => {
                          setMode(m.value);
                          setShowModeMenu(false);
                        }}
                      >
                        <span className="mode-icon">
                          {m.value === "mixed" ? "📺" : m.value === "films" ? "🎬" : "📺"}
                        </span>
                        {m.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="netflix-main">
          {categories && categories.carousel && (
            <Suspense fallback={<div className="loading-state">{t("common.loading")}</div>}>
              <Carousel
                videos={categories.carousel}
                onSelect={handleSelectVideo}
                cacheKey={cacheKey}
              />
            </Suspense>
          )}
          <div className="carousel-separator" aria-hidden="true" />
          {/* Bloc catégories caché quand une vue spécifique est active */}
          {currentView === "main" && (
            <div className="categories-container">
              {loading && !categories ? (
                <div className="loading-state">{t("common.loading")}</div>
              ) : searchResults.length > 0 ? (
                <CategoryRow
                  title={`🔍 Résultats de recherche (${searchResults.length})`}
                  videos={searchResults}
                  onSelect={handleSelectVideo}
                  cacheKey={cacheKey}
                />
              ) : searchQuery.trim() ? (
                <div className="no-results">
                  <p>Aucun résultat pour "{searchQuery}"</p>
                </div>
              ) : (
                renderCategories()
              )}
            </div>
          )}
        </main>

        {useMemo(() => {
          if (!selectedVideo) return null;
          return (
            <VideoDetail
              video={selectedVideo}
              onClose={handleCloseVideo}
              cacheKey={cacheKey}
              onDelete={handleDeleteVideo}
              onUpdateCache={handleUpdateCache}
              currentProfile={currentProfile}
            />
          );
        }, [selectedVideo, cacheKey, handleUpdateCache, handleCloseVideo, handleDeleteVideo, currentProfile])}

        {viewStates.settings && (
          <SettingsModal
            onClose={() => handleNavigate("main")}
            onCancel={() => handleNavigate("main")}
          />
        )}

        {viewStates.all && (
          <Suspense fallback={null}>
            <AllVideosGrid
              mode={mode}
              onSelect={handleSelectVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.year && (
          <Suspense fallback={null}>
            <YearGrid
              categories={categories}
              onSelect={handleSelectVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
              onDelete={handleDeleteVideo}
            />
          </Suspense>
        )}

        {viewStates.genre && (
          <Suspense fallback={null}>
            <GenreGrid
              categories={categories}
              onSelect={handleSelectVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
              onDelete={handleDeleteVideo}
            />
          </Suspense>
        )}

        {viewStates.collections && (
          <Suspense fallback={null}>
            <CollectionsView
              mode={mode}
              cacheKey={cacheKey}
              onSelectVideo={handleSelectVideo}
              onClose={() => handleNavigate("main")}
              onUpdateCache={handleUpdateCache}
            />
          </Suspense>
        )}

        {viewStates.watched && (
          <Suspense fallback={<div className="loading-screen">{t("loading")}</div>}>
            <VideoListGrid
              filter="watched"
              title={t("categories.watched")}
              cacheKey={cacheKey}
              currentProfile={currentProfile}
              onSelect={(v) => {
                setSelectedVideo(v);
                handleNavigate("main");
              }}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.resume && (
          <Suspense fallback={<div className="loading-screen">{t("loading")}</div>}>
            <VideoListGrid
              filter="to_resume"
              title={t("categories.resume")}
              cacheKey={cacheKey}
              currentProfile={currentProfile}
              onSelect={(v) => {
                setSelectedVideo(v);
                handleNavigate("main");
              }}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.random && randomVideo && (
          <VideoListModal
            title={t("nav.random")}
            videos={[randomVideo]}
            cacheKey={cacheKey}
            single
            onSelect={(v) => {
              setSelectedVideo(v);
              handleNavigate("main");
            }}
            onClose={() => handleNavigate("main")}
            extraActions={[
              {
                label: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                ),
                onClick: () => {
                  setSelectedVideo(randomVideo);
                  handleNavigate("main");
                },
              },
              {
                label: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                  </svg>
                ),
                onClick: () => handleRandomVideo(),
              },
            ]}
            onDelete={handleDeleteVideo}
          />
        )}
      </div>
      <NetworkInfo />
      
      {/* Footer avec attribution TMDb */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-logo">
            <img 
              src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg" 
              alt="TMDb Logo" 
              className="tmdb-logo"
            />
          </div>
          <div className="footer-text">
            <p className="attribution-text">
              Ce produit utilise l'API TMDb mais n'est ni approuvé, ni certifié, ni validé par TMDb.
            </p>
            <p className="copyright-text">
              © 2025 Homeflix - Sous licence MIT
            </p>
          </div>
        </div>
      </footer>
      
      {/* Sélection de profil au lancement */}
      {!currentProfile && (
        <ProfileSelector onSelectProfile={setCurrentProfile} />
      )}
    </div>
  );
}

