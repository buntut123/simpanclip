// Service worker minimal: syarat agar situs bisa dipasang sebagai PWA.
// Halaman selalu diambil dari jaringan dulu; cache hanya cadangan saat offline.
const CACHE = "simpanclip-v1";
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/", "/styles.css", "/app.js", "/favicon.svg"])));
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return; // jangan sentuh panggilan API
  e.respondWith(fetch(req).catch(() => caches.match(req)));
});
