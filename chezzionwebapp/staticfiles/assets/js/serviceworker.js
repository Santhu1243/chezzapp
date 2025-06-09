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
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});

self.addEventListener('install', (event) => {
    console.log('Service Worker Installing...');
    event.waitUntil(self.skipWaiting()); // Activate it immediately
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker Activated!');
    event.waitUntil(self.clients.claim()); // Take control immediately
});
