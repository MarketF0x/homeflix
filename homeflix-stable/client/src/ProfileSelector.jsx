import { useState, useEffect } from "react";
import ProfileManager from "./ProfileManager";
import PasswordPrompt from "./PasswordPrompt";
import { apiFetch, getApiUrl } from "./config";

const AVAILABLE_AVATARS = [
  "avatar_01.svg",
  "avatar_02.svg",
  "avatar_03.svg",
  "avatar_04.svg",
  "avatar_05.svg",
  "avatar_06.svg",
  "abstract_01.svg",
  "abstract_02.svg",
  "abstract_03.svg",
  "abstract_04.svg",
  "abstract_05.svg",
  "abstract_06.svg",
];

// Helper pour obtenir l'URL correcte de l'avatar
function getAvatarUrl(avatar) {
  if (avatar.startsWith("custom_avatars/")) {
    return getApiUrl(`/api/${avatar}`);
  }
  return getApiUrl(`/avatars/${avatar}`);
}

export default function ProfileSelector({ onSelectProfile }) {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showManager, setShowManager] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [pendingProfile, setPendingProfile] = useState(null);
  
  // Animation de démarrage : UNIQUEMENT au premier lancement de la session
  const [showCinemaIntro, setShowCinemaIntro] = useState(() => {
    // Vérifier si l'animation a déjà été jouée dans cette session
    const hasPlayed = sessionStorage.getItem('homeflix_intro_played');
    return !hasPlayed; // true si jamais joué, false sinon
  });

  // Bloquer le scroll de la page principale
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  // Gestion du bouton retour pour fermer le gestionnaire de profils
  useEffect(() => {
    if (!showManager && !pendingProfile) return; // Pas d'historique si pas de modal ouverte

    const handlePopState = (e) => {
      e.preventDefault();
      console.log("🔙 Bouton retour - Fermeture ProfileManager/PasswordPrompt");
      
      if (pendingProfile) {
        setPendingProfile(null);
      } else if (showManager) {
        setShowManager(false);
        setEditingProfile(null);
      }
    };

    window.history.pushState({ profileModal: true }, "", "");
    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [showManager, pendingProfile]);

  useEffect(() => {
    loadProfiles();
    
    // Si l'animation est affichée, la masquer après 4 secondes et marquer comme jouée
    if (showCinemaIntro) {
      const timer = setTimeout(() => {
        setShowCinemaIntro(false);
        sessionStorage.setItem('homeflix_intro_played', 'true');
      }, 4000);
      
      return () => clearTimeout(timer);
    }
  }, [showCinemaIntro]);

  async function loadProfiles() {
    try {
      setLoading(true);
      const response = await apiFetch("/api/profiles");
      const data = await response.json();
      
      if (data.ok) {
        setProfiles(data.profiles);
      }
    } catch (error) {
      console.error("Erreur chargement profils:", error);
    } finally {
      setLoading(false);
    }
  }

  function handleSelectProfile(profile) {
    // Si le profil a un mot de passe, demander la saisie
    if (profile.has_password) {
      setPendingProfile(profile);
    } else {
      onSelectProfile(profile);
    }
  }

  function handlePasswordSuccess() {
    if (pendingProfile) {
      onSelectProfile(pendingProfile);
      setPendingProfile(null);
    }
  }

  function handlePasswordCancel() {
    setPendingProfile(null);
  }

  function handleManageProfiles() {
    setShowManager(true);
  }

  function handleCloseManager() {
    setShowManager(false);
    setEditingProfile(null);
    loadProfiles();
  }

  if (pendingProfile) {
    return (
      <PasswordPrompt
        profile={pendingProfile}
        onSuccess={handlePasswordSuccess}
        onCancel={handlePasswordCancel}
      />
    );
  }

  if (showManager) {
    return (
      <ProfileManager
        profiles={profiles}
        availableAvatars={AVAILABLE_AVATARS}
        onClose={handleCloseManager}
      />
    );
  }

  return (
    <div className="profile-selector-overlay">
      {/* Animation cinéma au démarrage */}
      {showCinemaIntro && (
        <div className="cinema-intro">
          <div className="cinema-curtain cinema-curtain-left"></div>
          <div className="cinema-curtain cinema-curtain-right"></div>
          <div className="cinema-spotlight"></div>
          <div className="cinema-film-strip cinema-film-strip-left"></div>
          <div className="cinema-film-strip cinema-film-strip-right"></div>
          <div className="cinema-logo">
            <div className="cinema-logo-text">HOMEFLIX</div>
            <div className="cinema-logo-tagline">Votre cinéma personnel</div>
          </div>
        </div>
      )}

      <div className="profile-selector-container">
        <div className="profile-selector-header">
          <h1 className="profile-selector-title">Qui regarde ?</h1>
          <p className="profile-selector-subtitle">Sélectionnez un profil pour continuer</p>
        </div>

        {loading ? (
          <div className="profile-selector-loading">Chargement des profils...</div>
        ) : (
          <>
            <div className="profile-selector-grid">
              {profiles.map((profile) => (
                <div
                  key={profile.id}
                  className="profile-card"
                  onClick={() => handleSelectProfile(profile)}
                >
                  <div className="profile-card-avatar-wrapper">
                    <img
                      src={getAvatarUrl(profile.avatar)}
                      alt={profile.name}
                      className="profile-card-avatar"
                    />
                    {profile.has_password && (
                      <div className="profile-card-lock-icon">🔒</div>
                    )}
                  </div>
                  <div className="profile-card-name">{profile.name}</div>
                  {profile.is_main && (
                    <div className="profile-card-badge">Principal</div>
                  )}
                </div>
              ))}

              {/* Carte d'ajout de profil */}
              <div
                className="profile-card profile-card-add"
                onClick={handleManageProfiles}
              >
                <div className="profile-card-avatar-wrapper">
                  <div className="profile-card-avatar profile-add-icon">+</div>
                </div>
                <div className="profile-card-name">Ajouter un profil</div>
              </div>
            </div>

            {/* Bouton de gestion */}
            <div className="profile-selector-footer">
              <button
                className="profile-selector-manage-btn"
                onClick={handleManageProfiles}
              >
                ⚙️ Gérer les profils
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

