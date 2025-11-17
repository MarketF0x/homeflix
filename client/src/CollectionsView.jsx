import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import VideoCard from "./VideoCard.jsx";
import { apiFetch, getApiUrl } from "./config.js";

export default function CollectionsView({ mode, cacheKey, onSelectVideo, onClose, onUpdateCache }) {
  const [collections, setCollections] = useState({});
  const [standalone, setStandalone] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [editingCollection, setEditingCollection] = useState(null);
  const [newCollectionName, setNewCollectionName] = useState("");
  const scrollRef = useRef(null);

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
      if (selectedCollection) {
        setSelectedCollection(null);
      } else {
        onClose();
      }
    };
    window.history.pushState({ collectionsView: true }, "", "");
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [selectedCollection, onClose]);

  useEffect(() => {
    loadCollections();
  }, [mode, cacheKey]);

  async function loadCollections() {
    try {
      setLoading(true);
      const response = await apiFetch(`/api/collections?mode=${mode}`);
      const data = await response.json();
      setCollections(data.collections || {});
      setStandalone(data.standalone || []);
      // Après chargement, remonter en haut de la zone scrollable
      if (scrollRef.current) scrollRef.current.scrollTop = 0;
    } catch (error) {
      console.error("Erreur chargement collections:", error);
    } finally {
      setLoading(false);
    }
  }

  // Au montage et à chaque changement de panneau (liste <-> détails), remonter en haut
  useEffect(() => {
    try { window.scrollTo({ top: 0, behavior: 'instant' }); } catch {}
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, [selectedCollection]);

  async function handleRenameCollection(oldName) {
    if (!newCollectionName.trim()) return;
    
    try {
      // R�cup�rer toutes les vid�os de cette collection
      const videosToUpdate = collections[oldName].videos;
      
      // Mettre � jour chaque vid�o
      for (const video of videosToUpdate) {
        await apiFetch(`/api/video/update`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: video.id,
            collection_name: newCollectionName.trim()
          })
        });
      }
      
      // Recharger les collections
      setEditingCollection(null);
      setNewCollectionName("");
      
      // Forcer la mise � jour du cache global
      if (onUpdateCache) {
        onUpdateCache();
      }
      
      await loadCollections();
    } catch (error) {
      console.error("Erreur renommage collection:", error);
      alert("Erreur lors du renommage de la collection");
    }
  }

  async function handleDeleteCollection(collectionName) {
    if (!confirm(`Voulez-vous vraiment supprimer la collection "${collectionName}" ?\n\nLes vid�os ne seront pas supprim�es, seule l'appartenance � la collection sera retir�e.`)) {
      return;
    }
    
    try {
      // R�cup�rer toutes les vid�os de cette collection
      const videosToUpdate = collections[collectionName].videos;
      
      // Mettre � jour chaque vid�o pour retirer la collection
      for (const video of videosToUpdate) {
        await apiFetch(`/api/video/update`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: video.id,
            collection_name: ""  // Vider le champ collection
          })
        });
      }
      
      // Forcer la mise � jour du cache global
      if (onUpdateCache) {
        onUpdateCache();
      }
      
      await loadCollections();
    } catch (error) {
      console.error("Erreur suppression collection:", error);
      alert("Erreur lors de la suppression de la collection");
    }
  }

  const collectionNames = Object.keys(collections).sort();

  if (!selectedCollection) {
    return createPortal(
      <div className="modal-container" role="dialog" aria-modal="true">
        <div className="modal-overlay" onClick={onClose} />
        <div className="modal-content modal-large">
          <div className="modal-header">
            <h2 className="modal-title">
              Collections & Sagas ({collectionNames.length})
            </h2>
            <button className="modal-close-button" onClick={onClose} aria-label="Fermer">
              
            </button>
          </div>

          {loading ? (
            <div className="modal-loading">Chargement...</div>
          ) : (
            <div className="modal-scrollable" ref={scrollRef}>
              {collectionNames.length === 0 && standalone.length === 0 ? (
                <div className="modal-empty">Aucune collection d�tect�e</div>
              ) : (
                <div className="collections-grid">
                  {collectionNames.map((collectionName) => {
                    const videos = collections[collectionName].videos;
                    const displayVideos = videos.slice(0, 6);
                    const isEditing = editingCollection === collectionName;
                    
                    return (
                      <div
                        key={collectionName}
                        className="collection-card"
                      >
                        <div className="collection-card-header">
                          {isEditing ? (
                            <div style={{ flex: 1, display: 'flex', gap: '8px', alignItems: 'center' }}>
                              <input
                                type="text"
                                value={newCollectionName}
                                onChange={(e) => setNewCollectionName(e.target.value)}
                                placeholder={collectionName}
                                autoFocus
                                style={{
                                  flex: 1,
                                  padding: '6px 10px',
                                  backgroundColor: '#222',
                                  color: '#fff',
                                  border: '1px solid #444',
                                  borderRadius: '4px',
                                  fontSize: '14px'
                                }}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') handleRenameCollection(collectionName);
                                  if (e.key === 'Escape') {
                                    setEditingCollection(null);
                                    setNewCollectionName("");
                                  }
                                }}
                              />
                              <button
                                onClick={() => handleRenameCollection(collectionName)}
                                style={{
                                  padding: '6px 12px',
                                  backgroundColor: '#e50914',
                                  color: '#fff',
                                  border: 'none',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontSize: '14px'
                                }}
                              >
                                OK
                              </button>
                              <button
                                onClick={() => {
                                  setEditingCollection(null);
                                  setNewCollectionName("");
                                }}
                                style={{
                                  padding: '6px 12px',
                                  backgroundColor: '#333',
                                  color: '#fff',
                                  border: 'none',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontSize: '14px'
                                }}
                              >
                                ?
                              </button>
                            </div>
                          ) : (
                            <>
                              <div onClick={() => setSelectedCollection(collectionName)} style={{ flex: 1, cursor: 'pointer' }}>
                                <h3 className="collection-card-title">{collectionName}</h3>
                                <div className="collection-card-count">
                                  {videos.length} vid�o{videos.length > 1 ? 's' : ''}
                                </div>
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setEditingCollection(collectionName);
                                  setNewCollectionName(collectionName);
                                }}
                                style={{
                                  padding: '6px 12px',
                                  backgroundColor: '#222',
                                  color: '#fff',
                                  border: '1px solid #444',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontSize: '14px',
                                  marginLeft: '8px'
                                }}
                                title="Modifier le nom de la collection"
                              >
                                ??
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteCollection(collectionName);
                                }}
                                style={{
                                  padding: '6px 12px',
                                  backgroundColor: '#222',
                                  color: '#ff4444',
                                  border: '1px solid #444',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontSize: '14px',
                                  marginLeft: '4px'
                                }}
                                title="Supprimer la collection"
                              >
                                ???
                              </button>
                            </>
                          )}
                        </div>
                        <div 
                          className="collection-thumbnails"
                          onClick={() => !isEditing && setSelectedCollection(collectionName)}
                          style={{ cursor: isEditing ? 'default' : 'pointer' }}
                        >
                          {displayVideos.map((video, idx) => (
                            <img
                              key={idx}
                              src={getApiUrl(`/api/thumbnail?path=${encodeURIComponent(video.path)}&v=${cacheKey}`)}
                              alt={video.title}
                              className="collection-thumbnail"
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })}

                  {standalone.length > 0 && (
                    <div
                      className="collection-card"
                      onClick={() => setSelectedCollection("standalone")}
                    >
                      <div className="collection-card-header">
                        <h3 className="collection-card-title">Films autonomes</h3>
                        <div className="collection-card-count">
                          {standalone.length} vid�o{standalone.length > 1 ? 's' : ''}
                        </div>
                      </div>
                      <div className="collection-thumbnails">
                        {standalone.slice(0, 6).map((video, idx) => (
                          <img
                            key={idx}
                            src={getApiUrl(`/api/thumbnail?path=${encodeURIComponent(video.path)}&v=${cacheKey}`)}
                            alt={video.title}
                            className="collection-thumbnail"
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>,
      document.body
    );
  }

  const videos = selectedCollection === "standalone" 
    ? standalone 
    : collections[selectedCollection]?.videos || [];

  return createPortal(
    <div className="modal-container" role="dialog" aria-modal="true">
      <div className="modal-overlay" onClick={() => setSelectedCollection(null)} />
      <div className="modal-content modal-large">
        <div className="modal-header">
          <div className="modal-header-with-back">
            <button className="modal-back-button" onClick={() => setSelectedCollection(null)}>
               Retour
            </button>
            <h2 className="modal-title">
              {selectedCollection === "standalone" ? "Films autonomes" : selectedCollection} ({videos.length})
            </h2>
          </div>
          <button className="modal-close-button" onClick={onClose} aria-label="Fermer">
            
          </button>
        </div>

  <div className="modal-scrollable" ref={scrollRef}>
          <div className="modal-video-grid">
            {videos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                cacheKey={cacheKey}
                onClick={(v) => {
                  onClose();
                  onSelectVideo(v);
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}


