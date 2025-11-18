import { useState, memo, useCallback, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { thumbURL, updateVideo, enrichVideoFromTMDb } from "./api";
import VideoPlayer from "./VideoPlayer";
import { videoLogger } from "./logger";
import "./styles/pages/video-detail.css";

function VideoDetailComponent({ video, onClose, onDelete, onUpdateCache, currentProfile }) {
  const openedAtRef = useRef(Date.now());
  useEffect(() => { openedAtRef.current = Date.now(); }, [video?.id]);
  const [isLoading, setIsLoading] = useState(false);
  const [showPlayer, setShowPlayer] = useState(false);
  const [isEditingMetadata, setIsEditingMetadata] = useState(false);
  const [editedMetadata, setEditedMetadata] = useState({
    title: video?.title || "",
    year: video?.year || "",
    genre: video?.genre || "",
    overview: video?.overview || "",
    cast: video?.cast || "",
    collection_name: video?.collection || "",
    posterUrl: "",
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [posterPreview, setPosterPreview] = useState(null);
  const [cacheKey, setCacheKey] = useState(Date.now());
  const [showRecentPosters, setShowRecentPosters] = useState(false);
  const [recentPosters, setRecentPosters] = useState([]);
  const [tmdbUrl, setTmdbUrl] = useState("");
  const [forceImageReload, setForceImageReload] = useState(0);

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

  // Gestion du bouton retour pour fermer VideoDetail
  useEffect(() => {
    const handlePopState = (e) => {
      e.preventDefault();
      console.log("🔙 Bouton retour - Fermeture de VideoDetail");
      onClose();
    };

    // Ajouter un état à l'historique pour VideoDetail
    window.history.pushState({ videoDetail: true }, "", "");
    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [onClose]);

  const handlePlay = useCallback(() => {
    videoLogger.debug('Opening player for video:', video.title);
    setShowPlayer(true);
  }, [video]);

  const handleDelete = async () => {
    if (onDelete) {
      await onDelete(video);
      onClose();
    }
  };

  const handleTitleClick = () => {
    setEditedMetadata({
      title: video?.title || "",
      year: video?.year || "",
      genre: video?.genre || "",
      overview: video?.overview || "",
      cast: video?.cast || "",
      collection_name: video?.collection || "",
      posterUrl: "",
    });
    setPosterPreview(null);
    setIsEditingMetadata(true);
  };

  const handleCancelEdit = () => {
    // Réinitialiser tous les champs du formulaire aux valeurs d'origine
    setEditedMetadata({
      title: video?.title || "",
      year: video?.year || "",
      genre: video?.genre || "",
      overview: video?.overview || "",
      cast: video?.cast || "",
      collection_name: video?.collection || "",
      posterUrl: "",
    });
    setPosterPreview(null);
    setTmdbUrl("");
    setIsEditingMetadata(false);
  };

  const handlePosterUrlChange = (url) => {
    setEditedMetadata({...editedMetadata, posterUrl: url});
    // Prévisualiser l'image
    if (url.trim()) {
      setPosterPreview(url.trim());
    } else {
      setPosterPreview(null);
    }
  };

  const loadRecentPosters = async () => {
    try {
      const response = await fetch('/api/recent-posters');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const text = await response.text();
      const data = JSON.parse(text);
      
      setRecentPosters(data.posters || []);
      setShowRecentPosters(true);
    } catch (error) {
      videoLogger.error("Erreur chargement affiches récentes:", error);
    }
  };

  const applyRecentPoster = async (posterPath) => {
    try {
      setSaveMessage("⏳ Copie de l'affiche en cours...");
      
      const response = await updateVideo(video.id, { 
        copy_poster: posterPath 
      });
      
      if (response) {
        setSaveMessage("⏳ Affiche copiée ! Rechargement de l'image...");
        
        // Fermer la galerie immédiatement
        setShowRecentPosters(false);
        
        // Démonter temporairement l'image pour forcer un rechargement
        setForceImageReload(-1);
        
        // Attendre que le fichier soit bien écrit et que l'image soit démontée
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Générer les nouvelles valeurs et remonter l'image
        const newCacheKey = Date.now();
        const newReloadCounter = Math.floor(Math.random() * 1000000); // Valeur aléatoire pour garantir l'unicité
        
        // Remonter l'image avec les nouvelles valeurs
        setCacheKey(newCacheKey);
        setForceImageReload(newReloadCounter);
        
        // Construire la nouvelle URL d'aperçu
        const newPreviewUrl = `${thumbURL(video.path)}&v=${newCacheKey}&r=${newReloadCounter}`;
        setPosterPreview(newPreviewUrl);
        
        // Ne pas forcer le rechargement global du carrousel ici
        
        setSaveMessage("✓ Affiche mise à jour ! Fermeture automatique...");
        
        // Fermer l'éditeur après 2 secondes
        setTimeout(() => {
          setIsEditingMetadata(false);
          setPosterPreview(null);
          setSaveMessage("");
        }, 2000);
      } else {
        setSaveMessage("⚠️ Pas de réponse du serveur");
      }
    } catch (error) {
      console.error("❌ Erreur copie affiche:", error);
      videoLogger.error("Erreur copie affiche:", error);
      setSaveMessage(`✗ Erreur: ${error.message || error}`);
      setTimeout(() => setSaveMessage(""), 5000);
    }
  };

  const deleteRecentPoster = async (posterPath, filename) => {
    if (!confirm(`Supprimer définitivement l'affiche "${filename}" ?\n\nCette action est irréversible.`)) {
      return;
    }
    
    try {
      const response = await fetch('/api/delete-poster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ poster_path: posterPath })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
  await response.json();
      
      // Recharger la liste des affiches
      await loadRecentPosters();
      
      setSaveMessage("✓ Affiche supprimée !");
      setTimeout(() => setSaveMessage(""), 2000);
    } catch (error) {
      videoLogger.error("Erreur suppression:", error);
      setSaveMessage(`✗ Erreur: ${error.message || error}`);
      setTimeout(() => setSaveMessage(""), 5000);
    }
  };

  const handleSaveMetadata = async () => {
    try {
      setSaveMessage("💾 Sauvegarde en cours...");
      
      // Préparer les données à sauvegarder
      const dataToSave = {
        title: editedMetadata.title,
        year: editedMetadata.year,
        genre: editedMetadata.genre,
        overview: editedMetadata.overview,
        cast: editedMetadata.cast,
        collection_name: editedMetadata.collection_name,
      };
      
      let posterUpdated = false;
      
      // Si une URL d'affiche est fournie, l'ajouter
      if (editedMetadata.posterUrl && editedMetadata.posterUrl.trim()) {
        dataToSave.poster_url = editedMetadata.posterUrl.trim();
        setSaveMessage("📥 Téléchargement de l'affiche...");
        posterUpdated = true;
      }
      
      console.log("💾 Sauvegarde des données:", dataToSave);
      const response = await updateVideo(video.id, dataToSave);
      
      // Vérifier si la collection a changé
      const collectionChanged = editedMetadata.collection_name !== (video.collection || "");
      
      // Mettre à jour l'objet video localement UNIQUEMENT avec les champs retournés
      // IMPORTANT: Ne JAMAIS utiliser Object.assign qui peut écraser des propriétés comme 'path'
      if (response.title !== undefined) video.title = response.title;
      if (response.year !== undefined) video.year = response.year;
      if (response.genre !== undefined) video.genre = response.genre;
      if (response.overview !== undefined) video.overview = response.overview;
      if (response.cast !== undefined) video.cast = response.cast;
      if (response.collection_name !== undefined) video.collection = response.collection_name;
      
      // Si l'affiche ou la collection a été mise à jour
      if (posterUpdated || collectionChanged) {
        // Forcer le rechargement localement de l'affiche
        setCacheKey(Date.now());
        setForceImageReload(prev => prev + 1);
        
        // Ne PAS recharger le carrousel global pour éviter de perdre le contexte
        
        if (posterUpdated && collectionChanged) {
          setSaveMessage("✓ Affiche et collection mises à jour !");
        } else if (posterUpdated) {
          setSaveMessage("✓ Affiche mise à jour !");
        } else {
          setSaveMessage("✓ Collection mise à jour !");
        }
      } else {
        setSaveMessage("✓ Métadonnées sauvegardées !");
      }
      
      setTimeout(() => {
        setSaveMessage("");
        setIsEditingMetadata(false);
      }, 2000);
    } catch (error) {
      console.error("❌ Erreur sauvegarde métadonnées:", error);
      setSaveMessage(`✗ Erreur: ${error.message || error}`);
      setTimeout(() => setSaveMessage(""), 5000);
    }
  };

  const handleEnrichFromTMDb = async () => {
    try {
      setSaveMessage("� Sauvegarde des modifications...");
      
      // Ne sauvegarder que le titre et l'année s'ils ont été modifiés
      const changesExist = 
        (editedMetadata.title && editedMetadata.title !== video.title) ||
        (editedMetadata.year && editedMetadata.year !== video.year);
      
      if (changesExist) {
        setSaveMessage("💾 Sauvegarde du titre/année...");
        
        const dataToSave = {};
        if (editedMetadata.title && editedMetadata.title !== video.title) {
          dataToSave.title = editedMetadata.title;
        }
        if (editedMetadata.year && editedMetadata.year !== video.year) {
          dataToSave.year = editedMetadata.year;
        }
        
        const saveResponse = await updateVideo(video.id, dataToSave);
        if (saveResponse.title !== undefined) video.title = saveResponse.title;
        if (saveResponse.year !== undefined) video.year = saveResponse.year;
      }
      
      // Enrichir depuis TMDb avec le titre actuel en BDD
      setSaveMessage("🔍 Recherche sur TMDb...");
      
      const result = await enrichVideoFromTMDb(video.id);
      
      if (result.ok && result.video) {
        // Mettre à jour avec les données TMDb
        // IMPORTANT: Ne JAMAIS utiliser Object.assign qui peut écraser 'path'
        if (result.video.title !== undefined) video.title = result.video.title;
        if (result.video.year !== undefined) video.year = result.video.year;
        if (result.video.genre !== undefined) video.genre = result.video.genre;
        if (result.video.overview !== undefined) video.overview = result.video.overview;
        if (result.video.cast !== undefined) video.cast = result.video.cast;
        if (result.video.vote_average !== undefined) video.vote_average = result.video.vote_average;
        if (result.video.poster_path !== undefined) video.poster_path = result.video.poster_path;
        if (result.video.collection_name !== undefined) video.collection = result.video.collection_name;
        
        setEditedMetadata({
          title: result.video.title,
          year: result.video.year || "",
          genre: result.video.genre || "",
          overview: result.video.overview || "",
          cast: result.video.cast || "",
          collection_name: result.video.collection || "",
          posterUrl: "",
        });
        
        // Forcer le rechargement de l'affiche si elle a changé
        setCacheKey(Date.now());
        setForceImageReload(prev => prev + 1);
        
        // Ne PAS recharger le carousel - on met juste à jour l'affichage local
        // Désactiver pour éviter de perdre le contexte visuel
        // if (onUpdateCache) {
        //   onUpdateCache();
        // }
        
        setSaveMessage("✓ Métadonnées TMDb récupérées !");
        
        // Fermer l'éditeur après 2 secondes pour revenir à l'aperçu
        setTimeout(() => {
          setIsEditingMetadata(false);
          setSaveMessage("");
        }, 2000);
      } else {
        setSaveMessage("⚠️ " + (result.message || "Aucune métadonnée trouvée"));
        setTimeout(() => setSaveMessage(""), 5000);
      }
      
    } catch (error) {
      console.error("Erreur enrichissement TMDb:", error);
      setSaveMessage("✗ Erreur lors de la recherche TMDb");
      setTimeout(() => setSaveMessage(""), 5000);
    }
  };

  const enrichFromTmdbUrl = async () => {
    if (!tmdbUrl.trim()) {
      setSaveMessage("⚠️ Veuillez entrer une URL TMDb");
      setTimeout(() => setSaveMessage(""), 3000);
      return;
    }

    try {
      setIsLoading(true);
      setSaveMessage("🔍 Récupération depuis TMDb...");
      
      console.log("📤 Envoi requête TMDb URL:", tmdbUrl);
      
      const response = await fetch(`/api/video/${video.id}/enrich-from-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tmdb_url: tmdbUrl })
      });
      
      console.log("📥 Réponse serveur:", response.status, response.statusText);
      
      if (!response.ok) {
        let errorDetail = "Erreur serveur";
        try {
          const error = await response.json();
          errorDetail = error.detail || error.message || JSON.stringify(error);
        } catch (e) {
          errorDetail = `HTTP ${response.status}: ${response.statusText}`;
        }
        console.error("❌ Erreur serveur:", errorDetail);
        throw new Error(errorDetail);
      }
      
      const result = await response.json();
      console.log("✅ Résultat:", result);
      
      if (result.ok && result.video) {
        // Mettre à jour les données de la vidéo localement
        if (result.video.title !== undefined) video.title = result.video.title;
        if (result.video.year !== undefined) video.year = result.video.year;
        if (result.video.genre !== undefined) video.genre = result.video.genre;
        if (result.video.overview !== undefined) video.overview = result.video.overview;
        if (result.video.cast !== undefined) video.cast = result.video.cast;
        if (result.video.vote_average !== undefined) video.vote_average = result.video.vote_average;
        if (result.video.collection_name !== undefined) video.collection = result.video.collection_name;
        
        setEditedMetadata({
          title: result.video.title,
          year: result.video.year || "",
          genre: result.video.genre || "",
          overview: result.video.overview || "",
          cast: result.video.cast || "",
          collection_name: result.video.collection || "",
          posterUrl: "",
        });
        
        // Forcer le rechargement de l'affiche localement
        setCacheKey(Date.now());
        setForceImageReload(prev => prev + 1);
        
        // Ne PAS recharger le carousel - on met juste à jour l'affichage local
        // Désactiver pour éviter de perdre le contexte visuel
        // if (onUpdateCache) {
        //   onUpdateCache();
        // }
        
        setTmdbUrl("");
        
        setSaveMessage("✓ Métadonnées récupérées depuis TMDb !");
        
        // Fermer l'éditeur après 2 secondes pour revenir à l'aperçu
        setTimeout(() => {
          setIsEditingMetadata(false);
          setSaveMessage("");
        }, 2000);
      } else {
        setSaveMessage("⚠️ " + (result.error || result.message || "Erreur inconnue"));
        setTimeout(() => setSaveMessage(""), 5000);
      }
    } catch (error) {
      console.error("❌ Erreur enrichissement depuis URL:", error);
      console.error("❌ Stack:", error.stack);
      
      // Afficher le message d'erreur détaillé
      let errorMsg = "Erreur lors de la récupération";
      if (error.message) {
        errorMsg = error.message;
      }
      
      setSaveMessage("✗ " + errorMsg);
      setTimeout(() => setSaveMessage(""), 5000);
    } finally {
      setIsLoading(false);
    }
  };

  // Formater la durée en heures/minutes
  const formatDuration = (seconds) => {
    if (!seconds) return "Durée inconnue";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
  };

  // Générer les étoiles pour la note
  const renderRating = () => {
    if (!video.vote_average) return null;
    const rating = Math.round(video.vote_average / 2); // Convert 10 scale to 5 stars
    return (
      <div className="detail-rating">
        {[...Array(5)].map((_, i) => (
          <span key={i} className={i < rating ? "star filled" : "star"}>★</span>
        ))}
        <span className="rating-text">{video.vote_average}/10</span>
      </div>
    );
  };

  const handleOverlayClick = (e) => {
    // Empêcher la fermeture immédiate si le clic d'ouverture "fuit" jusqu'à l'overlay
    if (Date.now() - openedAtRef.current < 250) {
      e.stopPropagation();
      return;
    }
    onClose();
  };

  if (!video) return null;

  return createPortal(
    <>
      <div
        className="detail-overlay"
        onClick={handleOverlayClick}
        style={{ position: 'fixed', inset: 0, display: 'flex', zIndex: 10050, background: 'rgba(0,0,0,0.85)' }}
      >
        <div className="detail-container modern-detail" onClick={(e) => e.stopPropagation()} ref={(el) => {
          // Remettre la modale en haut au moment de l'ouverture
          if (el) {
            try {
              el.scrollTop = 0;
              // Par sécurité, remonter la fenêtre aussi
              window.scrollTo({ top: 0, behavior: 'instant' });
            } catch {}
          }
        }}>
          <button className="detail-close" onClick={onClose}>✕</button>

          <div className="detail-hero">
            {/* Section gauche : Poster avec bouton suppression */}
            <div className="detail-poster-wrapper">
              <div className="detail-poster-container">
                {forceImageReload >= 0 && (
                  <img
                    key={`poster-${cacheKey}-${forceImageReload}`}
                    className="detail-poster-image"
                    src={`${thumbURL(video.path)}&v=${cacheKey}&r=${forceImageReload}`}
                    alt={video.title}
                    onLoad={(e) => {
                      console.log("🖼️ Affiche principale chargée, cacheKey:", cacheKey, "reload:", forceImageReload);
                      console.log("🖼️ URL complète:", e.target.src);
                    }}
                    onError={(e) => {
                      console.error("❌ Erreur chargement affiche principale:", e.target.src);
                    }}
                  />
                )}
                
                {/* Bouton Play sur jaquette (mobile uniquement) - masqué en mode édition */}
                {!isEditingMetadata && (
                  <button
                    className="detail-poster-play-mobile"
                    onClick={handlePlay}
                    aria-label="Lire la vidéo"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </button>
                )}
                
                {/* Bouton de suppression/masquage sur la jaquette */}
                {onDelete && !showDeleteConfirm && (
                  <button
                    className="delete-btn-detail"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeleteConfirm(true);
                    }}
                    title={currentProfile?.is_main ? "Supprimer cette vidéo" : "Masquer cette vidéo"}
                    aria-label={currentProfile?.is_main ? "Supprimer" : "Masquer"}
                  >
                    {currentProfile?.is_main ? "🗑️" : "👁️‍🗨️"}
                  </button>
                )}
                
                {/* Confirmation de suppression/masquage sur la jaquette */}
                {showDeleteConfirm && (
                  <div className="delete-confirm-overlay">
                    <div className="delete-confirm-box">
                      <p>{currentProfile?.is_main ? "Supprimer cette vidéo ?" : "Masquer cette vidéo ?"}</p>
                      <div className="delete-confirm-buttons">
                        <button 
                          className="delete-confirm-yes" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete();
                          }}
                        >
                          ✓ Oui
                        </button>
                        <button 
                          className="delete-confirm-no" 
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowDeleteConfirm(false);
                          }}
                        >
                          ✗ Non
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Section droite : Informations */}
            <div className="detail-info-wrapper">
              {isEditingMetadata ? (
                <div className="detail-metadata-edit">
                  <h3 style={{ color: '#e50914', marginBottom: '15px' }}>✏️ Édition des métadonnées</h3>
                  
                  <label className="metadata-label">
                    Titre:
                    <input
                      type="text"
                      value={editedMetadata.title}
                      onChange={(e) => setEditedMetadata({...editedMetadata, title: e.target.value})}
                      className="metadata-input"
                      autoFocus
                    />
                  </label>
                  
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <label className="metadata-label" style={{ flex: 1 }}>
                      Année:
                      <input
                        type="number"
                        value={editedMetadata.year}
                        onChange={(e) => setEditedMetadata({...editedMetadata, year: e.target.value})}
                        className="metadata-input"
                        placeholder="2024"
                      />
                    </label>
                    
                    <label className="metadata-label" style={{ flex: 1 }}>
                      Genre:
                      <input
                        type="text"
                        value={editedMetadata.genre}
                        onChange={(e) => setEditedMetadata({...editedMetadata, genre: e.target.value})}
                        className="metadata-input"
                        placeholder="Action, Drame..."
                      />
                    </label>
                  </div>
                  
                  <label className="metadata-label">
                    Synopsis:
                    <textarea
                      value={editedMetadata.overview}
                      onChange={(e) => setEditedMetadata({...editedMetadata, overview: e.target.value})}
                      className="metadata-textarea"
                      rows="4"
                      placeholder="Description du film..."
                    />
                  </label>
                  
                  <label className="metadata-label">
                    Acteurs (séparés par des virgules):
                    <input
                      type="text"
                      value={editedMetadata.cast}
                      onChange={(e) => setEditedMetadata({...editedMetadata, cast: e.target.value})}
                      className="metadata-input"
                      placeholder="Tom Hanks, Morgan Freeman..."
                    />
                  </label>
                  
                  <label className="metadata-label">
                    Collection / Saga:
                    <input
                      type="text"
                      value={editedMetadata.collection_name}
                      onChange={(e) => setEditedMetadata({...editedMetadata, collection_name: e.target.value})}
                      className="metadata-input"
                      placeholder="Alien, Harry Potter, Star Wars..."
                    />
                  </label>
                  
                  <label className="metadata-label">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span>URL de l'affiche:</span>
                      <button 
                        onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(editedMetadata.title + ' poster')}&tbm=isch`, '_blank')}
                        className="inline-search-btn"
                        type="button"
                        title="Chercher sur Google Images"
                      >
                        🔍 Chercher
                      </button>
                      <button 
                        onClick={loadRecentPosters}
                        className="inline-search-btn recent-posters-btn"
                        type="button"
                        title="Afficher les affiches récemment téléchargées"
                      >
                        🖼️ Récentes
                      </button>
                    </div>
                    <input
                      type="url"
                      value={editedMetadata.posterUrl}
                      onChange={(e) => handlePosterUrlChange(e.target.value)}
                      className="metadata-input"
                      placeholder="https://... (Clic droit sur l'image > Copier le lien de l'image)"
                    />
                    <small style={{ color: '#999', fontSize: '0.85em', marginTop: '5px', display: 'block' }}>
                      💡 Cherche sur Google, puis <strong>clic droit sur l'image → Copier le lien de l'image</strong> et colle ici
                    </small>
                    
                    {/* URL TMDb pour enrichissement direct */}
                    <label style={{ marginTop: '15px', display: 'block', color: '#e0e0e0', marginBottom: '8px', fontWeight: '500' }}>
                      🎬 URL TMDb (pour récupérer toutes les métadonnées)
                    </label>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <input
                        type="url"
                        value={tmdbUrl}
                        onChange={(e) => setTmdbUrl(e.target.value)}
                        className="metadata-input"
                        placeholder="https://www.themoviedb.org/movie/550 ou /tv/1399"
                        style={{ flex: 1 }}
                      />
                      <button
                        onClick={enrichFromTmdbUrl}
                        disabled={isLoading || !tmdbUrl.trim()}
                        className="btn-secondary"
                        style={{ 
                          background: tmdbUrl.trim() ? 'linear-gradient(135deg, #01d277 0%, #01b464 100%)' : '#555',
                          cursor: tmdbUrl.trim() ? 'pointer' : 'not-allowed',
                          whiteSpace: 'nowrap'
                        }}
                        title="Récupérer les métadonnées depuis cette fiche TMDb"
                      >
                        🔄 Importer
                      </button>
                    </div>
                    <small style={{ color: '#999', fontSize: '0.85em', marginTop: '5px', display: 'block' }}>
                      💡 Trouve le bon film/série sur <a href={`https://www.themoviedb.org/search?query=${encodeURIComponent(editedMetadata.title)}`} target="_blank" rel="noopener" style={{color: '#01d277'}}>themoviedb.org</a>, copie l'URL de la page et clique sur "Importer"
                    </small>
                    
                    {/* Prévisualisation de l'affiche */}
                    {posterPreview && (
                      <div className="poster-preview-container">
                        <div className="poster-preview-label">
                          📸 Prévisualisation de l'affiche actuelle:
                        </div>
                        <img 
                          key={posterPreview}
                          src={posterPreview} 
                          alt="Prévisualisation"
                          className="poster-preview-image"
                          onError={(e) => {
                            console.error("❌ Erreur chargement prévisualisation:", posterPreview);
                            e.target.style.display = 'none';
                            setSaveMessage("❌ URL d'image invalide");
                            setTimeout(() => setSaveMessage(""), 3000);
                          }}
                          onLoad={(e) => {
                            console.log("✅ Prévisualisation chargée:", posterPreview);
                            e.target.style.display = 'block';
                          }}
                        />
                      </div>
                    )}
                    
                    {/* Galerie des affiches récentes */}
                    {showRecentPosters && (
                      <div style={{
                        marginTop: '15px',
                        padding: '15px',
                        background: 'rgba(5, 150, 105, 0.1)',
                        borderRadius: '8px',
                        border: '1px solid rgba(5, 150, 105, 0.3)'
                      }}>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: '12px'
                        }}>
                          <div style={{ color: '#059669', fontWeight: 'bold' }}>
                            🖼️ Affiches récentes ({recentPosters.length})
                          </div>
                          <button
                            onClick={() => setShowRecentPosters(false)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: '#999',
                              cursor: 'pointer',
                              fontSize: '1.2em'
                            }}
                          >
                            ✕
                          </button>
                        </div>
                        <div style={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
                          gap: '10px',
                          maxHeight: '300px',
                          overflowY: 'auto'
                        }}>
                          {recentPosters.map((poster, idx) => (
                            <div
                              key={idx}
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log("🖱️ Clic sur affiche:", poster.path);
                                applyRecentPoster(poster.path);
                              }}
                              style={{
                                cursor: 'pointer',
                                borderRadius: '6px',
                                overflow: 'hidden',
                                border: '2px solid transparent',
                                transition: 'all 0.2s',
                                position: 'relative'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.border = '2px solid #059669';
                                e.currentTarget.style.transform = 'scale(1.05)';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.border = '2px solid transparent';
                                e.currentTarget.style.transform = 'scale(1)';
                              }}
                              title={`Cliquer pour appliquer - ${poster.filename || ''}`}
                            >
                              {/* Bouton de suppression */}
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  deleteRecentPoster(poster.path, poster.filename);
                                }}
                                style={{
                                  position: 'absolute',
                                  top: '4px',
                                  right: '4px',
                                  width: '24px',
                                  height: '24px',
                                  borderRadius: '50%',
                                  border: 'none',
                                  background: 'rgba(220, 38, 38, 0.9)',
                                  color: 'white',
                                  fontSize: '16px',
                                  fontWeight: 'bold',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  zIndex: 10,
                                  transition: 'all 0.2s',
                                  padding: 0,
                                  lineHeight: 1
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = 'rgba(185, 28, 28, 1)';
                                  e.currentTarget.style.transform = 'scale(1.15)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = 'rgba(220, 38, 38, 0.9)';
                                  e.currentTarget.style.transform = 'scale(1)';
                                }}
                                title="Supprimer cette affiche"
                              >
                                ×
                              </button>
                              
                              <img
                                src={poster.url}
                                alt={poster.filename || 'Affiche'}
                                draggable={false}
                                onError={(e) => {
                                  console.error("❌ Erreur chargement image:", poster.url);
                                  e.target.style.border = "2px solid red";
                                }}
                                onLoad={() => {
                                  console.log("✅ Image chargée:", poster.url);
                                }}
                                style={{
                                  width: '100%',
                                  height: '150px',
                                  objectFit: 'cover',
                                  display: 'block',
                                  pointerEvents: 'none'
                                }}
                              />
                              {poster.filename && (
                                <div style={{
                                  position: 'absolute',
                                  bottom: 0,
                                  left: 0,
                                  right: 0,
                                  background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
                                  color: 'white',
                                  fontSize: '0.7em',
                                  padding: '8px 4px 4px',
                                  textAlign: 'center',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                  pointerEvents: 'none'
                                }}>
                                  {poster.filename}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </label>
                  
                  {saveMessage && (
                    <div className={`save-message ${saveMessage.includes('✓') ? 'success' : 'error'}`}>
                      {saveMessage}
                    </div>
                  )}
                  
                  <div className="metadata-edit-buttons">
                    <button onClick={handleSaveMetadata} className="save-metadata-btn">
                      💾 Sauvegarder
                    </button>
                    <button onClick={handleEnrichFromTMDb} className="tmdb-enrich-btn">
                      🎬 Re-scanner avec TMDb
                    </button>
                    <button onClick={handleCancelEdit} className="cancel-metadata-btn">
                      ✗ Annuler
                    </button>
                  </div>
                </div>
              ) : (
                <h1 
                  className="detail-hero-title editable" 
                  onClick={handleTitleClick}
                  title="Cliquer pour éditer les métadonnées"
                >
                  {video.title}
                  <span className="edit-icon">✏️</span>
                </h1>
              )}
              
              {/* Meta informations essentielles */}
              <div className="detail-meta-row">
                {video.year && (
                  <span className="meta-pill year">{video.year}</span>
                )}
                {video.duration_seconds && (
                  <span className="meta-pill duration">{formatDuration(video.duration_seconds)}</span>
                )}
                {video.genre && (
                  <span className="meta-pill genre">{video.genre}</span>
                )}
                {renderRating()}
              </div>

              {/* Description TMDB */}
              {video.overview && (
                <p className="detail-description">{video.overview}</p>
              )}
              
              {/* Message si pas de métadonnées */}
              {!video.overview && !video.cast && !video.vote_average && (
                <div className="detail-no-metadata">
                  <p style={{ color: '#ff9800', fontSize: '14px', marginTop: '10px' }}>
                    ℹ️ Aucune métadonnée TMDb disponible. 
                    Allez dans <strong>Paramètres</strong> → <strong>Enrichir les métadonnées</strong> pour récupérer les résumés et acteurs.
                  </p>
                </div>
              )}

              {/* Acteurs principaux */}
              {video.cast && (
                <div className="detail-cast">
                  <strong>🎭 Avec :</strong> {video.cast}
                </div>
              )}

              {/* Boutons d'action */}
              <div className="detail-action-buttons">
                <button 
                  className="detail-play-button" 
                  onClick={handlePlay}
                  title="Lire la vidéo"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                  <span style={{ fontSize: '1.1rem', fontWeight: '600' }}>LANCER LE FILM</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* VideoPlayer rendu APRÈS l'overlay pour avoir le bon z-index */}
      {showPlayer && (
        <VideoPlayer 
          video={video} 
          onClose={() => setShowPlayer(false)} 
          currentProfile={currentProfile}
        />
      )}
    </>,
    document.body
  );
}

export default memo(VideoDetailComponent);
