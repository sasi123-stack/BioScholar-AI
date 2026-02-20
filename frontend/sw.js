const CACHE_NAME = 'biomed-scholar-v1.3.0';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/styles.css',
    '/chat_styles.css',
    '/app.js',
    '/manifest.json'
];

// On install, cache the essential assets
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS_TO_CACHE))
    );
});

// Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Network First strategy
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests and non-http/https schemes (like chrome-extension)
    if (event.request.method !== 'GET' || !event.request.url.startsWith('http')) return;

    // Skip caching for API requests (especially health check)
    if (event.request.url.includes('/api/v1/')) {
        event.respondWith(
            fetch(event.request).catch(err => {
                console.warn('API fetch failed in SW:', err);
                return new Response(JSON.stringify({ error: 'Offline', message: 'API unavailable' }), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((networkResponse) => {
                // If network works, update the cache and return
                return caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, networkResponse.clone());
                    return networkResponse;
                });
            })
            .catch(async () => {
                try {
                    // Try exact match or match ignoring search
                    const cachedResponse = await caches.match(event.request, { ignoreSearch: true });
                    if (cachedResponse) return cachedResponse;

                    // Fallback for document navigation
                    if (event.request.mode === 'navigate') {
                        const cache = await caches.open(CACHE_NAME);
                        // Try both / and /index.html
                        return (await cache.match('/')) ||
                            (await cache.match('/index.html')) ||
                            new Response('Offline - Page not found in cache', { status: 404 });
                    }
                } catch (e) {
                    console.error('SW Match Error:', e);
                }

                return new Response('Offline: Network unavailable', {
                    status: 503,
                    statusText: 'Service Unavailable',
                    headers: { 'Content-Type': 'text/plain' }
                });
            })
    );
});
