const CACHE_NAME = 'cbs-3icell-v2';
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/css/mobile-nav.css',
    '/static/css/dashboard-responsive.css',
    '/static/js/main.js',
    '/static/js/offline-notifications.js',
    '/static/images/logo1.png',
    '/static/manifest.json',
    '/offline',
    'https://unpkg.com/@phosphor-icons/web',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap'
];

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(STATIC_ASSETS))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) return caches.delete(key);
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests like Mixpanel/Analytics if any
    if (!event.request.url.startsWith(self.location.origin) && !event.request.url.includes('unpkg') && !event.request.url.includes('fonts')) {
        return; 
    }

    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.match(event.request)
                        .then((response) => {
                            return response || caches.match('/offline');
                        });
                })
        );
    } else {
        event.respondWith(
            caches.match(event.request)
                .then((response) => {
                    return response || fetch(event.request);
                })
        );
    }
});
