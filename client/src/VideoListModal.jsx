import { createPortal } from "react-dom";
import VideoCard from "./VideoCard.jsx";
import "./grid.css";

export default function VideoListModal({
  title,
  videos = [],
  cacheKey = 0,
  onSelect,
  onClose,
  single = false,
  highlightProgress = false,
  extraActions = [],
}) {
  // Assurons-nous que le portail est bien monté
  const modalRoot = document.getElementById("modal-root") || document.body;
  
  // Gestionnaire pour fermer la modale quand on clique en dehors
  const handleOutsideClick = (e) => {
    if (e.target.classList.contains('secondary-page') || 
        e.target.classList.contains('secondary-page-overlay')) {
      onClose();
    }
  };

  return createPortal(
    <div 
      className="secondary-page" 
      role="dialog" 
      aria-modal="true" 
      onClick={handleOutsideClick}
    >
      <div className="secondary-page-overlay" />
      <div className="secondary-page-content" onClick={(e) => e.stopPropagation()}>
        <div className="secondary-page-header">
          <h2>{title}{!single && videos?.length ? ` (${videos.length})` : ""}</h2>
          <div className="header-actions">
            {extraActions.map((action, idx) => (
              <button key={idx} className="action-button" onClick={action.onClick}>
                {action.label}
              </button>
            ))}
            <button className="close-button" onClick={onClose} aria-label="Fermer">✕</button>
          </div>
        </div>

        <div className={`video-grid ${single ? "single" : ""}`}>
          {videos.map((video) => (
            <div key={video.id} className="video-grid-item">
              <VideoCard
                video={video}
                cacheKey={cacheKey}
                onClick={(v) => {
                  onSelect?.(v);
                }}
              />
              {highlightProgress && video.last_position > 0 && video.duration_seconds > 0 && (
                <div className="list-progress">
                  Reprise: {Math.round((video.last_position / video.duration_seconds) * 100)}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}
