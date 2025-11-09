import { createPortal } from "react-dom";
import ScrollableRow from "./ScrollableRow.jsx";

/**
 * Composant affichant les vidéos triées par genre dans une grille
 */
export default function GenreGrid({ categories, onSelect, cacheKey, onClose }) {
  if (!categories || !categories.by_genre) return null;

  const genres = Object.keys(categories.by_genre).sort((a, b) => 
    a.localeCompare(b)
  );

  return createPortal(
    <div className="secondary-page" role="dialog" aria-modal="true">
      <div className="secondary-page-overlay" onClick={onClose} />
      <div className="secondary-page-content">
        <div className="secondary-page-header">
          <h2>🎭 Films par genre</h2>
          <button className="close-button" onClick={onClose} aria-label="Fermer">✕</button>
        </div>

        <div className="genre-sections">
          {genres.map((genre) => (
            <ScrollableRow
              key={genre}
              title={genre.charAt(0).toUpperCase() + genre.slice(1)}
              videos={categories.by_genre[genre]}
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
