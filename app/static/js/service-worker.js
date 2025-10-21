const CACHE_NAME = "gymapp-cache-v3";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/theme_toggle.js",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/static/icons/splash.png"
];

// ✅ INSTALACIÓN DEL SERVICE WORKER
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// ✅ ACTIVACIÓN — limpia versiones viejas
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ✅ FETCH — modo offline
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).catch(() => caches.match("/"));
    })
  );
});
