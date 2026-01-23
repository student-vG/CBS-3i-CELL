const CACHE_NAME = 'cbs-placement-v1';
const ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/manifest.json',
    '/offline'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request)
                    .catch(() => {
                        if (event.request.mode === 'navigate') {
                            return caches.match('/offline');
                        }
                    });
            })
    );
});
