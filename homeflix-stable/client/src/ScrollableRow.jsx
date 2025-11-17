import { useRef, useState } from "react";
import VideoCard from "./VideoCard.jsx";
import "./scrollable-row.css";

export default function ScrollableRow({ title, videos, onSelect, cacheKey, onClose, onDelete }) {
  const rowRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const scroll = (direction) => {
    if (rowRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = rowRef.current;
      
      if (direction === 'right') {
        // Si on est à la fin, revenir au début
        if (scrollLeft >= scrollWidth - clientWidth - 10) {
          rowRef.current.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          rowRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
      } else {
        // Si on est au début, aller à la fin
        if (scrollLeft <= 0) {
          rowRef.current.scrollTo({ left: scrollWidth, behavior: 'smooth' });
        } else {
          const scrollAmount = clientWidth * 0.8;
          rowRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
      }
    }
  };

  const handleScroll = () => {
    if (rowRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = rowRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  if (!videos || videos.length === 0) return null;

  return (
    <div className="scrollable-section">
      <h3 className="section-title">{title}</h3>
      <div className="scrollable-container">
        <button 
          className="scroll-arrow left"
          onClick={() => scroll('left')}
          aria-label="Défiler à gauche"
        >
          ‹
        </button>
        <div 
          className="scrollable-content"
          ref={rowRef}
          onScroll={handleScroll}
        >
          {videos.map((video) => (
            <div key={video.id} className="video-item">
              <VideoCard
                video={video}
                cacheKey={cacheKey}
                onClick={(v) => {
                  if (onClose) onClose();
                  onSelect(v);
                }}
                onDelete={onDelete}
              />
            </div>
          ))}
        </div>
        <button 
          className="scroll-arrow right"
          onClick={() => scroll('right')}
          aria-label="Défiler à droite"
        >
          ›
        </button>
      </div>
    </div>
  );
}
