import { createPortal } from "react-dom";
import { useEffect } from "react";
import ScrollableRow from "./ScrollableRow.jsx";

export default function YearGrid({ categories, onSelect, cacheKey, onClose, onDelete }) {

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
    window.history.pushState({ yearGrid: true }, "", "");
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [onClose]);

  if (!categories?.by_year) return null;
  const years = Object.keys(categories.by_year).sort((a, b) => b - a);

  return createPortal(
    <div className="modal-container">
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-content modal-large">
        <div className="modal-header">
          <h2 className="modal-title">Films par année</h2>
          <button className="modal-close-button" onClick={onClose}>✕</button>
        </div>
        <div className="modal-scrollable">
          {years.map((year) => (
            <ScrollableRow
              key={year}
              title={`Films de ${year}`}
              videos={categories.by_year[year]}
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

