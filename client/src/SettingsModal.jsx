import { useState } from "react";
import { useI18n } from "./i18n.jsx";
import "./SettingsModal.css";

export default function SettingsModal({ onClose }) {
  const { language, setLanguage, t } = useI18n();
  const [directories, setDirectories] = useState([]);
  const [tmdbKey, setTmdbKey] = useState("");
  const [autoClean, setAutoClean] = useState(true);
  const [minFilm, setMinFilm] = useState(75);
  const [maxSeries, setMaxSeries] = useState(55);

  const languages = [
    { code: "fr", name: "Français" },
    { code: "en", name: "English" },
    { code: "de", name: "Deutsch" },
    { code: "es", name: "Español" },
  ];

  function addDirectory() {
    const newDir = prompt(t("settings.add_directory"));
    if (newDir && newDir.trim()) {
      setDirectories([...directories, newDir.trim()]);
    }
  }

  function removeDirectory(index) {
    setDirectories(directories.filter((_, i) => i !== index));
  }

  async function handleSave() {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/settings", {
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
            <button className="add-btn" onClick={addDirectory}>
              + {t("settings.add_directory")}
            </button>
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
    </div>
  );
}
