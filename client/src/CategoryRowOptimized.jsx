import { memo, useCallback, useRef, useState, useEffect } from "react";
import { thumbURL } from "./config.js";
import "./category-row.css";

// Lazy loading pour les images avec Intersection Observer
function LazyImage({ src, alt, className, onLoad }) {
  const [imageSrc, setImageSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !imageSrc) {
            setImageSrc(src);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: "50px", // Charger 50px avant d'entrer dans le viewport
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [src, imageSrc]);

  const handleImageLoad = () => {
    setIsLoading(false);
    if (onLoad) onLoad();
  };

  return (
    <div ref={imgRef} className={`${className} lazy-image-container`}>
      {imageSrc ? (
        <img
          src={imageSrc}
          alt={alt}
          className={className}
          onLoad={handleImageLoad}
          loading="lazy"
          style={{ opacity: isLoading ? 0 : 1, transition: "opacity 0.3s" }}
        />
      ) : (
        <div className="image-placeholder" style={{ backgroundColor: "#1a1a1a" }} />
      )}
    </div>
  );
}

const LazyImageMemo = memo(LazyImage);

function CategoryRow({ title, videos, onSelect, cacheKey = 0, onDelete }) {
  // Les hooks doivent être appelés avant tout return conditionnel
  const handleSelect = useCallback((v) => onSelect(v), [onSelect]);
  const scrollContainerRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const scroll = useCallback((direction) => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      
      if (direction === 'right') {
        if (scrollLeft >= scrollWidth - clientWidth - 10) {
          scrollContainerRef.current.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          scrollContainerRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
      } else {
        if (scrollLeft <= 0) {
          scrollContainerRef.current.scrollTo({ left: scrollWidth, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          scrollContainerRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
      }
    }
  }, []);

  const handleScroll = useCallback(() => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  }, []);

  if (!videos || videos.length === 0) return null;

  return (
    <div className="category-row">
      <h3 className="category-title">{title}</h3>
      <div className="category-scroll-container">
        <button 
          className="category-scroll-button left"
          onClick={() => scroll('left')}
          aria-label="Défiler à gauche"
        >
          ‹
        </button>
        <div 
          className="category-scroll"
          ref={scrollContainerRef}
          onScroll={handleScroll}
        >
          {videos.map((video) => (
            <VideoCard
              key={video.id}
              video={video}
              cacheKey={cacheKey}
              onSelect={handleSelect}
            />
          ))}
        </div>
        <button 
          className="category-scroll-button right"
          onClick={() => scroll('right')}
          aria-label="Défiler à droite"
        >
          ›
        </button>
      </div>
    </div>
  );
}

// Composant de carte vidéo mémoïsé pour éviter re-renders inutiles
const VideoCard = memo(({ video, cacheKey, onSelect }) => {
  const handleClick = useCallback(() => {
    onSelect(video);
  }, [video, onSelect]);

  return (
    <div className="category-card" onClick={handleClick}>
      <LazyImageMemo
        className="category-poster"
        src={`${thumbURL(video.path)}&v=${cacheKey}`}
        alt={video.title}
      />
      <div className="category-card-title">{video.title}</div>
      {video.watched && (
        <div className="watched-badge">✓ Vu</div>
      )}
            {video.last_position > 0 && (
              <div
                className="resume-badge"
                aria-label="Reprendre la lecture"
                data-tooltip="Reprendre la lecture"
                title="Reprendre la lecture"
              >
                ⏸
              </div>
            )}
    </div>
  );
});

VideoCard.displayName = 'VideoCard';

export default memo(CategoryRow);
export { CategoryRow };

