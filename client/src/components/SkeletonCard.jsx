import React from 'react';
import './SkeletonCard.css';

/**
 * Skeleton Card - Loading placeholder pour les cartes vidéo
 * Affiche une animation de chargement pendant le fetch des données
 */
export default function SkeletonCard() {
  return (
    <div className="video-card skeleton-card">
      <div className="skeleton-image">
        <div className="skeleton-shimmer"></div>
      </div>
      <div className="skeleton-content">
        <div className="skeleton-title">
          <div className="skeleton-shimmer"></div>
        </div>
        <div className="skeleton-info">
          <div className="skeleton-shimmer"></div>
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton Grid - Grille de skeletons pour AllVideosGrid
 */
export function SkeletonGrid({ count = 12 }) {
  return (
    <div className="videos-grid">
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard key={`skeleton-${index}`} />
      ))}
    </div>
  );
}

/**
 * Skeleton Row - Rangée de skeletons pour Carousel
 */
export function SkeletonRow({ count = 6 }) {
  return (
    <div className="scrollable-row-inner">
      {Array.from({ length: count }).map((_, index) => (
        <div key={`skeleton-row-${index}`} className="carousel-item">
          <SkeletonCard />
        </div>
      ))}
    </div>
  );
}
