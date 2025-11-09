import { useEffect, useState, useRef, Suspense, lazy, useMemo, useCallback } from "react";
import CategoryRow from "./CategoryRow.jsx";
import SettingsModal from "./SettingsModal.jsx";
import VideoListModal from "./VideoListModal.jsx";
import "./modal.css";
import "./nav.css";
// Lazy components pour réduire bundle initial
const Carousel = lazy(() => import("./Carousel.jsx"));
import VideoDetail from "./VideoDetail.jsx";
const AllVideosGrid = lazy(() => import("./AllVideosGrid.jsx"));
const YearGrid = lazy(() => import("./YearGrid.jsx"));
const GenreGrid = lazy(() => import("./GenreGrid.jsx"));
import { fetchCategories, getRandomVideo, openPath } from "./api";
import WebGLBackground from "./WebGLBackground.jsx";
import { useI18n } from "./i18n.jsx";

export default function App() {
  const { t } = useI18n();
  
  // États principaux
  const [categories, setCategories] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  
  // États de filtrage
  const [mode, setMode] = useState("mixed");
  const [filter, setFilter] = useState("all");
  
  // États UI
  const [loading, setLoading] = useState(false);
  const [cacheKey] = useState(0);
  
  // États de navigation
  const [currentView, setCurrentView] = useState("main");

  // Gestionnaires d'événements optimisés
  const handleCloseVideo = useCallback(() => {
    setSelectedVideo(null);
  }, []);

  const handleNavigate = useCallback((view) => {
    setCurrentView(view);
    // Reset la vidéo sélectionnée si on change de vue
    setSelectedVideo(null);
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
  // États des vues spécifiques - regroupés pour plus de clarté
  const viewStates = {
    all: useMemo(() => currentView === "all", [currentView]),
    year: useMemo(() => currentView === "year", [currentView]),
    genre: useMemo(() => currentView === "genre", [currentView]),
    watched: useMemo(() => currentView === "watched", [currentView]),
    resume: useMemo(() => currentView === "resume", [currentView]),
    random: useMemo(() => currentView === "random", [currentView]),
    settings: useMemo(() => currentView === "settings", [currentView]),
  };

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
    { value: "by_year", label: t("nav.by_year") },
    { value: "by_genre", label: t("nav.by_genre") },
    { value: "random", label: t("nav.random") },
  ];

  const [error, setError] = useState(null);

  async function load(modeArg = mode) {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/categories?mode=${modeArg}`);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Données reçues:", data);
      if (!data || !data.carousel) {
        throw new Error("Format de données invalide");
      }
      setCategories(data);
    } catch (e) {
      console.error("Erreur détaillée:", e);
      setError(e.message);
      setCategories(null);
    } finally {
      setLoading(false);
    }
  }

  async function playRandom(autoPlay = false) {
    try {
      const video = await getRandomVideo(mode);
      if (autoPlay) {
        await openPath(video.path, video.id);
      } else {
        setRandomVideo(video);
        handleNavigate("random");
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
      if (autoPlay) {
        const video = categories.to_resume[0];
        await openPath(video.path, video.id);
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
        // Ouvrir fenêtre de reprise plutôt que lancer directement
        handleNavigate("resume");
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

  // Ajout d'un effet pour gérer le scroll du body
  useEffect(() => {
    document.body.style.overflow = selectedVideo ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [selectedVideo]);

  useEffect(() => {
    load(mode);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

    // Vue par défaut : tout afficher
    return (
      <>
        {/* Afficher "Reprendre la lecture" seulement s'il y a des vidéos */}
        {categories.to_resume && categories.to_resume.length > 0 && (
          <CategoryRow
            title={t("categories.resume")}
            videos={categories.to_resume}
            onSelect={setSelectedVideo}
            cacheKey={cacheKey}
          />
        )}
        <div ref={watchedSectionRef}>
          {categories.watched && categories.watched.length > 0 && (
            <CategoryRow
              title={t("categories.watched")}
              videos={categories.watched}
              onSelect={setSelectedVideo}
              cacheKey={cacheKey}
            />
          )}
        </div>
        {Object.entries(categories.by_year || {}).slice(0, 3).map(([year, videos]) => (
          <CategoryRow
            key={year}
            title={`${t("categories.films_of")} ${year}`}
            videos={videos}
            onSelect={setSelectedVideo}
            cacheKey={cacheKey}
          />
        ))}
        {Object.entries(categories.by_genre || {}).slice(0, 3).map(([genre, videos]) => (
          <CategoryRow
            key={genre}
            title={`${t("categories.genre")} ${genre.charAt(0).toUpperCase() + genre.slice(1)}`}
            videos={videos}
            onSelect={setSelectedVideo}
            cacheKey={cacheKey}
          />
        ))}
      </>
    );
  };

  return (
    <div className="app">
      <WebGLBackground />
      <div className="content">
        <header className="netflix-header">
          <div className="header-left">
            <h1 className="logo">🎬 HomeOne</h1>
            <nav className="header-nav" role="navigation">
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
          </div>
          <div className="header-right">
            <button
              className="settings-button"
              onClick={() => handleNavigate("settings")}
              title={t("common.settings")}
            >
              ⚙️
            </button>
            <select
              className="mode-select"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              {MODES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </header>

        <main className="netflix-main">
          {categories && categories.carousel && (
            <Suspense fallback={<div className="loading-state">{t("common.loading")}</div>}>
              <Carousel
                videos={categories.carousel}
                onSelect={setSelectedVideo}
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
            />
          );
        }, [selectedVideo, cacheKey])}

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
              onSelect={setSelectedVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.year && (
          <Suspense fallback={null}>
            <YearGrid
              categories={categories}
              onSelect={setSelectedVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.genre && (
          <Suspense fallback={null}>
            <GenreGrid
              categories={categories}
              onSelect={setSelectedVideo}
              cacheKey={cacheKey}
              onClose={() => handleNavigate("main")}
            />
          </Suspense>
        )}

        {viewStates.watched && categories?.watched?.length > 0 && (
          <VideoListModal
            title={t("categories.watched")}
            videos={categories.watched}
            cacheKey={cacheKey}
            onSelect={(v) => {
              setSelectedVideo(v);
              handleNavigate("main");
            }}
            onClose={() => handleNavigate("main")}
          />
        )}

        {viewStates.resume && categories?.to_resume?.length > 0 && (
          <VideoListModal
            title={t("categories.resume")}
            videos={categories.to_resume}
            cacheKey={cacheKey}
            onSelect={(v) => {
              setSelectedVideo(v);
              handleNavigate("main");
            }}
            onClose={() => handleNavigate("main")}
            highlightProgress
          />
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
                label: t("common.play"),
                onClick: async () => {
                  await openPath(randomVideo.path, randomVideo.id);
                  handleNavigate("main");
                },
              },
              {
                label: t("common.refresh"),
                onClick: () => handleRandomVideo(),
              },
            ]}
          />
        )}
      </div>
    </div>
  );
}
