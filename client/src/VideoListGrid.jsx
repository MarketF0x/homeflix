import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import VideoCard from "./VideoCard.jsx";
import { fetchCategories, deleteVideo } from "./config.js";

/**
 * Composant affichant une liste filtrée de vidéos dans un modal
 * Utilisé pour "Déjà vu" et "Reprise"
 */
export default function VideoListGrid({ filter, title, onSelect, cacheKey, onClose, currentProfile }) {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  // Bloquer le scroll de la page principale quand le modal est ouvert
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    async function loadVideos() {
      setLoading(true);
      try {
        const profileId = currentProfile?.id || null;
        console.log(`📥 VideoListGrid chargement (filter=${filter}, profile=${profileId})`);
        const data = await fetchCategories("mixed", profileId);
        // filter peut être "watched" ou "to_resume"
        setVideos(data[filter] || []);
        console.log(`📦 VideoListGrid reçu: ${(data[filter] || []).length} vidéos`);
      } catch (error) {
        console.error(`Erreur lors du chargement (${filter}):`, error);
        setVideos([]);
      } finally {
        setLoading(false);
      }
    }

    loadVideos();
  }, [filter, currentProfile]);

  const handleDeleteVideo = async (video) => {
    try {
      await deleteVideo(video.id, true);
      setVideos(prevVideos => prevVideos.filter(v => v.id !== video.id));
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
          <h2 className="modal-title">{title} ({videos.length})</h2>
          <button className="modal-close-button" onClick={onClose} aria-label="Fermer">
            ✕
          </button>
        </div>

        {loading ? (
          <div className="modal-loading">Chargement...</div>
        ) : videos.length === 0 ? (
          <div className="modal-empty">Aucune vidéo trouvée</div>
        ) : (
          <div className="modal-scrollable">
            <div className="modal-video-grid">
              {videos.map((video) => (
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

