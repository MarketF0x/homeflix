import { useEffect, useCallback, useRef } from 'react';

/**
 * Hook pour la navigation au clavier
 * Gère les raccourcis clavier globaux et la navigation focus
 */

export function useKeyboardNavigation({
  onEscape,
  onEnter,
  onArrowLeft,
  onArrowRight,
  onArrowUp,
  onArrowDown,
  enabled = true
}) {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e) => {
      // Ignorer si on est dans un input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          onEscape?.();
          break;
        case 'Enter':
          e.preventDefault();
          onEnter?.();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          onArrowLeft?.();
          break;
        case 'ArrowRight':
          e.preventDefault();
          onArrowRight?.();
          break;
        case 'ArrowUp':
          e.preventDefault();
          onArrowUp?.();
          break;
        case 'ArrowDown':
          e.preventDefault();
          onArrowDown?.();
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, onEscape, onEnter, onArrowLeft, onArrowRight, onArrowUp, onArrowDown]);
}

/**
 * Hook pour la navigation dans les carousels
 */
export function useCarouselNavigation({ items = [], onSelectItem }) {
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const carouselRef = useRef(null);

  const handleArrowLeft = useCallback(() => {
    setSelectedIndex((prev) => (prev > 0 ? prev - 1 : items.length - 1));
  }, [items.length]);

  const handleArrowRight = useCallback(() => {
    setSelectedIndex((prev) => (prev < items.length - 1 ? prev + 1 : 0));
  }, [items.length]);

  const handleEnter = useCallback(() => {
    if (items[selectedIndex]) {
      onSelectItem?.(items[selectedIndex]);
    }
  }, [items, selectedIndex, onSelectItem]);

  useKeyboardNavigation({
    onArrowLeft: handleArrowLeft,
    onArrowRight: handleArrowRight,
    onEnter: handleEnter
  });

  // Auto-scroll vers l'élément sélectionné
  useEffect(() => {
    if (carouselRef.current && items[selectedIndex]) {
      const selectedElement = carouselRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center'
        });
      }
    }
  }, [selectedIndex, items]);

  return {
    selectedIndex,
    setSelectedIndex,
    carouselRef
  };
}

/**
 * Hook pour les raccourcis globaux
 */
export function useGlobalShortcuts({
  onSearch,        // Ctrl/Cmd + K
  onSettings,      // Ctrl/Cmd + ,
  onFullscreen,    // F
  onPlayPause,     // Espace
  onMute,          // M
  onVolumeUp,      // Arrow Up (dans lecteur)
  onVolumeDown,    // Arrow Down (dans lecteur)
  onSeekForward,   // Arrow Right (dans lecteur)
  onSeekBackward,  // Arrow Left (dans lecteur)
  enabled = true
}) {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e) => {
      // Ignorer si on est dans un input (sauf pour Escape)
      const isInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';
      
      // Ctrl/Cmd + K → Recherche
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        onSearch?.();
        return;
      }

      // Ctrl/Cmd + , → Paramètres
      if ((e.ctrlKey || e.metaKey) && e.key === ',') {
        e.preventDefault();
        onSettings?.();
        return;
      }

      if (isInput) return;

      switch (e.key) {
        case 'f':
        case 'F':
          e.preventDefault();
          onFullscreen?.();
          break;
        case ' ':
          e.preventDefault();
          onPlayPause?.();
          break;
        case 'm':
        case 'M':
          e.preventDefault();
          onMute?.();
          break;
        case 'ArrowUp':
          if (onVolumeUp) {
            e.preventDefault();
            onVolumeUp();
          }
          break;
        case 'ArrowDown':
          if (onVolumeDown) {
            e.preventDefault();
            onVolumeDown();
          }
          break;
        case 'ArrowRight':
          if (onSeekForward) {
            e.preventDefault();
            onSeekForward();
          }
          break;
        case 'ArrowLeft':
          if (onSeekBackward) {
            e.preventDefault();
            onSeekBackward();
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    enabled,
    onSearch,
    onSettings,
    onFullscreen,
    onPlayPause,
    onMute,
    onVolumeUp,
    onVolumeDown,
    onSeekForward,
    onSeekBackward
  ]);
}

/**
 * Hook pour le focus trap (dans les modals)
 */
export function useFocusTrap(elementRef, enabled = true) {
  useEffect(() => {
    if (!enabled || !elementRef.current) return;

    const element = elementRef.current;
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus sur le premier élément
    firstElement?.focus();

    const handleTab = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    element.addEventListener('keydown', handleTab);
    return () => element.removeEventListener('keydown', handleTab);
  }, [elementRef, enabled]);
}

export default {
  useKeyboardNavigation,
  useCarouselNavigation,
  useGlobalShortcuts,
  useFocusTrap
};
