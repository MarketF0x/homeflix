import { useState, useEffect } from "react";
import "./FolderBrowser.css";
import { apiFetch, getApiUrl } from "./config.js";

export default function FolderBrowser({ onSelect, onClose }) {
  const [currentPath, setCurrentPath] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [parent, setParent] = useState(null);

  useEffect(() => {
    loadDirectory(currentPath);
  }, []);

  async function loadDirectory(path) {
    setLoading(true);
    try {
      const url = path 
        ? `/api/filesystem/browse?path=${encodeURIComponent(path)}`
        : `/api/filesystem/browse`;
      
      const response = await apiFetch(url);
      const data = await response.json();
      
      setCurrentPath(data.current_path);
      setItems(data.items);
      setParent(data.parent);
    } catch (error) {
      console.error("Erreur lors du chargement:", error);
      alert("❌ Erreur lors du chargement du répertoire");
    } finally {
      setLoading(false);
    }
  }

  function handleFolderClick(folderPath) {
    loadDirectory(folderPath);
  }

  function handleParentClick() {
    if (parent) {
      loadDirectory(parent);
    }
  }

  function handleSelect() {
    if (currentPath) {
      onSelect(currentPath);
    }
  }

  return (
    <div className="folder-browser-overlay" onClick={onClose}>
      <div className="folder-browser" onClick={(e) => e.stopPropagation()}>
        <div className="folder-browser-header">
          <h3>📁 Sélectionner un répertoire</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="folder-browser-path">
          <span className="path-label">Emplacement :</span>
          <span className="current-path">{currentPath || "Sélectionnez un lecteur"}</span>
        </div>

        <div className="folder-browser-info">
          <span className="info-icon">ℹ️</span>
          <span className="info-text">Le scan inclura automatiquement tous les sous-dossiers</span>
        </div>

        <div className="folder-browser-toolbar">
          {parent && (
            <button className="parent-btn" onClick={handleParentClick}>
              ⬆️ Dossier parent
            </button>
          )}
        </div>

        <div className="folder-browser-content">
          {loading ? (
            <div className="loading-state">Chargement...</div>
          ) : items.length === 0 ? (
            <div className="empty-state">Aucun dossier</div>
          ) : (
            <div className="folders-list">
              {items.map((item) => (
                <div
                  key={item.path}
                  className={`folder-item ${item.locked ? 'locked' : ''}`}
                  onClick={() => !item.locked && handleFolderClick(item.path)}
                  title={item.path}
                >
                  <span className="folder-icon">
                    {item.type === 'drive' ? '💾' : item.locked ? '🔒' : '📁'}
                  </span>
                  <span className="folder-name">{item.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="folder-browser-footer">
          <button className="cancel-btn" onClick={onClose}>
            Annuler
          </button>
          <button 
            className="select-btn" 
            onClick={handleSelect}
            disabled={!currentPath}
          >
            Sélectionner ce dossier
          </button>
        </div>
      </div>
    </div>
  );
}

