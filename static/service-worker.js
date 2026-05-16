const CACHE_NAME = 'rise-college-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// Install event - cache core assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(keyList.map(key => {
        if (key !== CACHE_NAME) {
          console.log('[Service Worker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache then network (stale-while-revalidate)
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // Return cached response if available
        if (cachedResponse) {
          // Update cache in background
          fetch(event.request).then(networkResponse => {
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, networkResponse.clone());
            });
          }).catch(err => console.log('Background update failed', err));
          return cachedResponse;
        }
        
        // Fallback to network
        return fetch(event.request).then(networkResponse => {
          // Don't cache non-GET requests or external URLs
          if (!event.request.url.startsWith(self.location.origin) || event.request.method !== 'GET') {
            return networkResponse;
          }
          // Cache the fetched response
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        }).catch(error => {
          console.log('[Service Worker] Fetch failed:', error);
          // Optionally return offline page for navigation requests
          if (event.request.mode === 'navigate') {
            return caches.match('/offline.html');
          }
          return new Response('Network error', { status: 408, statusText: 'Timeout' });
        });
      })
  );
});

// Push notification handler (if supported)
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.message || 'New update available',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-72.png',
    vibrate: [200, 100, 200],
    data: { url: data.url || '/' }
  };
  event.waitUntil(
    self.registration.showNotification(data.title || 'College Management System', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});