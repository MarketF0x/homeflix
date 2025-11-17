import { useState, useEffect } from "react";
import { SECURITY_QUESTIONS } from "./securityQuestions";
import { apiFetch, getApiUrl } from "./config.js";

// Helper pour obtenir l'URL correcte de l'avatar
function getAvatarUrl(avatar) {
  if (avatar.startsWith("custom_avatars/")) {
    return getApiUrl(`/api/${avatar}`);
  }
  return `/avatars/${avatar}`;
}

export default function ProfileManager({ profiles, availableAvatars, onClose }) {
  const [mode, setMode] = useState("list"); // "list", "create", "edit"
  const [editingProfile, setEditingProfile] = useState(null);
  const [name, setName] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState(availableAvatars[0]);
  const [restrictions, setRestrictions] = useState({});
  const [oldPassword, setOldPassword] = useState("");
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState("");
  const [showCustomAvatarInput, setShowCustomAvatarInput] = useState(false);

  // Bloquer le scroll de la page principale quand le modal est ouvert
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  function handleCreate() {
    setMode("create");
    setName("");
    setSelectedAvatar(availableAvatars[0]);
    setRestrictions({});
    setOldPassword("");
    setSecurityQuestion("");
    setSecurityAnswer("");
    setShowCustomAvatarInput(false);
    setAvatarUrl("");
  }

  function handleEdit(profile) {
    setMode("edit");
    setEditingProfile(profile);
    setName(profile.name);
    setSelectedAvatar(profile.avatar);
    setRestrictions(profile.restrictions || {});
    setOldPassword("");
    setSecurityQuestion(profile.security_question || "");
    setSecurityAnswer("");
    setShowCustomAvatarInput(false);
    setAvatarUrl("");
  }

  async function handleUploadAvatarFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingAvatar(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await apiFetch("/api/profiles/upload-avatar", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.ok) {
        setSelectedAvatar(data.avatar);
        setShowCustomAvatarInput(false);
        setAvatarUrl("");
      }
    } catch (error) {
      console.error("Erreur upload avatar:", error);
      alert("Erreur lors de l'upload de l'avatar");
    } finally {
      setUploadingAvatar(false);
    }
  }

  async function handleUploadAvatarUrl() {
    if (!avatarUrl.trim()) return;

    setUploadingAvatar(true);
    try {
      const formData = new FormData();
      formData.append("url", avatarUrl.trim());

      const response = await apiFetch("/api/profiles/upload-avatar", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.ok) {
        setSelectedAvatar(data.avatar);
        setShowCustomAvatarInput(false);
        setAvatarUrl("");
      }
    } catch (error) {
      console.error("Erreur upload avatar depuis URL:", error);
      alert("Erreur lors du téléchargement de l'avatar depuis l'URL");
    } finally {
      setUploadingAvatar(false);
    }
  }

  async function handleDelete(profile) {
    if (!confirm(`Supprimer le profil "${profile.name}" ?`)) {
      return;
    }

    try {
      const response = await apiFetch(`/api/profiles/${profile.id}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.ok) {
        onClose(); // Recharger la liste
      } else {
        alert(data.error || "Erreur lors de la suppression");
      }
    } catch (error) {
      console.error("Erreur suppression profil:", error);
      alert("Erreur lors de la suppression du profil");
    }
  }

  async function handleSave() {
    if (!name.trim()) {
      alert("Veuillez saisir un nom de profil");
      return;
    }

    // Pour le profil principal qui veut changer son mot de passe
    if (editingProfile?.is_main && securityAnswer) {
      if (!securityQuestion) {
        alert("Veuillez choisir une question secrète");
        return;
      }
      if (editingProfile.has_password && !oldPassword) {
        alert("Veuillez entrer votre ancien mot de passe");
        return;
      }
    }

    setSaving(true);

    try {
      const url = mode === "edit"
        ? `/api/profiles/${editingProfile.id}`
        : "/api/profiles";

      const method = mode === "edit" ? "PUT" : "POST";

      const body = {
        name,
        avatar: selectedAvatar,
        restrictions,
      };

      // Pour la modification avec changement de mot de passe
      if (mode === "edit" && editingProfile?.is_main) {
        if (oldPassword) {
          body.old_password = oldPassword;
        }
        if (securityQuestion && securityAnswer) {
          body.security_question = securityQuestion;
          body.security_answer = securityAnswer;
        }
      }

      if (mode === "create") {
        body.is_main = false;
      }

      const response = await apiFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.ok) {
        if (securityAnswer) {
          alert("✅ Votre nouveau mot de passe est votre réponse à la question secrète");
        }
        onClose();
      } else {
        alert(data.error || data.detail || "Erreur lors de la sauvegarde");
      }
    } catch (error) {
      console.error("Erreur sauvegarde profil:", error);
      alert("Erreur lors de la sauvegarde du profil");
    } finally {
      setSaving(false);
    }
  }

  function handleRestrictionChange(key, value) {
    setRestrictions((prev) => ({
      ...prev,
      [key]: value,
    }));
  }

  if (mode === "list") {
    return (
      <div className="profile-manager-overlay">
        <div className="profile-manager-container">
          <div className="profile-manager-header">
            <h2 className="profile-manager-title">Gérer les profils</h2>
            <button className="modal-close-button" onClick={onClose}>
              ✕
            </button>
          </div>

          <div className="profile-manager-content">
            <button
              className="profile-manager-btn profile-manager-btn-primary"
              onClick={handleCreate}
              style={{ marginBottom: "20px", width: "100%" }}
            >
              + Créer un nouveau profil
            </button>

            <div className="profile-manager-list">
              {profiles.map((profile) => (
                <div key={profile.id} className="profile-manager-list-item">
                  <div className="profile-manager-list-item-info">
                    <img
                      src={getAvatarUrl(profile.avatar)}
                      alt={profile.name}
                      className="profile-manager-list-item-avatar"
                    />
                    <div className="profile-manager-list-item-details">
                      <div className="profile-manager-list-item-name">
                        {profile.name}
                        {profile.is_main && (
                          <span className="profile-card-badge" style={{ marginLeft: "10px" }}>
                            Principal
                          </span>
                        )}
                        {profile.has_password && (
                          <span style={{ marginLeft: "10px" }}>🔒</span>
                        )}
                      </div>
                      {Object.keys(profile.restrictions || {}).length > 0 && (
                        <div className="profile-manager-list-item-restrictions">
                          {profile.restrictions.kidsMode && "Mode enfants"}
                          {profile.restrictions.hideAdult && " • Contenu adulte masqué"}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="profile-manager-list-item-actions">
                    <button
                      className="profile-manager-list-item-btn"
                      onClick={() => handleEdit(profile)}
                    >
                      ✏️ Modifier
                    </button>
                    {!profile.is_main && (
                      <button
                        className="profile-manager-list-item-btn profile-manager-list-item-btn-danger"
                        onClick={() => handleDelete(profile)}
                      >
                        🗑️ Supprimer
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="profile-manager-actions" style={{ marginTop: "30px" }}>
              <button
                className="profile-manager-btn profile-manager-btn-secondary"
                onClick={onClose}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Mode création ou édition
  return (
    <div className="profile-manager-overlay">
      <div className="profile-manager-container">
        <div className="profile-manager-header">
          <h2 className="profile-manager-title">
            {mode === "edit" ? "Modifier le profil" : "Créer un profil"}
          </h2>
          <button className="modal-close-button" onClick={() => setMode("list")}>
            ✕
          </button>
        </div>

        <div className="profile-manager-content">
          {/* Sélection du nom */}
          <div className="profile-manager-field">
            <label className="profile-manager-label">Nom du profil</label>
            <input
              type="text"
              className="profile-manager-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Entrez un nom..."
              maxLength={20}
              autoFocus
              disabled={editingProfile?.is_main}
            />
            {editingProfile?.is_main && (
              <small style={{ color: "rgba(255,255,255,0.6)", marginTop: "5px", display: "block" }}>
                Le nom du profil principal ne peut pas être modifié
              </small>
            )}
          </div>

          {/* Sélection de l'avatar */}
          <div className="profile-manager-field">
            <label className="profile-manager-label">Choisir un avatar</label>
            
            {/* Grille d'avatars prédéfinis */}
            <div className="profile-manager-avatar-grid">
              {availableAvatars.map((avatar) => (
                <div
                  key={avatar}
                  className={`profile-manager-avatar-option ${
                    selectedAvatar === avatar ? "selected" : ""
                  }`}
                  onClick={() => setSelectedAvatar(avatar)}
                >
                  <img
                    src={`/avatars/${avatar}`}
                    alt={avatar}
                    className="profile-manager-avatar-img"
                  />
                </div>
              ))}
              
              {/* Afficher l'avatar personnalisé s'il existe */}
              {selectedAvatar.startsWith("custom_avatars/") && (
                <div className="profile-manager-avatar-option selected">
                  <img
                    src={getApiUrl(`/api/${selectedAvatar}`)}
                    alt="Avatar personnalisé"
                    className="profile-manager-avatar-img"
                  />
                </div>
              )}
            </div>

            {/* Bouton pour importer un avatar personnalisé */}
            <div style={{ marginTop: "15px" }}>
              <button
                type="button"
                className="profile-manager-btn profile-manager-btn-secondary"
                onClick={() => setShowCustomAvatarInput(!showCustomAvatarInput)}
                style={{ fontSize: "0.9rem", padding: "8px 16px" }}
              >
                {showCustomAvatarInput ? "❌ Annuler" : "📷 Importer un avatar personnalisé"}
              </button>
            </div>

            {/* Interface d'upload d'avatar personnalisé */}
            {showCustomAvatarInput && (
              <div className="profile-manager-custom-avatar" style={{
                marginTop: "15px",
                padding: "15px",
                backgroundColor: "rgba(255,255,255,0.05)",
                borderRadius: "8px",
                border: "1px solid rgba(255,255,255,0.1)"
              }}>
                <p style={{ marginBottom: "10px", fontSize: "0.9rem", color: "rgba(255,255,255,0.8)" }}>
                  Importez une image depuis votre ordinateur ou depuis une URL. L'image sera automatiquement redimensionnée à 200x200 pixels.
                </p>

                {/* Upload depuis un fichier */}
                <div style={{ marginBottom: "15px" }}>
                  <label className="profile-manager-label" style={{ fontSize: "0.9rem", marginBottom: "8px" }}>
                    📁 Depuis un fichier local
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleUploadAvatarFile}
                    disabled={uploadingAvatar}
                    className="profile-manager-input"
                    style={{ padding: "8px" }}
                  />
                </div>

                {/* Upload depuis une URL */}
                <div>
                  <label className="profile-manager-label" style={{ fontSize: "0.9rem", marginBottom: "8px" }}>
                    🌐 Depuis une URL
                  </label>
                  <div style={{ display: "flex", gap: "10px" }}>
                    <input
                      type="text"
                      className="profile-manager-input"
                      value={avatarUrl}
                      onChange={(e) => setAvatarUrl(e.target.value)}
                      placeholder="https://exemple.com/image.jpg"
                      disabled={uploadingAvatar}
                      style={{ flex: 1 }}
                    />
                    <button
                      type="button"
                      className="profile-manager-btn profile-manager-btn-primary"
                      onClick={handleUploadAvatarUrl}
                      disabled={uploadingAvatar || !avatarUrl.trim()}
                      style={{ padding: "8px 16px", fontSize: "0.9rem" }}
                    >
                      {uploadingAvatar ? "⏳" : "📥"}
                    </button>
                  </div>
                </div>

                {uploadingAvatar && (
                  <p style={{ marginTop: "10px", fontSize: "0.9rem", color: "#4CAF50", textAlign: "center" }}>
                    ⏳ Traitement de l'image en cours...
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Protection par mot de passe (pour profil principal en édition) */}
          {editingProfile?.is_main && (
            <>
              <div className="profile-manager-field" style={{ marginTop: "20px", paddingTop: "20px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
                <label className="profile-manager-label" style={{ fontSize: "1.1rem", fontWeight: "600" }}>
                  🔒 Protection par mot de passe
                </label>
                
                {editingProfile.has_password && (
                  <div className="profile-manager-field">
                    <label className="profile-manager-label">
                      Ancien mot de passe (requis pour modifier)
                    </label>
                    <input
                      type="password"
                      className="profile-manager-input"
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                      placeholder="Entrez votre mot de passe actuel..."
                    />
                  </div>
                )}
                
                <div className="profile-manager-field">
                  <label className="profile-manager-label">
                    Choisissez une question secrète
                  </label>
                  <select
                    className="profile-manager-input"
                    value={securityQuestion}
                    onChange={(e) => setSecurityQuestion(e.target.value)}
                    style={{ cursor: "pointer" }}
                  >
                    <option value="">-- Sélectionner une question --</option>
                    {SECURITY_QUESTIONS.map((question, idx) => (
                      <option key={idx} value={question}>
                        {question}
                      </option>
                    ))}
                  </select>
                </div>

                {securityQuestion && (
                  <div className="profile-manager-field">
                    <label className="profile-manager-label">
                      Votre réponse (deviendra votre mot de passe)
                    </label>
                    <input
                      type="text"
                      className="profile-manager-input"
                      value={securityAnswer}
                      onChange={(e) => setSecurityAnswer(e.target.value)}
                      placeholder="Tapez votre réponse..."
                      autoComplete="off"
                    />
                    <small style={{ color: "rgba(255,255,255,0.6)", marginTop: "8px", display: "block", fontSize: "0.9rem" }}>
                      💡 Cette réponse sera utilisée comme mot de passe. Mémorisez-la bien !
                    </small>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Restrictions (optionnel pour profils secondaires) */}
          {!editingProfile?.is_main && (
            <div className="profile-manager-field">
              <label className="profile-manager-label">Restrictions (optionnel)</label>
              <div className="profile-manager-restrictions">
                <label className="profile-manager-checkbox">
                  <input
                    type="checkbox"
                    checked={restrictions.hideAdult || false}
                    onChange={(e) =>
                      handleRestrictionChange("hideAdult", e.target.checked)
                    }
                  />
                  <span>Masquer le contenu adulte</span>
                </label>
                <label className="profile-manager-checkbox">
                  <input
                    type="checkbox"
                    checked={restrictions.kidsMode || false}
                    onChange={(e) =>
                      handleRestrictionChange("kidsMode", e.target.checked)
                    }
                  />
                  <span>Mode enfants (limiter au contenu tout public)</span>
                </label>
              </div>
            </div>
          )}

          {/* Boutons d'action */}
          <div className="profile-manager-actions">
            <button
              className="profile-manager-btn profile-manager-btn-secondary"
              onClick={() => setMode("list")}
              disabled={saving}
            >
              Annuler
            </button>
            <button
              className="profile-manager-btn profile-manager-btn-primary"
              onClick={handleSave}
              disabled={saving || !name.trim()}
            >
              {saving ? "Enregistrement..." : mode === "edit" ? "Modifier" : "Créer"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

