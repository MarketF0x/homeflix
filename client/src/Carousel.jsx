import { useState, useEffect, memo } from "react";
import { thumbURL } from "./api";

function Carousel({ videos, onSelect, cacheKey = 0 }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (!videos || videos.length === 0 || !isAutoPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % videos.length);
    }, 8000);

    return () => clearInterval(interval);
  }, [videos, isAutoPlaying]);

  if (!videos || videos.length === 0) return null;

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + videos.length) % videos.length);
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % videos.length);
  };

  // Calculer les indices des 5 vidéos à afficher
  const farLeftIndex = (currentIndex - 2 + videos.length) % videos.length;
  const leftIndex = (currentIndex - 1 + videos.length) % videos.length;
  const rightIndex = (currentIndex + 1) % videos.length;
  const farRightIndex = (currentIndex + 2) % videos.length;

  const farLeftVideo = videos[farLeftIndex];
  const leftVideo = videos[leftIndex];
  const currentVideo = videos[currentIndex];
  const rightVideo = videos[rightIndex];
  const farRightVideo = videos[farRightIndex];

  return (
    <div 
      className="carousel-3d-wrapper"
      onMouseEnter={() => setIsAutoPlaying(false)}
      onMouseLeave={() => setIsAutoPlaying(true)}
    >
      <button 
        className="carousel-btn prev" 
        onClick={goToPrevious} 
        aria-label="Précédent"
      >
        ‹
      </button>

      <div className="carousel-container">
        {/* Affiche extrême gauche */}
        <div 
          className="carousel-card far-left" 
          onClick={goToPrevious}
        >
          <img
            loading="lazy"
            src={`${thumbURL(farLeftVideo.path)}&v=${cacheKey}`}
            alt={farLeftVideo.title}
            className="carousel-img"
          />
        </div>

        {/* Affiche gauche */}
        <div className="carousel-card left" onClick={goToPrevious}>
          <img
            src={`${thumbURL(leftVideo.path)}&v=${cacheKey}`}
            alt={leftVideo.title}
            className="carousel-img"
          />
        </div>

        {/* Affiche centrale */}
        <div className="carousel-card center" onClick={() => onSelect(currentVideo)}>
          <img
            src={`${thumbURL(currentVideo.path)}&v=${cacheKey}`}
            alt={currentVideo.title}
            className="carousel-img"
          />
          <div className="carousel-overlay">
            <h2 className="carousel-title">{currentVideo.title}</h2>
            <div className="carousel-metadata">
              {currentVideo.year && <span className="carousel-year">{currentVideo.year}</span>}
              {currentVideo.genre && <span className="carousel-genre">{currentVideo.genre}</span>}
            </div>
            <button className="carousel-play-btn" onClick={(e) => { e.stopPropagation(); onSelect(currentVideo); }}>
              ▶ Lire
            </button>
          </div>
        </div>

        {/* Affiche droite */}
        <div className="carousel-card right" onClick={goToNext}>
          <img
            src={`${thumbURL(rightVideo.path)}&v=${cacheKey}`}
            alt={rightVideo.title}
            className="carousel-img"
          />
        </div>

        {/* Affiche extrême droite */}
        <div className="carousel-card far-right" onClick={goToNext}>
          <img
            src={`${thumbURL(farRightVideo.path)}&v=${cacheKey}`}
            alt={farRightVideo.title}
            className="carousel-img"
          />
        </div>
      </div>

      <button className="carousel-btn next" onClick={goToNext} aria-label="Suivant">
        ›
      </button>

      <div className="carousel-indicators">
        {videos.map((_, index) => (
          <button
            key={index}
            className={`indicator ${index === currentIndex ? "active" : ""}`}
            onClick={() => setCurrentIndex(index)}
            aria-label={`Vidéo ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}

export default memo(Carousel);
