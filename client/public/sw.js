// ============================================
// SERVICE WORKER OPTIMISÉ - Homeflix v2.5
// Stratégies de cache professionnelles
// ============================================

const CACHE_VERSION = 'homeflix-v2.5.0';
const STATIC_CACHE = CACHE_VERSION + '-static';
const DYNAMIC_CACHE = CACHE_VERSION + '-dynamic';
const IMAGE_CACHE = CACHE_VERSION + '-images';
const API_CACHE = CACHE_VERSION + '-api';

// Durées de cache (en secondes)
const CACHE_DURATIONS = {
  static: 7 * 24 * 60 * 60,    // 7 jours pour les assets statiques
  dynamic: 24 * 60 * 60,        // 1 jour pour les pages
  images: 30 * 24 * 60 * 60,    // 30 jours pour les images
  api: 5 * 60,                  // 5 minutes pour les données API
};

// Fichiers critiques à mettre en cache immédiatement
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] 🚀 Installation version:', CACHE_VERSION);
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(STATIC_FILES))
      .then(() => self.skipWaiting())
      .catch((err) => console.error('[SW] ❌ Erreur installation:', err))
  );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', (event) => {
  console.log('[SW] ✅ Activation du Service Worker');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName.startsWith('homeflix-v') && 
                     cacheName !== STATIC_CACHE && 
                     cacheName !== DYNAMIC_CACHE &&
                     cacheName !== IMAGE_CACHE &&
                     cacheName !== API_CACHE;
            })
            .map((cacheName) => {
              console.log('[SW] 🗑️ Suppression cache obsolète:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => self.clients.claim())
      .catch((err) => console.error('[SW] ❌ Erreur activation:', err))
  );
});

// Stratégies de cache intelligentes
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorer les requêtes non-GET
  if (request.method !== 'GET') {
    return;
  }

  // Stratégie selon le type de ressource
  
  // 1. API - Network First avec cache court
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE, CACHE_DURATIONS.api));
    return;
  }
  
  // 2. Images/Thumbnails - Cache First avec fallback réseau
  if (url.pathname.includes('/thumbnail') || 
      url.pathname.includes('/poster') ||
      url.pathname.includes('/avatars/') ||
      request.destination === 'image') {
    event.respondWith(cacheFirstStrategy(request, IMAGE_CACHE, CACHE_DURATIONS.images));
    return;
  }
  
  // 3. Assets statiques (JS, CSS) - Cache First
  if (url.pathname.includes('/assets/') || 
      request.destination === 'style' || 
      request.destination === 'script') {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE, CACHE_DURATIONS.static));
    return;
  }
  
  // 4. Pages HTML - Network First
  if (request.destination === 'document') {
    event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE, CACHE_DURATIONS.dynamic));
    return;
  }
  
  // 5. Autres ressources - Network only
  event.respondWith(fetch(request));
});

// Stratégie: Cache First (pour images et assets statiques)
async function cacheFirstStrategy(request, cacheName, maxAge) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Vérifier si le cache n'est pas expiré
      const cachedDate = new Date(cachedResponse.headers.get('date'));
      const now = new Date();
      const age = (now - cachedDate) / 1000; // âge en secondes
      
      if (age < maxAge) {
        console.log('[SW] 💾 Cache hit:', request.url.substring(0, 80));
        return cachedResponse;
      }
    }
    
    // Cache expiré ou inexistant - récupérer du réseau
    const networkResponse = await fetch(request);
    
    // Mettre en cache la nouvelle réponse
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Si erreur réseau, utiliser le cache même expiré
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] 🔄 Fallback cache:', request.url.substring(0, 80));
      return cachedResponse;
    }
    throw error;
  }
}

// Stratégie: Network First (pour API et pages)
async function networkFirstStrategy(request, cacheName, maxAge) {
  try {
    const networkResponse = await fetch(request);
    
    // Mettre en cache les réponses réussies
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Si erreur réseau, utiliser le cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] 🔄 Fallback réseau -> cache:', request.url.substring(0, 80));
      return cachedResponse;
    }
    
    // Pas de cache disponible, retourner page d'erreur
    if (request.destination === 'document') {
      const fallback = await caches.match('/index.html');
      if (fallback) return fallback;
    }
    
    throw error;
  }
}

// Écouter les messages pour contrôle manuel
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[SW] ⏭️ Skip waiting demandé');
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    console.log('[SW] 🗑️ Nettoyage total du cache demandé');
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});
