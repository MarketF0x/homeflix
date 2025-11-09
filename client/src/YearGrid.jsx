import { createPortal } from "react-dom";
import ScrollableRow from "./ScrollableRow.jsx";

/**
 * Composant affichant les vidéos triées par année dans une grille
 */
export default function YearGrid({ categories, onSelect, cacheKey, onClose }) {
  if (!categories || !categories.by_year) return null;

  const years = Object.keys(categories.by_year).sort((a, b) => b - a); // Trier par année décroissante

  return createPortal(
    <div className="secondary-page" role="dialog" aria-modal="true">
      <div className="secondary-page-overlay" onClick={onClose} />
      <div className="secondary-page-content">
        <div className="secondary-page-header">
          <h2>📅 Films par année</h2>
          <button className="close-button" onClick={onClose} aria-label="Fermer">✕</button>
        </div>

        <div className="year-sections">
          {years.map((year) => (
            <ScrollableRow
              key={year}
              title={`Films de ${year}`}
              videos={categories.by_year[year]}
              cacheKey={cacheKey}
              onSelect={onSelect}
              onClose={onClose}
            />
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}
