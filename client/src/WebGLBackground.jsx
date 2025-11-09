// Fond "aurore boréale" 100% CSS (léger et doux, couleurs coucher de soleil)
import React from "react";

export default function WebGLBackground() {
  return (
    <div className="webgl-bg aurora-bg">
      {/* couches lumineuses douces */}
      <div className="aurora-layer l1" />
      <div className="aurora-layer l2" />
      <div className="aurora-layer l3" />
      <div className="aurora-layer l4" />
      {/* gradient de fond pour relier l'ensemble */}
      <div className="aurora-gradient" />
    </div>
  );
}
