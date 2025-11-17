import { useState, useEffect } from "react";
import { useI18n } from "./i18n.jsx";
import FolderBrowser from "./FolderBrowser.jsx";
import "./SettingsModal.css";
import { apiFetch } from "./config.js";

export default function SettingsModal({ onClose }) {
  const { language, setLanguage, t } = useI18n();
  const [directories, setDirectories] = useState([]);
  const [tmdbKey, setTmdbKey] = useState("");
  const [autoClean, setAutoClean] = useState(true);
  const [minFilm, setMinFilm] = useState(75);
  const [maxSeries, setMaxSeries] = useState(55);
  const [duplicates, setDuplicates] = useState(null);
  const [loadingDuplicates, setLoadingDuplicates] = useState(false);
  const [selectedForDeletion, setSelectedForDeletion] = useState([]);
  const [showFolderBrowser, setShowFolderBrowser] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [enrichStats, setEnrichStats] = useState(null);
  const [autoDetecting, setAutoDetecting] = useState(false);
  const [scanning, setScanning] = useState(false);

  const languages = [
    { code: "fr", name: "Français" },
    { code: "en", name: "English" },
    { code: "de", name: "Deutsch" },
    { code: "es", name: "Español" },
  ];

  // Charger les paramètres au montage
  useEffect(() => {
    async function loadSettings() {
      try {
        const response = await apiFetch("/api/settings");
        const data = await response.json();
        setDirectories(data.video_directories || []);
        setTmdbKey(data.tmdb_api_key || "");
        setAutoClean(data.auto_clean_filenames ?? true);
        setMinFilm(data.min_film_minutes || 75);
        setMaxSeries(data.max_series_minutes || 55);
      } catch (error) {
        console.error("Erreur chargement settings:", error);
      }
    }
    loadSettings();
  }, []);

  // Bloquer le scroll de la page principale quand le modal est ouvert
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
      onClose();
    };
    window.history.pushState({ settingsModal: true }, "", "");
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [onClose]);

  function addDirectory() {
    // Temporairement: utiliser prompt en attendant que FolderBrowser soit testé
    const newDir = prompt(t("settings.add_directory"));
    if (newDir && newDir.trim()) {
      setDirectories([...directories, newDir.trim()]);
    }
    // Pour activer FolderBrowser plus tard:
    // setShowFolderBrowser(true);
  }

  function handleFolderSelected(folderPath) {
    setDirectories([...directories, folderPath]);
    setShowFolderBrowser(false);
  }

  function removeDirectory(index) {
    setDirectories(directories.filter((_, i) => i !== index));
  }

  async function handleSave() {
    try {
      const response = await apiFetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language,
          video_directories: directories,
          tmdb_api_key: tmdbKey,
          auto_clean_filenames: autoClean,
          min_film_minutes: minFilm,
          max_series_minutes: maxSeries,
        }),
      });

      if (response.ok) {
        alert("✅ " + t("settings.save"));
        onClose();
      } else {
        alert("❌ Erreur lors de la sauvegarde");
      }
    } catch (error) {
      console.error(error);
      alert("❌ Erreur de connexion au serveur");
    }
  }

  async function enrichMetadata(force = false) {
    setEnriching(true);
    setEnrichStats(null);
    try {
      const response = await apiFetch(`/api/metadata/enrich?force=${force}`, {
        method: "POST",
      });
      const data = await response.json();
      
      if (data.ok) {
        setEnrichStats(data);
        alert(`✅ Enrichissement terminé !\n\n` +
              `• ${data.updated} vidéos enrichies\n` +
              `• ${data.skipped} déjà à jour\n` +
              `• ${data.failed} échecs\n` +
              `• Total: ${data.total} vidéos`);
      } else {
        alert("❌ Erreur lors de l'enrichissement");
      }
    } catch (error) {
      console.error("Erreur lors de l'enrichissement:", error);
      alert("❌ Erreur de connexion au serveur");
    } finally {
      setEnriching(false);
    }
  }

  async function triggerManualScan() {
    setScanning(true);
    try {
      const response = await apiFetch("/api/scan", {
        method: "POST",
      });
      const data = await response.json();
      
      if (data.ok) {
        alert(`✅ Scan terminé !\n\n` +
              `• ${data.indexed} vidéos ajoutées\n` +
              `• ${data.removed} vidéos supprimées\n` +
              `• ${data.total} total dans la bibliothèque\n\n` +
              `Les métadonnées et miniatures sont en cours de génération...`);
      } else {
        alert("❌ Erreur lors du scan");
      }
    } catch (error) {
      console.error("Erreur lors du scan:", error);
      alert("❌ Erreur de connexion au serveur");
    } finally {
      setScanning(false);
    }
  }

  async function scanDuplicates() {
    setLoadingDuplicates(true);
    try {
      const response = await apiFetch("/api/duplicates");
      const data = await response.json();
      setDuplicates(data);
      setSelectedForDeletion([]);
    } catch (error) {
      console.error("Erreur lors du scan des doublons:", error);
      alert("❌ Erreur lors du scan des doublons");
    } finally {
      setLoadingDuplicates(false);
    }
  }

  async function autoDetectDirectories() {
    setAutoDetecting(true);
    try {
      const response = await apiFetch("/api/detect-video-directories", {
        method: "POST"
      });
      const data = await response.json();
      
      if (data.ok && data.directories) {
        setDirectories(data.directories);
        alert(`✅ ${data.message}\n\n${data.directories.join('\n')}`);
      } else {
        alert(`⚠️ ${data.message || 'Aucun répertoire vidéo détecté'}`);
      }
    } catch (error) {
      console.error("Erreur lors de la détection automatique:", error);
      alert("❌ Erreur lors de la détection automatique des répertoires");
    } finally {
      setAutoDetecting(false);
    }
  }

  function toggleFileSelection(filePath) {
    setSelectedForDeletion(prev => 
      prev.includes(filePath) 
        ? prev.filter(p => p !== filePath)
        : [...prev, filePath]
    );
  }

  async function deleteDuplicates() {
    if (selectedForDeletion.length === 0) {
      alert("⚠️ Aucun fichier sélectionné");
      return;
    }

    if (!confirm(`Voulez-vous vraiment supprimer définitivement ${selectedForDeletion.length} fichier(s) ?`)) {
      return;
    }

    try {
      const response = await apiFetch("/api/duplicates/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_paths: selectedForDeletion }),
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.deleted_count} fichier(s) supprimé(s)`);
        // Relancer le scan pour actualiser
        scanDuplicates();
      } else {
        alert("❌ Erreur lors de la suppression");
      }
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      alert("❌ Erreur lors de la suppression");
    }
  }

  // Gestionnaire pour fermer la modale quand on clique en dehors
  const handleOutsideClick = (e) => {
    if (e.target.classList.contains('settings-modal-overlay')) {
      onClose();
    }
  };

  return (
    <div className="settings-modal-overlay" onClick={handleOutsideClick}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>{t("settings.title")}</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="settings-content">
          {/* Langue */}
          <div className="setting-group">
            <label>{t("settings.language")}</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="setting-select"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Répertoires vidéo */}
          <div className="setting-group">
            <label>{t("settings.video_directories")}</label>
            <div className="directories-list">
              {directories.map((dir, index) => (
                <div key={index} className="directory-item">
                  <span>{dir}</span>
                  <button
                    className="remove-btn"
                    onClick={() => removeDirectory(index)}
                  >
                    {t("settings.remove")}
                  </button>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <button className="add-btn" onClick={addDirectory}>
                + {t("settings.add_directory")}
              </button>
              <button 
                className="scan-duplicates-btn" 
                onClick={autoDetectDirectories}
                disabled={autoDetecting}
                title="Détecter automatiquement les répertoires contenant des vidéos"
              >
                {autoDetecting ? "🔍 Détection..." : "🔍 Détection automatique"}
              </button>
            </div>
          </div>

          {/* Clé API TMDb */}
          <div className="setting-group">
            <label>{t("settings.tmdb_api_key")}</label>
            <input
              type="text"
              value={tmdbKey}
              onChange={(e) => setTmdbKey(e.target.value)}
              className="setting-input"
              placeholder="ea6fc0ab5f79a1f46933be60a01e0a17"
            />
            <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
              <button 
                className="scan-duplicates-btn" 
                onClick={() => enrichMetadata(false)}
                disabled={enriching || !tmdbKey}
                title="Enrichir seulement les vidéos sans métadonnées"
              >
                {enriching ? "⏳ Enrichissement..." : "🎬 Enrichir les métadonnées"}
              </button>
              <button 
                className="scan-duplicates-btn" 
                onClick={() => enrichMetadata(true)}
                disabled={enriching || !tmdbKey}
                style={{ background: '#ff6b35' }}
                title="Forcer l'enrichissement de TOUTES les vidéos"
              >
                {enriching ? "⏳ Enrichissement..." : "🔄 Tout réenrichir"}
              </button>
            </div>
            {enrichStats && (
              <div style={{ 
                marginTop: '10px', 
                padding: '10px', 
                background: 'rgba(76, 175, 80, 0.1)',
                borderRadius: '5px',
                fontSize: '0.9em'
              }}>
                <strong>✅ Derniers résultats :</strong><br/>
                • {enrichStats.updated} enrichies | {enrichStats.skipped} déjà à jour | {enrichStats.failed} échecs
              </div>
            )}
            <p style={{ fontSize: '0.85em', color: '#888', marginTop: '8px' }}>
              💡 L'enrichissement récupère : titre officiel, affiche HD, résumé, genres, note
            </p>
          </div>

          {/* Nettoyage auto */}
          <div className="setting-group">
            <label>
              <input
                type="checkbox"
                checked={autoClean}
                onChange={(e) => setAutoClean(e.target.checked)}
              />
              {t("settings.auto_clean")}
            </label>
          </div>

          {/* Scan manuel */}
          <div className="setting-group">
            <label>📂 Scan manuel de la bibliothèque</label>
            <button 
              className="scan-duplicates-btn" 
              onClick={triggerManualScan}
              disabled={scanning}
              title="Rechercher immédiatement de nouvelles vidéos dans les répertoires configurés"
            >
              {scanning ? "🔄 Scan en cours..." : "🔍 Scanner maintenant"}
            </button>
            <p style={{ fontSize: '0.85em', color: '#888', marginTop: '8px' }}>
              💡 Le scan automatique s'effectue toutes les 24 heures. Utilisez ce bouton pour forcer une recherche immédiate.
            </p>
          </div>

          {/* Durées */}
          <div className="setting-group">
            <label>{t("settings.min_film_duration")}</label>
            <input
              type="number"
              value={minFilm}
              onChange={(e) => setMinFilm(parseInt(e.target.value))}
              className="setting-input"
              min="1"
            />
          </div>

          <div className="setting-group">
            <label>{t("settings.max_series_duration")}</label>
            <input
              type="number"
              value={maxSeries}
              onChange={(e) => setMaxSeries(parseInt(e.target.value))}
              className="setting-input"
              min="1"
            />
          </div>

          {/* Gestion des doublons */}
          <div className="setting-group duplicates-section">
            <label>🔍 Gestion des fichiers en doublon</label>
            <button 
              className="scan-duplicates-btn" 
              onClick={scanDuplicates}
              disabled={loadingDuplicates}
            >
              {loadingDuplicates ? "Scan en cours..." : "Scanner les doublons"}
            </button>

            {duplicates && (
              <div className="duplicates-results">
                <p className="duplicates-summary">
                  {duplicates.total_groups > 0 
                    ? `${duplicates.total_groups} groupe(s) de doublons trouvés (${duplicates.total_files} fichiers)`
                    : "✅ Aucun doublon détecté"
                  }
                </p>

                {duplicates.total_groups > 0 && (
                  <>
                    <div className="duplicates-list">
                      {Object.entries(duplicates.duplicates).map(([title, files]) => (
                        <div key={title} className="duplicate-group">
                          <h4 className="duplicate-title">{files[0].title || title}</h4>
                          <div className="duplicate-files">
                            {files.map((file, idx) => (
                              <div key={file.id} className="duplicate-file">
                                <input
                                  type="checkbox"
                                  checked={selectedForDeletion.includes(file.path)}
                                  onChange={() => toggleFileSelection(file.path)}
                                />
                                <div className="file-info">
                                  <span className="file-name">{file.file_name}</span>
                                  <span className="file-details">
                                    {(file.file_size / (1024 * 1024)).toFixed(2)} MB
                                    {file.resolution && ` • ${file.resolution}`}
                                    {file.duration && ` • ${Math.floor(file.duration / 60)}min`}
                                  </span>
                                  <span className="file-path">{file.path}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>

                    {selectedForDeletion.length > 0 && (
                      <button 
                        className="delete-duplicates-btn"
                        onClick={deleteDuplicates}
                      >
                        🗑️ Supprimer définitivement ({selectedForDeletion.length} fichier(s))
                      </button>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="settings-footer">
          <button className="cancel-btn" onClick={onClose}>
            {t("settings.cancel")}
          </button>
          <button className="save-btn" onClick={handleSave}>
            {t("settings.save")}
          </button>
        </div>
      </div>

      {/* Explorateur de dossiers */}
      {showFolderBrowser && (
        <FolderBrowser
          onSelect={handleFolderSelected}
          onClose={() => setShowFolderBrowser(false)}
        />
      )}
    </div>
  );
}

