import { memo, useMemo } from "react";
import { thumbURL } from "./api";
import LazyThumb from "./LazyThumb.jsx";

function VideoCard({ video, cacheKey = 0, onClick }) {
  // Calculer le pourcentage de progression
  const progressPercent = useMemo(() => {
    return video.last_position && video.duration_seconds
      ? Math.min(100, (video.last_position / video.duration_seconds) * 100)
      : 0;
  }, [video.last_position, video.duration_seconds]);

  return (
    <div
      className="card"
      onClick={() => onClick && onClick(video)}
      title="Cliquez pour voir les détails"
    >
      <div className="card-image-container">
        <LazyThumb
          className="poster"
          src={`${thumbURL(video.path)}&v=${cacheKey}`}
          alt={video.title}
        />
        {/* Barre de progression pour les vidéos en cours */}
        {progressPercent > 0 && (
          <div className="progress-overlay">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
        {/* Badge "À reprendre" */}
        {progressPercent > 0 && progressPercent < 90 && (
          <div className="resume-badge">
            ⏸ {Math.floor(progressPercent)}%
          </div>
        )}
      </div>
      <div className="caption">{video.title}</div>
    </div>
  );
}

export default memo(VideoCard);
