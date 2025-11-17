import { useState, useEffect } from "react";
import { apiFetch } from "./config.js";

export default function PasswordPrompt({ profile, onSuccess, onCancel }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [answer, setAnswer] = useState("");
  const [securityQuestion, setSecurityQuestion] = useState("");

  // Bloquer le scroll de la page principale quand le modal est ouvert
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    // Charger la question secrète au montage
    if (profile?.id) {
      fetchSecurityQuestion();
    }
  }, [profile]);

  async function fetchSecurityQuestion() {
    try {
      const response = await apiFetch(`/api/profiles/${profile.id}/security-question`);
      const data = await response.json();
      if (data.ok && data.question) {
        setSecurityQuestion(data.question);
      }
    } catch (error) {
      console.error("Erreur chargement question:", error);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await apiFetch("/api/profiles/verify-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profile.id,
          password: password,
        }),
      });

      const data = await response.json();

      if (data.ok && data.valid) {
        onSuccess();
      } else {
        setError("Mot de passe incorrect");
      }
    } catch (err) {
      console.error("Erreur vérification mot de passe:", err);
      setError("Erreur lors de la vérification");
    } finally {
      setLoading(false);
    }
  }

  async function handleResetPassword(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await apiFetch("/api/profiles/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profile.id,
          security_answer: answer,
        }),
      });

      const data = await response.json();

      if (data.ok) {
        // La réponse est maintenant le nouveau mot de passe
        alert("Votre nouveau mot de passe est votre réponse à la question secrète");
        onSuccess();
      } else {
        setError(data.message || "Erreur lors de la réinitialisation");
      }
    } catch (err) {
      console.error("Erreur réinitialisation:", err);
      setError("Erreur lors de la réinitialisation");
    } finally {
      setLoading(false);
    }
  }

  if (!securityQuestion) {
    return (
      <div className="password-prompt-overlay">
        <div className="password-prompt-container">
          <div className="password-prompt-header">
            <h2 className="password-prompt-title">Chargement...</h2>
          </div>
        </div>
      </div>
    );
  }

  if (showForgot) {
    return (
      <div className="password-prompt-overlay">
        <div className="password-prompt-container">
          <div className="password-prompt-header">
            <h2 className="password-prompt-title">Réinitialiser le mot de passe</h2>
            <p className="password-prompt-subtitle">Profil: {profile.name}</p>
          </div>

          <form onSubmit={handleResetPassword} className="password-prompt-content">
            {error && <div className="password-prompt-error">{error}</div>}

            <div className="password-prompt-question">
              {securityQuestion}
            </div>

            <div className="password-prompt-field">
              <label className="password-prompt-label">
                Votre réponse (deviendra votre nouveau mot de passe)
              </label>
              <input
                type="text"
                className="password-prompt-input"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Tapez votre réponse..."
                autoFocus
                disabled={loading}
              />
              <small style={{ color: "rgba(255,255,255,0.6)", marginTop: "5px", display: "block" }}>
                💡 Cette réponse deviendra votre nouveau mot de passe
              </small>
            </div>

            <div className="password-prompt-actions">
              <button
                type="button"
                className="password-prompt-btn password-prompt-btn-secondary"
                onClick={() => setShowForgot(false)}
                disabled={loading}
              >
                Retour
              </button>
              <button
                type="submit"
                className="password-prompt-btn password-prompt-btn-primary"
                disabled={loading || !answer.trim()}
              >
                {loading ? "Réinitialisation..." : "Réinitialiser"}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="password-prompt-overlay">
      <div className="password-prompt-container">
        <div className="password-prompt-header">
          <h2 className="password-prompt-title">Entrez le mot de passe</h2>
          <p className="password-prompt-subtitle">Profil: {profile.name}</p>
        </div>

        <form onSubmit={handleSubmit} className="password-prompt-content">
          {error && <div className="password-prompt-error">{error}</div>}

          <div className="password-prompt-field">
            <label className="password-prompt-label">Mot de passe</label>
            <input
              type="password"
              className="password-prompt-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Entrez votre mot de passe..."
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="password-prompt-actions">
            <button
              type="button"
              className="password-prompt-btn password-prompt-btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="password-prompt-btn password-prompt-btn-primary"
              disabled={loading || !password}
            >
              {loading ? "Vérification..." : "Valider"}
            </button>
          </div>

          <div className="password-prompt-forgot">
            <a
              className="password-prompt-forgot-link"
              onClick={() => setShowForgot(true)}
            >
              Mot de passe oublié ?
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}

