import { createPortal } from "react-dom";
import { useEffect, useRef } from "react";
import ScrollableRow from "./ScrollableRow.jsx";

export default function GenreGrid({ categories, onSelect, cacheKey, onClose, onDelete }) {
  const scrollRef = useRef(null);

  // Bloquer le scroll de la page principale SEULEMENT sur desktop
  useEffect(() => {
    const isMobile = window.innerWidth <= 768;
    if (!isMobile) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      if (!isMobile) {
        document.body.style.overflow = "";
      }
    };
  }, []);

  // Gérer le bouton retour du téléphone
  useEffect(() => {
    const handlePopState = (e) => {
      e.preventDefault();
      onClose();
    };
    window.history.pushState({ genreGrid: true }, "", "");
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [onClose]);

  // Au montage, remonter en haut et réinitialiser la zone scrollable
  useEffect(() => {
    try { window.scrollTo({ top: 0, behavior: 'instant' }); } catch {}
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, []);

  if (!categories?.by_genre) return null;
  const genres = Object.keys(categories.by_genre).sort();

  return createPortal(
    <div className="modal-container">
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-content modal-large">
        <div className="modal-header">
          <h2 className="modal-title">Films par genre</h2>
          <button className="modal-close-button" onClick={onClose}>✕</button>
        </div>
        <div className="modal-scrollable" ref={scrollRef}>
          {genres.map((genre) => (
            <ScrollableRow
              key={genre}
              title={genre.charAt(0).toUpperCase() + genre.slice(1)}
              videos={categories.by_genre[genre]}
              cacheKey={cacheKey}
              onSelect={onSelect}
              onClose={onClose}
              onDelete={onDelete}
            />
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}

