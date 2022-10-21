const cache_name = "app";
const assets = [
  "/",
  "/addons/addons.js",
  "/fonts/fa-brands.css",
  "/fonts/fa-brands.ttf",
  "/fonts/fa-brands.woff2",
  "/fonts/fa-solid.css",
  "/fonts/fa-solid.ttf",
  "/fonts/fa-solid.woff2",
  "/fonts/fontawesome.css",
  "/favicon.ico",
  "/index.css",
  "/index.html",
  "/index.js",
  "/index_color.css",
];

self.addEventListener("install", installEvent => {
  installEvent.waitUntil(
    caches.open(cache_name).then(cache => {
      cache.addAll(assets);
    })
  );
});

self.addEventListener("fetch", fetchEvent => {
  fetchEvent.respondWith(
    caches.match(fetchEvent.request).then(res => {
      return res || fetch(fetchEvent.request);
    })
  );
});
