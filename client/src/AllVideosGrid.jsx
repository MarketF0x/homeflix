import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import VideoCard from "./VideoCard.jsx";
import { fetchAllVideos } from "./api";

/**
 * Composant affichant toutes les vidéos dans une grille avec 5 colonnes
 */
export default function AllVideosGrid({ mode, onSelect, cacheKey, onClose }) {
  const [allVideos, setAllVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAllVideos() {
      setLoading(true);
      try {
        const data = await fetchAllVideos(mode);
        setAllVideos(data.videos || []);
      } catch (error) {
        console.error("Erreur lors du chargement de toutes les vidéos:", error);
        setAllVideos([]);
      } finally {
        setLoading(false);
      }
    }

    loadAllVideos();
  }, [mode]);

  return createPortal(
    <div className="secondary-page" role="dialog" aria-modal="true">
      <div className="secondary-page-overlay" onClick={onClose} />
      <div className="secondary-page-content">
        <div className="secondary-page-header">
          <h2>📚 Toutes les vidéos ({allVideos.length})</h2>
          <button className="close-button" onClick={onClose} aria-label="Fermer">✕</button>
        </div>

        {loading ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#fff" }}>
            Chargement...
          </div>
        ) : (
          <div className="video-grid">
            {allVideos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                cacheKey={cacheKey}
                onClick={(v) => {
                  onClose();
                  onSelect(v);
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
