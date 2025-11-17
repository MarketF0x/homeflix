// API backend - utilise toujours l'origine actuelle
export const API = `http://${window.location.hostname}:8000/api`;

// Log pour diagnostic
console.log('🌐 API URL configurée:', API);
console.log('🌐 Hostname:', window.location.hostname);

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
