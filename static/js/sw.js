const CACHE_NAME = "placement-cell-v1";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/main.js",
  "/static/js/offline-notifications.js",
  "/offline.html",
];

// Install event
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
      .catch((err) => console.log("Cache installation failed:", err)),
  );
  self.skipWaiting();
});

// Activate event
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        }),
      );
    }),
  );
  self.clients.claim();
});

// Fetch event - Network first, cache fallback
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }

  // For API calls, try network first
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful responses
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return cached version if offline
          return caches
            .match(request)
            .then(
              (response) =>
                response || new Response("Offline - cached data not available"),
            );
        }),
    );
  } else {
    // For HTML/CSS/JS, cache first, network fallback
    event.respondWith(
      caches.match(request).then((response) => {
        if (response) {
          return response;
        }
        return fetch(request)
          .then((response) => {
            if (!response || response.status !== 200) {
              return response;
            }
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
            return response;
          })
          .catch(() => {
            return caches.match("/offline.html");
          });
      }),
    );
  }
});

// Background sync for offline notifications
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-notifications") {
    event.waitUntil(syncNotifications());
  }
});

async function syncNotifications() {
  try {
    const db = await openDatabase();
    const pendingNotifications = await getAllFromStore(
      db,
      "pendingNotifications",
    );

    for (const notif of pendingNotifications) {
      try {
        const response = await fetch("/api/notifications/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(notif),
        });

        if (response.ok) {
          await deleteFromStore(db, "pendingNotifications", notif.id);
        }
      } catch (err) {
        console.error("Failed to sync notification:", err);
      }
    }
  } catch (err) {
    console.error("Sync failed:", err);
  }
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("placementDB", 1);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("pendingNotifications")) {
        db.createObjectStore("pendingNotifications", { keyPath: "id" });
      }
    };
  });
}

function getAllFromStore(db, storeName) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, "readonly");
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function deleteFromStore(db, storeName, key) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, "readwrite");
    const store = transaction.objectStore(storeName);
    const request = store.delete(key);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

// Push notifications
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.message || "You have a new notification",
    icon: "/static/icons/icon-192.png",
    badge: "/static/icons/badge-72.png",
    tag: data.tag || "notification",
    requireInteraction: data.requireInteraction || false,
    actions: [
      { action: "open", title: "Open" },
      { action: "close", title: "Close" },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(data.title || "Placement Cell", options),
  );
});

// Notification click handler
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        for (let client of clientList) {
          if (client.url === "/" && "focus" in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow("/");
        }
      }),
  );
});
