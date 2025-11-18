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
  // Edition groupée / fusion
  const [bulkEditOpen, setBulkEditOpen] = useState(false);
  const [bulkSelected, setBulkSelected] = useState(() => new Set());
  const [bulkNewName, setBulkNewName] = useState("");
  const [bulkProcessing, setBulkProcessing] = useState(false);
  // Recherche & vidéos globales
  const [bulkSearch, setBulkSearch] = useState("");
  const [allVideos, setAllVideos] = useState([]);
  const [allVideosLoading, setAllVideosLoading] = useState(false);
  const [videosShowLimit, setVideosShowLimit] = useState(150);
  // Sélection de vidéos à assigner
  const [selectedVideoIds, setSelectedVideoIds] = useState(() => new Set());
  // Sélection par motif (ex: SxxExx)
  const [selectPattern, setSelectPattern] = useState("S\\\d{2}E\\\d{2}");
  // Affiche & métadonnées à appliquer
  const [posterDataUrl, setPosterDataUrl] = useState("");
  const [metaTitle, setMetaTitle] = useState("");
  const [metaYear, setMetaYear] = useState("");
  const [metaGenre, setMetaGenre] = useState("");
  const [metaOverview, setMetaOverview] = useState("");
  const [metaCast, setMetaCast] = useState("");
  // Propositions d'affiches depuis la base
  const [posterSuggestions, setPosterSuggestions] = useState([]);
  const [posterSuggestLoading, setPosterSuggestLoading] = useState(false);
  const [posterChoiceUrl, setPosterChoiceUrl] = useState(""); // Utiliser une URL d'affiche existante
  const [posterCopyPath, setPosterCopyPath] = useState(""); // Copier une affiche locale existante côté serveur
  const scrollRef = useRef(null);
  const bulkSearchInputRef = useRef(null);
  const hasAnyMeta = !!(posterDataUrl || posterChoiceUrl || posterCopyPath || metaTitle || metaYear || metaGenre || metaOverview || metaCast);
  const canAssign = selectedVideoIds.size > 0 && (bulkNewName.trim() || hasAnyMeta) && !bulkProcessing;
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
    const target = (newCollectionName || '').trim();
    if (!target) return;
    if (target === oldName) {
      // Rien à faire, fermer le mode édition
      setEditingCollection(null);
      setNewCollectionName("");
      return;
    }
    
    try {
      // Récupérer toutes les vidéos de cette collection
      const videosToUpdate = collections[oldName].videos;
      
      // Mettre à jour chaque vidéo (optimisation possible: endpoint batch)
      for (const video of videosToUpdate) {
        await apiFetch(`/api/video/update`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: video.id,
            collection_name: target
          })
        });
      }
      // Mise à jour optimiste de l'état local pour retour visuel immédiat
      setCollections(prev => {
        const next = { ...prev };
        const old = next[oldName];
        if (!old) return prev;
        const moved = { ...old, videos: (old.videos || []).map(v => ({ ...v, collection_name: target })) };
        delete next[oldName];
        // Fusionner si la cible existait déjà
        if (next[target]) {
          const existing = next[target];
          // Dédupliquer par id lors de la fusion
          const byId = new Map();
          [...(existing.videos || []), ...moved.videos].forEach(v => { byId.set(v.id, v); });
          next[target] = { ...existing, videos: Array.from(byId.values()) };
        } else {
          next[target] = moved;
        }
        return next;
      });

      // Forcer la mise à jour du cache global
      if (onUpdateCache) {
        onUpdateCache();
      }
      // Nettoyer l'édition et conserver le modal ouvert
      setEditingCollection(null);
      setNewCollectionName("");
      // Si on visualisait cette collection, suivre le nouveau nom
      setSelectedCollection(sel => sel === oldName ? target : sel);
      // Rafraîchissement de sécurité depuis le serveur
      await loadCollections();
    } catch (error) {
  console.error("Erreur renommage collection:", error);
  alert("Erreur lors du renommage de la collection");
    }
  }

  const collectionNames = Object.keys(collections).sort();

  function toggleBulkSelection(name) {
    setBulkSelected(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name); else next.add(name);
      return next;
    });
  }

  async function handleBulkMerge() {
    if (!bulkNewName.trim() || bulkSelected.size === 0) return;
    setBulkProcessing(true);
    try {
      // Récupérer toutes les vidéos des collections sélectionnées
      const allVideos = [];
      bulkSelected.forEach(name => {
        const vids = collections[name]?.videos || [];
        vids.forEach(v => allVideos.push(v));
      });
      // Mise à jour: assigner nouveau nom de collection à chaque vidéo
      for (const video of allVideos) {
        await apiFetch(`/api/video/update`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: video.id, collection_name: bulkNewName.trim() })
        });
      }
      if (onUpdateCache) onUpdateCache();
      // Recharger puis s'assurer que la collection cible reste visible
      await loadCollections();
      // Nettoyer la recherche pour éviter qu'un filtre masque la collection résultat
      setBulkSearch("");
      // Reset état
      setBulkSelected(new Set());
      setBulkNewName("");
      setBulkEditOpen(false);
    } catch (e) {
      console.error("Erreur fusion collections:", e);
      alert("Erreur lors de la fusion des collections");
    } finally {
      setBulkProcessing(false);
    }
  }

  const canBulkMerge = bulkNewName.trim() && bulkSelected.size > 0 && !bulkProcessing;

  // Charger toutes les vidéos quand panneau ouverture (une seule fois)
  useEffect(() => {
    if (bulkEditOpen && allVideos.length === 0 && !allVideosLoading) {
      (async () => {
        try {
          setAllVideosLoading(true);
          const resp = await apiFetch(`/api/videos/all?mode=${mode}`);
          const data = await resp.json();
          setAllVideos(data.videos || []);
        } catch (e) {
          console.error('Erreur chargement vidéos globales:', e);
        } finally {
          setAllVideosLoading(false);
        }
      })();
    }
  }, [bulkEditOpen, allVideos.length, allVideosLoading, mode]);

  // Chargement des propositions d'affiches basées sur la recherche utilisateur
  useEffect(() => {
    let timer;
    const q = bulkSearch.trim();
    if (!bulkEditOpen) {
      setPosterSuggestions([]);
      return;
    }
    if (!q) {
      setPosterSuggestions([]);
      return;
    }
    timer = setTimeout(async () => {
      try {
        setPosterSuggestLoading(true);
        // 1) Rechercher des vidéos par titre pour proposer leur poster/thumbnail
        const videosResp = await apiFetch(`/api/videos?limit=40&search=${encodeURIComponent(q)}`);
        const videosData = await videosResp.json();
        const videoItems = (videosData.videos || []).map(v => {
          // Construire une URL d'affiche utilisable
          let url = v.poster_path || "";
          if (url && url.startsWith('/')) {
            url = `https://image.tmdb.org/t/p/w500${url}`;
          }
          if (!url) {
            url = getApiUrl(`/api/thumbnail?path=${encodeURIComponent(v.path)}&direct=1`);
          }
          return {
            id: `v-${v.id}`,
            label: v.title || (v.path || '').split(/[/\\\\]/).pop(),
            previewUrl: url,
            mode: 'url',
            source: 'videos',
            url
          };
        });

        // 2) Récupérer les affiches manuelles récentes et filtrer par similarité nom
        const recentResp = await apiFetch(`/api/recent-posters?limit=60`);
        const recentData = await recentResp.json();
        const qLower = q.toLowerCase();
        const recentItems = (recentData.posters || [])
          .filter(p => (p.filename || '').toLowerCase().includes(qLower))
          .map(p => ({
            id: `p-${p.filename}`,
            label: p.filename,
            previewUrl: getApiUrl(p.url),
            mode: 'copy',
            source: 'recent',
            copyPath: p.path
          }));

        // Fusionner, limiter et supprimer doublons par previewUrl
        const merged = [...videoItems, ...recentItems];
        const seen = new Set();
        const unique = [];
        for (const it of merged) {
          const key = `${it.mode}:${it.mode === 'copy' ? it.copyPath : it.url}`;
          if (!seen.has(key)) { seen.add(key); unique.push(it); }
          if (unique.length >= 30) break;
        }
        setPosterSuggestions(unique);
      } catch (e) {
        console.error('Erreur suggestions affiches:', e);
        setPosterSuggestions([]);
      } finally {
        setPosterSuggestLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [bulkSearch, bulkEditOpen]);

  function bytesToHuman(bytes) {
    if (!bytes && bytes !== 0) return '';
    const b = Number(bytes);
    if (isNaN(b)) return '';
    const units = ['B','KB','MB','GB','TB'];
    let i = 0; let val = b;
    while (val >= 1024 && i < units.length - 1) { val /= 1024; i++; }
    return `${val.toFixed(i === 0 ? 0 : val < 10 ? 1 : 0)} ${units[i]}`;
  }

  const searchLower = bulkSearch.trim().toLowerCase();
  const filteredCollections = searchLower
    ? collectionNames.filter(n => n.toLowerCase().includes(searchLower))
    : collectionNames;
  const filteredVideos = searchLower
    ? allVideos.filter(v => (v.title || '').toLowerCase().includes(searchLower) || (v.path || '').toLowerCase().includes(searchLower))
    : allVideos;
  const slicedVideos = filteredVideos.slice(0, videosShowLimit);

  function getVideoFilename(v) {
    const p = v.path || "";
    const parts = p.split(/[/\\\\]/);
    return parts[parts.length - 1] || p;
  }

  function suggestSeriesNameFrom(str) {
    // Retirer extension
    let base = str.replace(/\.[^.]+$/, "");
    // Retirer motif SxxExx et ce qui suit en séparateurs courants
    base = base.replace(/S\d{2}E\d{2}.*/i, "");
    // Nettoyage espaces et tirets/points
    base = base.replace(/[._-]+/g, " ").trim();
    return base || "Saga";
  }

  function selectByPatternOn(list) {
    try {
      const re = new RegExp(selectPattern, 'i');
      const next = new Set(selectedVideoIds);
      list.forEach(v => {
        const name = getVideoFilename(v);
        if (re.test(name)) next.add(v.id);
      });
      setSelectedVideoIds(next);
    } catch (e) {
      alert("Motif invalide. Exemple: S\\\\d{2}E\\\\d{2}");
    }
  }

  function proposeNameFromSelection() {
    const chosen = allVideos.filter(v => selectedVideoIds.has(v.id));
    if (chosen.length === 0) return;
    const names = chosen.map(v => suggestSeriesNameFrom(getVideoFilename(v))).filter(Boolean);
    if (names.length === 0) return;
    // Choisir le nom le plus fréquent
    const freq = new Map();
    names.forEach(n => freq.set(n, (freq.get(n) || 0) + 1));
    let best = names[0];
    let bestCount = 0;
    for (const [n, c] of freq.entries()) {
      if (c > bestCount) { best = n; bestCount = c; }
    }
    setBulkNewName(best);
  }

  if (!selectedCollection) {
    return createPortal(
      <div className="modal-container" role="dialog" aria-modal="true">
        <div className="modal-overlay" onClick={onClose} />
        <div className="modal-content modal-large">
          <div className="modal-header">
            <h2 className="modal-title">
              Collections & Sagas ({collectionNames.length})
            </h2>
            <button
              type="button"
              className={bulkEditOpen ? 'btn-danger btn-sm' : 'btn-secondary btn-sm'}
              onClick={() => setBulkEditOpen(o => !o)}
              aria-expanded={bulkEditOpen}
              aria-controls="bulk-edit-panel"
              style={{ marginLeft: '12px' }}
            >
              {bulkEditOpen ? 'Fermer édition' : 'Éditer'}
            </button>
            <button className="modal-close-button" onClick={onClose} aria-label="Fermer" title="Fermer">
              <span aria-hidden="true">×</span>
            </button>
          </div>

          {bulkEditOpen && (
            <div
              id="bulk-edit-panel"
              className="bulk-edit-panel"
              style={{
                background: '#141414',
                border: '1px solid #303030',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '16px'
              }}
            >
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
                <div style={{ flex: '1 1 240px' }}>
                  <label htmlFor="bulk-search" style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Recherche (collections ou vidéos)</label>
                  <input
                    id="bulk-search"
                    type="text"
                    value={bulkSearch}
                    onChange={e => setBulkSearch(e.target.value)}
                    placeholder="Tapez un nom..."
                    ref={bulkSearchInputRef}
                    style={{
                      width: '100%',
                      padding: '8px 10px',
                      background: '#1d1d1d',
                      color: '#fff',
                      border: '1px solid #444',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                <div style={{ flex: '1 1 240px' }}>
                  <label htmlFor="pattern-input" style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Sélection par motif (ex: S\u00A0xx E\u00A0xx)</label>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <input
                      id="pattern-input"
                      type="text"
                      value={selectPattern}
                      onChange={e => setSelectPattern(e.target.value)}
                      placeholder={"S\\d{2}E\\d{2}"}
                      style={{
                        flex: 1,
                        padding: '8px 10px',
                        background: '#1d1d1d',
                        color: '#fff',
                        border: '1px solid #444',
                        borderRadius: '4px'
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setSelectPattern('S\\\d{2}E\\\d{2}')}
                      style={{ padding: '8px 10px', background: '#222', color: '#ddd', border: '1px solid #333', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', whiteSpace: 'nowrap' }}
                    >SxxExx</button>
                    <button
                      type="button"
                      onClick={() => selectByPatternOn(filteredVideos)}
                      style={{ padding: '8px 10px', background: '#222', color: '#ddd', border: '1px solid #333', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', whiteSpace: 'nowrap' }}
                    >Sélectionner par motif</button>
                  </div>
                </div>
                <div style={{ flex: '1 1 240px' }}>
                  <label htmlFor="bulk-new-name" style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Nouveau nom de collection</label>
                  <input
                    id="bulk-new-name"
                    type="text"
                    value={bulkNewName}
                    onChange={e => setBulkNewName(e.target.value)}
                    placeholder="Entrer un nom"
                    style={{
                      width: '100%',
                      padding: '8px 10px',
                      background: '#222',
                      color: '#fff',
                      border: '1px solid #444',
                      borderRadius: '4px'
                    }}
                  />
                  {/* Suggestions rapides de collections existantes */}
                  {bulkNewName && (
                    <div style={{ marginTop: '6px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {filteredCollections.slice(0, 6).map(name => (
                        <button
                          key={name}
                          type="button"
                          onClick={() => setBulkNewName(name)}
                          style={{
                            padding: '4px 8px',
                            background: '#1f1f1f',
                            color: '#ddd',
                            border: '1px solid #333',
                            borderRadius: '12px',
                            fontSize: '12px',
                            cursor: 'pointer'
                          }}
                          aria-label={`Utiliser la collection ${name}`}
                        >{name}</button>
                      ))}
                      <button
                        type="button"
                        onClick={proposeNameFromSelection}
                        style={{ padding: '4px 8px', background: '#1f1f1f', color: '#ddd', border: '1px solid #333', borderRadius: '12px', fontSize: '12px', cursor: 'pointer' }}
                      >Proposer un nom depuis la sélection</button>
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    className="btn-primary"
                    disabled={!canAssign}
                    onClick={async () => {
                      setBulkProcessing(true);
                      try {
                        const target = bulkNewName.trim();
                        // Appliquer la collection cible à toutes les vidéos sélectionnées
                        for (const id of selectedVideoIds) {
                          const payload = { id };
                          if (target) payload.collection_name = target;
                          // Ordre de priorité: image téléversée > URL d'affiche choisie > copie d'affiche locale
                          if (posterDataUrl) {
                            payload.poster_url = posterDataUrl;
                          } else if (posterChoiceUrl) {
                            payload.poster_url = posterChoiceUrl;
                          } else if (posterCopyPath) {
                            payload.copy_poster = posterCopyPath;
                          }
                          if (metaTitle) payload.title = metaTitle;
                          if (metaYear) payload.year = metaYear;
                          if (metaGenre) payload.genre = metaGenre;
                          if (metaOverview) payload.overview = metaOverview;
                          if (metaCast) payload.cast = metaCast;

                          await apiFetch(`/api/video/update`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                          });
                        }
                        if (onUpdateCache) onUpdateCache();
                        await loadCollections();
                        // Nettoyage
                        setSelectedVideoIds(new Set());
                        // Conserver bulkNewName pour continuer à ajouter si besoin
                        // Ne pas réinitialiser les métadonnées automatiquement pour permettre plusieurs assignations
                      } catch (e) {
                        console.error('Erreur assignation collection:', e);
                        alert('Erreur lors de l\'assignation à la collection');
                      } finally {
                        setBulkProcessing(false);
                      }
                    }}
                    aria-label="Assigner les vidéos sélectionnées à la collection"
                  >
                    {bulkProcessing ? 'Assignation...' : 'Assigner'}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary btn-sm"
                    onClick={() => { setBulkSelected(new Set()); setSelectedVideoIds(new Set()); setBulkNewName(''); }}
                    aria-label="Réinitialiser la sélection"
                  >Réinitialiser</button>
                </div>
              </div>
              <div style={{ maxHeight: '180px', overflowY: 'auto', borderTop: '1px solid #222', paddingTop: '8px' }}>
                <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px', textTransform: 'uppercase' }}>Collections</div>
                {filteredCollections.length === 0 && (
                  <div style={{ color: '#666', fontSize: '14px' }}>Aucune collection trouvée.</div>
                )}
                {filteredCollections.map(name => {
                  const checked = bulkSelected.has(name);
                  return (
                    <label key={name} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 2px', cursor: 'pointer', fontSize: '14px', color: '#ddd' }}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleBulkSelection(name)}
                        style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                        aria-label={`Sélectionner la collection ${name}`}
                      />
                      <span style={{ flex: 1 }}>{name}</span>
                      <span style={{ fontSize: '11px', color: '#888' }}>{collections[name].videos.length} vidéo{collections[name].videos.length > 1 ? 's' : ''}</span>
                    </label>
                  );
                })}
                {/* Actions de fusion de collections sélectionnées */}
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '12px', color: '#888' }}>{bulkSelected.size} sélectionnée{bulkSelected.size > 1 ? 's' : ''}</span>
                  <button
                    type="button"
                    className="btn-primary btn-sm"
                    disabled={!canBulkMerge}
                    onClick={handleBulkMerge}
                    title="Fusionner les collections sélectionnées dans le nom cible"
                    aria-label="Fusionner les collections sélectionnées"
                  >
                    Fusionner →
                  </button>
                  <span style={{ fontSize: '12px', color: '#777' }}>Vers « {bulkNewName || '...'} »</span>
                </div>
                <hr style={{ border: 'none', borderTop: '1px solid #222', margin: '8px 0' }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px', textTransform: 'uppercase' }}>Vidéos {allVideosLoading && '(chargement...)'}</div>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button
                      type="button"
                      className="btn-secondary btn-sm"
                      onClick={() => {
                        const next = new Set(selectedVideoIds);
                        slicedVideos.forEach(v => next.add(v.id));
                        setSelectedVideoIds(next);
                      }}
                    >Sélectionner affichées</button>
                    <button
                      type="button"
                      className="btn-secondary btn-sm"
                      onClick={() => setSelectedVideoIds(new Set())}
                    >Vider sélection</button>
                    <span style={{ fontSize: '12px', color: '#888', alignSelf: 'center' }}>{selectedVideoIds.size} sélectionnée{selectedVideoIds.size > 1 ? 's' : ''}</span>
                  </div>
                </div>
                {!allVideosLoading && filteredVideos.length === 0 && (
                  <div style={{ color: '#666', fontSize: '14px' }}>Aucune vidéo correspondante.</div>
                )}
                {slicedVideos.map(v => {
                  const checked = selectedVideoIds.has(v.id);
                  return (
                    <label key={v.id} style={{ display: 'grid', gridTemplateColumns: '16px 1fr', gap: '8px', alignItems: 'center', padding: '6px 2px', fontSize: '13px', color: '#ccc', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => {
                          setSelectedVideoIds(prev => {
                            const next = new Set(prev);
                            if (next.has(v.id)) next.delete(v.id); else next.add(v.id);
                            return next;
                          });
                        }}
                        style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                        aria-label={`Sélectionner la vidéo ${v.title || v.path}`}
                      />
                      <div style={{ minWidth: 0, display: 'flex', flexDirection: 'column' }}>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline', minWidth: 0 }}>
                          <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{v.title || '(sans titre)'}</span>
                          <span style={{ fontSize: '11px', color: '#9ad' }}>{bytesToHuman(v.size)}</span>
                        </div>
                        <span style={{ fontSize: '11px', color: '#9cf', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{v.path}</span>
                      </div>
                    </label>
                  );
                })}
                {filteredVideos.length > videosShowLimit && (
                  <button
                    type="button"
                    className="btn-secondary btn-sm"
                    onClick={() => setVideosShowLimit(l => l + 200)}
                    style={{ marginTop: '6px' }}
                  >Afficher plus ({slicedVideos.length}/{filteredVideos.length})</button>
                )}
              </div>
              <div style={{ borderTop: '1px solid #222', marginTop: '10px', paddingTop: '10px' }}>
                <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px', textTransform: 'uppercase' }}>Affiche & métadonnées</div>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <div style={{ flex: '0 0 200px' }}>
                    <label htmlFor="poster-input" style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Affiche (image)</label>
                    <input
                      id="poster-input"
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files && e.target.files[0];
                        if (!file) return;
                        const reader = new FileReader();
                        reader.onload = () => {
                          const result = reader.result;
                          if (typeof result === 'string') setPosterDataUrl(result);
                          // Nettoyer les autres choix si on téléverse une image
                          setPosterChoiceUrl("");
                          setPosterCopyPath("");
                        };
                        reader.readAsDataURL(file);
                      }}
                    />
                    {posterDataUrl && (
                      <div style={{ marginTop: '8px' }}>
                        <img src={posterDataUrl} alt="Prévisualisation affiche" style={{ width: '120px', height: 'auto', borderRadius: '6px', border: '1px solid #333' }} />
                        <div>
                          <button type="button" onClick={() => setPosterDataUrl("")} style={{ marginTop: '6px', padding: '4px 8px', background: '#222', color: '#ddd', border: '1px solid #333', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>Retirer l'affiche</button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div style={{ flex: '1 1 280px', minWidth: '260px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Titre</label>
                      <input value={metaTitle} onChange={e => setMetaTitle(e.target.value)} placeholder="Laisser vide pour ne pas modifier" style={{ width: '100%', padding: '8px 10px', background: '#1d1d1d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Année</label>
                      <input type="number" value={metaYear} onChange={e => setMetaYear(e.target.value)} placeholder="ex: 2016" style={{ width: '100%', padding: '8px 10px', background: '#1d1d1d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Genre</label>
                      <input value={metaGenre} onChange={e => setMetaGenre(e.target.value)} placeholder="Action, Drame..." style={{ width: '100%', padding: '8px 10px', background: '#1d1d1d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Casting</label>
                      <input value={metaCast} onChange={e => setMetaCast(e.target.value)} placeholder="Acteur 1, Acteur 2" style={{ width: '100%', padding: '8px 10px', background: '#1d1d1d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
                    </div>
                    <div style={{ gridColumn: '1 / span 2' }}>
                      <label style={{ display: 'block', fontSize: '12px', color: '#bbb', marginBottom: '4px' }}>Synopsis</label>
                      <textarea value={metaOverview} onChange={e => setMetaOverview(e.target.value)} placeholder="Résumé..." rows={3} style={{ width: '100%', padding: '8px 10px', background: '#1d1d1d', color: '#fff', border: '1px solid #444', borderRadius: '4px', resize: 'vertical' }} />
                    </div>
                  </div>
                </div>
                {/* Propositions d'affiches liées à la recherche */}
                <div style={{ marginTop: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '6px' }}>
                    <div style={{ fontSize: '12px', color: '#888', textTransform: 'uppercase' }}>Affiches proposées</div>
                    {posterSuggestLoading && <span style={{ fontSize: '12px', color: '#666' }}>(recherche...)</span>}
                    {!posterSuggestLoading && posterSuggestions.length > 0 && (
                      <span style={{ fontSize: '12px', color: '#666' }}>({posterSuggestions.length})</span>
                    )}
                  </div>
                  {posterSuggestions.length === 0 && !posterSuggestLoading && (
                    <div style={{ fontSize: '12px', color: '#666' }}>Aucune affiche proposée pour "{bulkSearch}". Essayez un autre mot-clé.</div>
                  )}
                  {posterSuggestions.length > 0 && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '10px' }}>
                      {posterSuggestions.map(s => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => {
                            setPosterDataUrl("");
                            if (s.mode === 'copy') { setPosterCopyPath(s.copyPath); setPosterChoiceUrl(""); }
                            else { setPosterChoiceUrl(s.url); setPosterCopyPath(""); }
                          }}
                          title={`Utiliser cette affiche (${s.source})`}
                          style={{
                            display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'center',
                            background: '#1c1c1c', border: '1px solid #333', borderRadius: '8px', padding: '8px', cursor: 'pointer'
                          }}
                        >
                          <img src={s.previewUrl} alt={s.label} style={{ width: '100%', height: 'auto', borderRadius: '4px' }} />
                          <span style={{ fontSize: '11px', color: '#bbb', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', width: '100%' }}>{s.label}</span>
                          <span style={{ fontSize: '10px', color: '#666' }}>{s.source === 'recent' ? 'Affiche locale' : 'Depuis vidéo'}</span>
                        </button>
                      ))}
                    </div>
                  )}
                  {(posterChoiceUrl || posterCopyPath) && (
                    <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#bbb' }}>Affiche sélectionnée:</span>
                      {posterChoiceUrl && <img src={posterChoiceUrl} alt="Affiche choisie" style={{ height: '40px', borderRadius: '4px', border: '1px solid #333' }} />}
                      {!posterChoiceUrl && posterCopyPath && <span style={{ fontSize: '12px', color: '#8ad' }}>{posterCopyPath}</span>}
                      <button type="button" onClick={() => { setPosterChoiceUrl(""); setPosterCopyPath(""); }} style={{ padding: '4px 8px', background: '#222', color: '#ddd', border: '1px solid #333', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>Retirer</button>
                    </div>
                  )}
                </div>
                <p style={{ marginTop: '6px', fontSize: '12px', color: '#777' }}>Les champs remplis seront appliqués et écraseront les métadonnées existantes des vidéos sélectionnées. L'affiche personnalisée remplacera l'affiche actuelle.</p>
              </div>
              <p style={{ marginTop: '8px', fontSize: '12px', color: '#777' }}>
                Sélectionnez une ou plusieurs vidéos dans la liste puis choisissez une collection existante ou tapez un nom pour en créer une et validez avec « Assigner ».
              </p>
            </div>
          )}

          {loading ? (
            <div className="modal-loading">Chargement...</div>
          ) : (
            <div className="modal-scrollable" ref={scrollRef}>
              {collectionNames.length === 0 && standalone.length === 0 ? (
                <div className="modal-empty">Aucune collection détectée</div>
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
                                type="button"
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
                                aria-label="Valider le renommage"
                              >
                                OK
                              </button>
                              <button
                                type="button"
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
                                aria-label="Annuler le renommage"
                              >
                                ✕
                              </button>
                            </div>
                          ) : (
                            <>
                              <div 
                                onClick={(e) => {
                                  // Si on clique sur le titre, ouvrir le mode renommage
                                  const target = e.target;
                                  if (target.tagName === 'H3' || target.closest('h3')) {
                                    e.stopPropagation();
                                    setEditingCollection(collectionName);
                                    setNewCollectionName(collectionName);
                                  } else {
                                    // Sinon ouvrir la saga
                                    setSelectedCollection(collectionName);
                                  }
                                }}
                                style={{ flex: 1, cursor: 'pointer', minWidth: 0 }}
                              >
                                <h3 className="collection-card-title" title="Cliquer pour renommer">{collectionName}</h3>
                                <div className="collection-card-count">
                                  {videos.length} vidéo{videos.length > 1 ? 's' : ''}
                                </div>
                              </div>
                              <div className="collection-card-tools">
                                <button
                                  type="button"
                                  className="btn-icon btn-glass btn-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (scrollRef.current) scrollRef.current.scrollTop = 0;
                                    setBulkEditOpen(true);
                                    setBulkSearch(collectionName);
                                    setTimeout(() => { try { bulkSearchInputRef.current && bulkSearchInputRef.current.focus(); } catch {} }, 0);
                                  }}
                                  title={`Ouvrir l'édition avec la recherche « ${collectionName} »`}
                                  aria-label={`Éditer avec recherche ${collectionName}`}
                                >
                                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                                    <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                                  </svg>
                                </button>
                                <button
                                  type="button"
                                  className="btn-icon btn-glass btn-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteCollection(collectionName);
                                  }}
                                  title="Supprimer la collection"
                                  aria-label="Supprimer la collection"
                                  style={{ color: '#ff6666' }}
                                >
                                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                                    <path d="M6 19a2 2 0 002 2h8a2 2 0 002-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                                  </svg>
                                </button>
                              </div>
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
                          {standalone.length} vidéo{standalone.length > 1 ? 's' : ''}
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
            <button className="modal-back-button" onClick={() => setSelectedCollection(null)} aria-label="Retour aux collections">
              ← Retour
            </button>
            <h2 className="modal-title">
              {selectedCollection === "standalone" ? "Films autonomes" : selectedCollection} ({videos.length})
            </h2>
          </div>
          <button className="modal-close-button" onClick={onClose} aria-label="Fermer le modal">
            <span aria-hidden="true">×</span>
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


