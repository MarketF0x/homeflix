import React from "react";

// Titre SVG avec dégradé + brillance compatible (desktop et mobile)
// Pas de background-clip:text -> fonctionne de façon fiable dans Chromium/Electron et Firefox
export default function LogoTitle({ text = "HOMEONE" }) {
  const safeText = String(text);
  return (
    <svg
      className="logo-title-svg"
      viewBox="0 0 1000 240"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label={safeText}
      focusable="false"
    >
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%" gradientUnits="objectBoundingBox">
          <stop offset="0%" stopColor="#ff1a1a" />
          <stop offset="15%" stopColor="#e50914" />
          <stop offset="35%" stopColor="#ff4444" />
          <stop offset="55%" stopColor="#e50914" />
          <stop offset="75%" stopColor="#b20710" />
          <stop offset="100%" stopColor="#ff1a1a" />
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            from="-0.4 0"
            to="0.4 0"
            dur="6s"
            repeatCount="indefinite"
            additive="sum"
          />
        </linearGradient>

        {/* Brillance blanche qui balaie le texte */}
        <linearGradient id="shineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="transparent" />
          <stop offset="48%" stopColor="rgba(255,255,255,0.9)" />
          <stop offset="52%" stopColor="rgba(255,255,255,0.6)" />
          <stop offset="100%" stopColor="transparent" />
          <animateTransform
            attributeName="gradientTransform"
            type="translate"
            from="-1 0"
            to="1 0"
            dur="10s"
            repeatCount="indefinite"
          />
        </linearGradient>

        <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Glow de fond (léger) */}
      <g filter="url(#softGlow)">
        <text
          x="50%"
          y="50%"
          dominantBaseline="middle"
          textAnchor="middle"
          className="logo-title-text base"
          fill="url(#logoGradient)"
        >
          {safeText}
        </text>
        {/* Brillance au-dessus du texte */}
        <text
          x="50%"
          y="50%"
          dominantBaseline="middle"
          textAnchor="middle"
          className="logo-title-text shine"
          fill="url(#shineGradient)"
        >
          {safeText}
        </text>
      </g>
    </svg>
  );
}
