const API = "http://127.0.0.1:8000/api";

export async function fetchVideos(mode = "mixed") {
  const res = await fetch(`${API}/videos?mode=${mode}`);
  if (!res.ok) throw new Error("Erreur lors du chargement des vidéos");
  return res.json();
}

export async function fetchCategories(mode = "mixed") {
  const res = await fetch(`${API}/categories?mode=${mode}`);
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
  if (!res.ok) throw new Error("Erreur lors de la mise à jour");
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
