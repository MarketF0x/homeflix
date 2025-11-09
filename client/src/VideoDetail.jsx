import { useState, memo, useCallback } from "react";
import { thumbURL, openPath } from "./api";
import VideoPlayer from "./VideoPlayer";
import "./video-detail.css";

// Fonction utilitaire pour formater la taille du fichier
function formatSize(bytes) {
  if (!bytes) return "Taille inconnue";
  const sizes = ["o", "Ko", "Mo", "Go"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
}

function VideoDetailComponent({ video, onClose, cacheKey = 0 }) {
  const [showPlayer, setShowPlayer] = useState(false);

  if (!video) return null;

  const handlePlay = useCallback(() => {
    setShowPlayer(true);
  }, []);

  const handleClosePlayer = useCallback(() => {
    setShowPlayer(false);
  }, []);

  if (showPlayer) {
    return <VideoPlayer video={video} onClose={handleClosePlayer} />;
  }

  // Formater la durée en heures/minutes
  const formatDuration = (seconds) => {
    if (!seconds) return "Durée inconnue";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
  };

  // Générer les étoiles pour la note
  const renderRating = () => {
    if (!video.vote_average) return null;
    const rating = Math.round(video.vote_average / 2); // Convert 10 scale to 5 stars
    return (
      <div className="detail-rating">
        {[...Array(5)].map((_, i) => (
          <span key={i} className={i < rating ? "star filled" : "star"}>★</span>
        ))}
        <span className="rating-text">{video.vote_average}/10</span>
      </div>
    );
  };

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-container modern-detail" onClick={(e) => e.stopPropagation()}>
        <button className="detail-close" onClick={onClose}>✕</button>

        <div className="detail-hero">
          {/* Section gauche : Poster avec bouton play */}
          <div className="detail-poster-wrapper">
            <div className="detail-poster-container">
              <img
                className="detail-poster-image"
                src={`${thumbURL(video.path)}&v=${cacheKey}`}
                alt={video.title}
              />
              <div className="play-button-overlay" onClick={handlePlay}>
                <div className="play-icon">▶</div>
              </div>
            </div>
          </div>

          {/* Section droite : Informations */}
          <div className="detail-info-wrapper">
            <h1 className="detail-hero-title">{video.title}</h1>
            
            {/* Meta informations essentielles */}
            <div className="detail-meta-row">
              {video.year && (
                <span className="meta-pill year">{video.year}</span>
              )}
              {video.duration_seconds && (
                <span className="meta-pill duration">{formatDuration(video.duration_seconds)}</span>
              )}
              {video.genre && (
                <span className="meta-pill genre">{video.genre}</span>
              )}
              {renderRating()}
            </div>

            {/* Description TMDB */}
            {video.overview && (
              <p className="detail-description">{video.overview}</p>
            )}

            {/* Bouton de lecture principal */}
            <div className="action-buttons">
              <button className="primary-action" onClick={handlePlay}>
                <span className="icon">▶</span>
                Lecture
              </button>
            </div>

            {/* Taille du fichier */}
            {video.size && (
              <p className="detail-file-info">
                <span className="file-icon">💾</span>
                {formatSize(video.size)}
              </p>
            )}

            {/* Boutons d'action */}
            <div className="detail-action-buttons">
              <button className="action-btn-primary" onClick={handlePlay}>
                <span className="btn-icon">▶</span>
                Lire
              </button>
              <button className="action-btn-secondary" onClick={handlePlayExternal}>
                <span className="btn-icon">📱</span>
                Lecteur externe
              </button>
            </div>

            {/* Chemin du fichier (optionnel, discret) */}
            {video.path && (
              <div className="detail-file-path">
                <span className="path-icon">📁</span>
                <span className="path-text">{video.path}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(VideoDetailComponent);
