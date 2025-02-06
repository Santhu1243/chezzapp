let CACHE_NAME = 'django-pwa-cache-v1';
let urlsToCache = [
    '/',
    '/static/assets/css/style.css',  // Ensure this exists
    '/static/assets/js/script.js',   // Ensure this exists
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return Promise.all(
                urlsToCache.map(url => 
                    fetch(url, {cache: "no-store"})
                        .then(response => {
                            if (!response.ok) {
                                console.warn(`Skipping ${url}, failed to fetch.`);
                                return null;
                            }
                            return cache.put(url, response.clone());
                        })
                        .catch(err => console.error(`Error caching ${url}:`, err))
                )
            );
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
