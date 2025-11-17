import { memo, useCallback, useRef, useState } from "react";
import { thumbURL } from "./config.js";
import LazyThumb from "./LazyThumb.jsx";
import "./category-row.css";

function CategoryRow({ title, videos, onSelect, cacheKey = 0, onDelete }) {
  // Les hooks doivent être appelés avant tout return conditionnel
  const handleSelect = useCallback((v) => onSelect(v), [onSelect]);
  const scrollContainerRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  if (!videos || videos.length === 0) return null;

  const scroll = (direction) => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      
      if (direction === 'right') {
        // Si on est à la fin, revenir au début
        if (scrollLeft >= scrollWidth - clientWidth - 10) {
          scrollContainerRef.current.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          scrollContainerRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
      } else {
        // Si on est au début, aller à la fin
        if (scrollLeft <= 0) {
          scrollContainerRef.current.scrollTo({ left: scrollWidth, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          scrollContainerRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
      }
    }
  };

  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

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
          <div
            key={video.id}
            className="category-card"
            onClick={() => handleSelect(video)}
            tabIndex={0}
            role="button"
            aria-label={`Voir ${video.title}`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleSelect(video);
              }
            }}
          >
            <LazyThumb
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

export default memo(CategoryRow);
export { CategoryRow };

