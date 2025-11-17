/**
 * Configuration centralisée de l'API
 * Détecte automatiquement l'environnement (dev, prod, Electron, distant)
 */

/**
 * Détecte l'URL de base de l'API en fonction de l'environnement
 * @returns {string} URL de base de l'API
 */
export function getApiBaseUrl() {
  // Si en mode développement avec Vite, utiliser le proxy
  if (import.meta.env.DEV) {
    return ''; // Les requêtes /api/* sont proxifiées par Vite
  }
  
  // En production/Electron, détecter si on est en local ou distant
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  // Cas Electron / file:// ou hostname vide -> fallback local
  if (protocol === 'file:' || !hostname) {
    return 'http://127.0.0.1:8000';
  }
  
  // Si localhost ou 127.0.0.1, utiliser le serveur local
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://127.0.0.1:8000';
  }
  
  // Si accès distant, utiliser l'IP actuelle avec le port 8000
  return `http://${hostname}:8000`;
}

/**
 * Construit une URL complète pour l'API
 * @param {string} path - Chemin de l'endpoint (ex: '/api/profiles')
 * @returns {string} URL complète
 */
export function getApiUrl(path) {
  const baseUrl = getApiBaseUrl();
  // Assurer que le path commence par /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

/**
 * Effectue une requête fetch avec l'URL de base correcte
 * @param {string} path - Chemin de l'endpoint
 * @param {object} options - Options fetch
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
  const url = getApiUrl(path);
  return fetch(url, options);
}

// ============================================
// API ENDPOINTS - Fonctions métier
// ============================================

export const API = getApiUrl('/api');

// Log pour diagnostic (uniquement en dev)
if (import.meta.env.DEV) {
  console.log('🌐 API URL configurée:', API);
  console.log('🌐 Hostname:', window.location.hostname);
}

export async function fetchVideos(mode = "mixed", profileId = null) {
  let url = `${API}/videos?mode=${mode}`;
  if (profileId !== null) {
    url += `&profile_id=${profileId}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Erreur lors du chargement des vidéos");
  return res.json();
}

export async function fetchCategories(mode = "mixed", profileId = null) {
  let url = `${API}/categories?mode=${mode}`;
  if (profileId !== null) {
    url += `&profile_id=${profileId}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Erreur lors du chargement des catégories");
  return res.json();
}

export async function fetchAllVideos(mode = "mixed") {
  const res = await fetch(`${API}/videos/all?mode=${mode}`);
  if (!res.ok) throw new Error("Erreur lors du chargement de toutes les vidéos");
  return res.json();
}

export async function scan() {
  const res = await fetch(`${API}/scan`, { method: "POST" });
  if (!res.ok) throw new Error("Erreur lors du scan");
  return res.json();
}

export async function openPath(path, videoId = null) {
  const res = await fetch(`${API}/open`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, id: videoId }),
  });
  if (!res.ok) throw new Error("Erreur lors de l'ouverture de la vidéo");
  return res.json();
}

export async function updateVideo(videoId, updates) {
  const res = await fetch(`${API}/video/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: videoId, ...updates }),
  });
  if (!res.ok) {
    const text = await res.text();
    console.error("Erreur serveur:", res.status, text);
    throw new Error(`Erreur lors de la mise à jour: ${res.status}`);
  }
  
  // Vérifier le content-type avant de parser
  const contentType = res.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    const text = await res.text();
    console.error("Réponse non-JSON:", text);
    throw new Error("Le serveur n'a pas retourné de JSON");
  }
  
  return res.json();
}

export async function enrichVideoFromTMDb(videoId) {
  const res = await fetch(`${API}/video/${videoId}/enrich`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Erreur lors de l'enrichissement TMDb");
  return res.json();
}

export async function deleteVideo(videoId, deleteFile = true, profileId = null) {
  let url = `${API}/videos/${videoId}?delete_file=${deleteFile}`;
  if (profileId !== null) {
    url += `&profile_id=${profileId}`;
  }
  const res = await fetch(url, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Erreur lors de la suppression de la vidéo");
  return res.json();
}

export async function getRandomVideo(mode = "mixed") {
  const res = await fetch(`${API}/random?mode=${mode}`);
  if (!res.ok) throw new Error("Aucune vidéo disponible");
  return res.json();
}

export function thumbURL(path) {
  const p = encodeURIComponent(path);
  return `${API}/thumbnail?path=${p}`;
}

export async function generateThumbnails(force = false) {
  const res = await fetch(`${API}/thumbnails/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force }),
  });
  if (!res.ok) throw new Error("Erreur lors de la génération des miniatures");
  return res.json();
}

// Export de l'URL de base pour usage direct si nécessaire
export const API_BASE_URL = getApiBaseUrl();
