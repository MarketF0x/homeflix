import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboard';
import './SearchSuggestions.css';

/**
 * SearchSuggestions Component
 * Barre de recherche avec suggestions intelligentes
 */
export default function SearchSuggestions({ 
  videos = [], 
  onSelectVideo,
  onClose 
}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Focus automatique
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Filtrer les suggestions
  useEffect(() => {
    if (query.trim().length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const searchQuery = query.toLowerCase();
    const filtered = videos
      .filter(video => {
        const titleMatch = video.title?.toLowerCase().includes(searchQuery);
        const yearMatch = video.year?.toString().includes(searchQuery);
        const genreMatch = video.genres?.some(g => 
          g.toLowerCase().includes(searchQuery)
        );
        return titleMatch || yearMatch || genreMatch;
      })
      .slice(0, 8); // Limite à 8 suggestions

    setSuggestions(filtered);
    setIsOpen(filtered.length > 0);
    setSelectedIndex(-1);
  }, [query, videos]);

  // Navigation clavier
  const handleArrowDown = useCallback(() => {
    setSelectedIndex(prev => 
      prev < suggestions.length - 1 ? prev + 1 : 0
    );
  }, [suggestions.length]);

  const handleArrowUp = useCallback(() => {
    setSelectedIndex(prev => 
      prev > 0 ? prev - 1 : suggestions.length - 1
    );
  }, [suggestions.length]);

  const handleEnter = useCallback(() => {
    if (selectedIndex >= 0 && suggestions[selectedIndex]) {
      onSelectVideo?.(suggestions[selectedIndex]);
      handleClose();
    }
  }, [selectedIndex, suggestions, onSelectVideo]);

  const handleEscape = useCallback(() => {
    handleClose();
  }, []);

  useKeyboardNavigation({
    onArrowDown: handleArrowDown,
    onArrowUp: handleArrowUp,
    onEnter: handleEnter,
    onEscape: handleEscape,
    enabled: isOpen
  });

  const handleClose = () => {
    setQuery('');
    setSuggestions([]);
    setIsOpen(false);
    onClose?.();
  };

  const handleSelectSuggestion = (video) => {
    onSelectVideo?.(video);
    handleClose();
  };

  // Highlight matching text
  const highlightMatch = (text, query) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="highlight">{part}</mark>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  // Suggestions groupées par type
  const groupedSuggestions = suggestions.reduce((acc, video) => {
    const type = video.type || 'movie';
    if (!acc[type]) acc[type] = [];
    acc[type].push(video);
    return acc;
  }, {});

  return (
    <div className="search-modal">
      <div className="search-container">
        <div className="search-input-wrapper">
          <svg className="search-icon" width="20" height="20" viewBox="0 0 20 20">
            <path 
              fill="currentColor" 
              d="M8 12a4 4 0 100-8 4 4 0 000 8zm0 2A6 6 0 118 2a6 6 0 010 12zm7.293-.707a1 1 0 011.414 1.414l-3-3a1 1 0 00-1.414-1.414l3 3z"
            />
          </svg>
          
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            placeholder="Rechercher un film, série, année, genre..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
          />
          
          {query && (
            <button 
              className="search-clear" 
              onClick={() => setQuery('')}
              aria-label="Effacer"
            >
              ✕
            </button>
          )}
        </div>

        {isOpen && suggestions.length > 0 && (
          <div className="search-suggestions" ref={suggestionsRef}>
            {Object.entries(groupedSuggestions).map(([type, items]) => (
              <div key={type} className="suggestion-group">
                <div className="suggestion-group-title">
                  {type === 'movie' ? '🎬 Films' : '📺 Séries'}
                </div>
                
                {items.map((video, index) => {
                  const globalIndex = suggestions.indexOf(video);
                  const isSelected = globalIndex === selectedIndex;
                  
                  return (
                    <div
                      key={video.id}
                      className={`suggestion-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleSelectSuggestion(video)}
                      onMouseEnter={() => setSelectedIndex(globalIndex)}
                    >
                      {video.poster_path && (
                        <img
                          src={video.poster_path}
                          alt={video.title}
                          className="suggestion-poster"
                          loading="lazy"
                        />
                      )}
                      
                      <div className="suggestion-content">
                        <div className="suggestion-title">
                          {highlightMatch(video.title || 'Sans titre', query)}
                        </div>
                        
                        <div className="suggestion-meta">
                          {video.year && <span>{video.year}</span>}
                          {video.genres && video.genres.length > 0 && (
                            <span className="suggestion-genres">
                              {video.genres.slice(0, 2).join(', ')}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      {isSelected && (
                        <div className="suggestion-arrow">→</div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        {query.length >= 2 && suggestions.length === 0 && (
          <div className="search-no-results">
            <div className="no-results-icon">🔍</div>
            <div className="no-results-text">
              Aucun résultat pour "<strong>{query}</strong>"
            </div>
          </div>
        )}

        <div className="search-shortcuts">
          <kbd>↑</kbd> <kbd>↓</kbd> pour naviguer · 
          <kbd>Enter</kbd> pour sélectionner · 
          <kbd>Esc</kbd> pour fermer
        </div>
      </div>
      
      <div className="search-backdrop" onClick={handleClose} />
    </div>
  );
}
