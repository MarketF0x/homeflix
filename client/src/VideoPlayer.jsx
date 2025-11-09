import { useState, useRef, useEffect } from "react";
import { thumbURL } from "./api";

export default function VideoPlayer({ video, onClose }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(video?.last_position || 0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const controlsTimeoutRef = useRef(null);

  // Construire l'URL de la vidéo
  const videoUrl = `http://localhost:8000/api/stream?path=${encodeURIComponent(video.path)}`;

  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    // Charger la position sauvegardée
    if (video.last_position) {
      videoElement.currentTime = video.last_position;
    }

    // Sauvegarder la progression toutes les 5 secondes
    const saveInterval = setInterval(() => {
      if (videoElement.currentTime > 0) {
        saveProgress(Math.floor(videoElement.currentTime));
      }
    }, 5000);

    return () => {
      clearInterval(saveInterval);
      // Sauvegarder une dernière fois à la fermeture
      if (videoElement.currentTime > 0) {
        saveProgress(Math.floor(videoElement.currentTime));
      }
    };
  }, [video]);

  const saveProgress = async (position) => {
    try {
      await fetch("http://localhost:8000/api/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: video.id,
          position: position,
        }),
      });
    } catch (e) {
      console.error("Erreur sauvegarde progression:", e);
    }
  };

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
    setCurrentTime(videoElement.currentTime);
    setDuration(videoElement.duration);
  };

  const handleSeek = (e) => {
    const videoElement = videoRef.current;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    videoElement.currentTime = pos * duration;
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
    videoElement.currentTime += seconds;
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
      if (isPlaying) setShowControls(false);
    }, 3000);
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
      case "Escape":
        onClose();
        break;
    }
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [isPlaying, volume]);

  return (
    <div
      ref={playerRef}
      className="video-player-overlay"
      onMouseMove={handleMouseMove}
      onClick={togglePlay}
    >
      <video
        ref={videoRef}
        className="video-player-element"
        src={videoUrl}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        onClick={(e) => e.stopPropagation()}
      />

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

        {/* Boutons de contrôle */}
        <div className="controls-row">
          <div className="controls-left">
            <button
              className="control-btn"
              onClick={(e) => {
                e.stopPropagation();
                togglePlay();
              }}
            >
              {isPlaying ? "⏸" : "▶"}
            </button>

            <button
              className="control-btn"
              onClick={(e) => {
                e.stopPropagation();
                skip(-10);
              }}
            >
              ⏪ 10s
            </button>

            <button
              className="control-btn"
              onClick={(e) => {
                e.stopPropagation();
                skip(10);
              }}
            >
              10s ⏩
            </button>

            <div className="volume-control" onClick={(e) => e.stopPropagation()}>
              <button
                className="control-btn"
                onClick={() => {
                  const newVol = volume === 0 ? 1 : 0;
                  setVolume(newVol);
                  videoRef.current.volume = newVol;
                }}
              >
                {volume === 0 ? "🔇" : volume < 0.5 ? "🔉" : "🔊"}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={handleVolumeChange}
                className="volume-slider"
              />
            </div>

            <div className="time-display">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          <div className="controls-right">
            <button
              className="control-btn"
              onClick={(e) => {
                e.stopPropagation();
                toggleFullscreen();
              }}
            >
              {isFullscreen ? "⛶" : "⛶"}
            </button>

            <button
              className="control-btn close-btn"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      {/* Titre de la vidéo */}
      <div className={`video-title ${showControls ? "visible" : ""}`}>
        <h2>{video.title}</h2>
      </div>

      {/* Aide raccourcis */}
      {showControls && (
        <div className="keyboard-hints">
          <span>Espace: Pause</span>
          <span>←/→: -10s/+10s</span>
          <span>↑/↓: Volume</span>
          <span>F: Plein écran</span>
          <span>M: Mute</span>
          <span>Echap: Fermer</span>
        </div>
      )}
    </div>
  );
}
