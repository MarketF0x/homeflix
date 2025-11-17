import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import VideoCard from "./VideoCard.jsx";
import { fetchAllVideos, deleteVideo } from "./config.js";

/**
 * Composant affichant toutes les vidéos dans une grille avec 5 colonnes
 */
export default function AllVideosGrid({ mode, onSelect, cacheKey, onClose }) {
  const [allVideos, setAllVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef(null);

  // Bloquer le scroll de la page principale SEULEMENT sur desktop
  useEffect(() => {
    const isMobile = window.innerWidth <= 768;
    if (!isMobile) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      if (!isMobile) {
        document.body.style.overflow = "";
      }
    };
  }, []);

  // Gérer le bouton retour du téléphone
  useEffect(() => {
    const handlePopState = (e) => {
      e.preventDefault();
      onClose();
    };
    window.history.pushState({ allVideosGrid: true }, "", "");
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [onClose]);

  useEffect(() => {
    async function loadAllVideos() {
      setLoading(true);
      try {
        const data = await fetchAllVideos(mode);
        setAllVideos(data.videos || []);
        // Remonter en haut au moment où les données arrivent
        if (scrollRef.current) scrollRef.current.scrollTop = 0;
      } catch (error) {
        console.error("Erreur lors du chargement de toutes les vidéos:", error);
        setAllVideos([]);
      } finally {
        setLoading(false);
      }
    }

    loadAllVideos();
  }, [mode]);

  // Au montage, remonter la page et la zone scrollable
  useEffect(() => {
    try { window.scrollTo({ top: 0, behavior: 'instant' }); } catch {}
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, []);

  const handleDeleteVideo = async (video) => {
    try {
      await deleteVideo(video.id, true);
      setAllVideos(prevVideos => prevVideos.filter(v => v.id !== video.id));
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      alert("Impossible de supprimer la vidéo");
    }
  };

  return createPortal(
    <div className="modal-container" role="dialog" aria-modal="true">
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">Toutes les vidéos ({allVideos.length})</h2>
          <button className="modal-close-button" onClick={onClose} aria-label="Fermer">
            ✕
          </button>
        </div>

        {loading ? (
          <div className="modal-loading">Chargement...</div>
        ) : (
          <div className="modal-scrollable" ref={scrollRef}>
            <div className="modal-video-grid">
              {allVideos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  cacheKey={cacheKey}
                  onClick={(v) => {
                    onClose();
                    onSelect(v);
                  }}
                  onDelete={handleDeleteVideo}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}

