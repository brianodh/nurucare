const CACHE_NAME = 'NuruCare-v1';
const OFFLINE_FALLBACK = '/offline.html';

// Assets to cache immediately on install
const PRECACHE_URLS = [
  '/',
  '/roles',
  '/female/intake',
  '/education',
  '/male/dashboard',
  '/partner-sync',
  '/offline.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS).catch(() => {
        // Silently fail on assets that aren't available yet
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    ).then(() => self.clients.claim())
  );
});

// Network-first for API calls, cache-first for static assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests except Google Fonts
  if (url.origin !== location.origin && !url.hostname.includes('fonts.googleapis')) return;

  // For navigation requests (HTML pages)
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() =>
        caches.match(request).then((cached) => cached || caches.match(OFFLINE_FALLBACK))
      )
    );
    return;
  }

  // Stale-while-revalidate for static assets
  event.respondWith(
    caches.match(request).then((cached) => {
      const fetchPromise = fetch(request).then((response) => {
        if (response && response.status === 200 && response.type !== 'opaque') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

// Background sync for queued intake submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-intake') {
    event.waitUntil(syncQueuedIntakes());
  }
});

async function syncQueuedIntakes() {
  // Notify clients that sync is happening
  const clients = await self.clients.matchAll();
  clients.forEach((client) => client.postMessage({ type: 'SYNC_START' }));
}
