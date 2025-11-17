import { motion, AnimatePresence } from 'framer-motion';

/**
 * Page Transition Variants
 * Configurations d'animation pour les transitions de pages
 */

// Fade & Slide (par défaut)
export const fadeSlideVariants = {
  initial: { 
    opacity: 0, 
    y: 20 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: {
      duration: 0.2,
      ease: 'easeIn'
    }
  }
};

// Scale (pour les modals)
export const scaleVariants = {
  initial: { 
    opacity: 0, 
    scale: 0.9 
  },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: {
      duration: 0.2,
      ease: 'easeOut'
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.9,
    transition: {
      duration: 0.15,
      ease: 'easeIn'
    }
  }
};

// Slide from right (pour les pages latérales)
export const slideRightVariants = {
  initial: { 
    opacity: 0, 
    x: 100 
  },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  },
  exit: { 
    opacity: 0, 
    x: 100,
    transition: {
      duration: 0.2,
      ease: 'easeIn'
    }
  }
};

// Fade uniquement (pour les overlays)
export const fadeVariants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: { duration: 0.2 }
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.15 }
  }
};

/**
 * Stagger Children Animation
 * Pour animer les listes d'éléments
 */
export const staggerContainerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05
    }
  }
};

export const staggerItemVariants = {
  initial: { 
    opacity: 0, 
    y: 20 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.3
    }
  }
};

/**
 * Modal Backdrop Animation
 */
export const backdropVariants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: { duration: 0.2 }
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.15 }
  }
};
