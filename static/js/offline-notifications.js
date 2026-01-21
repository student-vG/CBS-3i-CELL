// Offline Notifications Handler
class OfflineNotificationManager {
  constructor() {
    this.dbName = "placementDB";
    this.storeName = "pendingNotifications";
    this.db = null;
    this.isOnline = navigator.onLine;
    this.initDB();
    this.setupEventListeners();
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => {
        console.error("Database failed to open");
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log("Database opened successfully");
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, {
            keyPath: "id",
            autoIncrement: true,
          });
          console.log("Object store created");
        }
      };
    });
  }

  setupEventListeners() {
    window.addEventListener("online", () => {
      this.isOnline = true;
      console.log("App is online");
      this.syncPendingNotifications();
      this.showNotification("You are back online!", { type: "success" });
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
      console.log("App is offline");
      this.showNotification(
        "You are now offline. Notifications will sync when back online.",
        { type: "warning" },
      );
    });
  }

  async addNotification(notificationData) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, "readwrite");
      const store = transaction.objectStore(this.storeName);
      const notification = {
        ...notificationData,
        timestamp: new Date().toISOString(),
        synced: false,
      };

      const request = store.add(notification);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async getPendingNotifications() {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, "readonly");
      const store = transaction.objectStore(this.storeName);
      const request = store.getAll();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async deleteNotification(id) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(this.storeName, "readwrite");
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async syncPendingNotifications() {
    if (!this.isOnline) return;

    const pending = await this.getPendingNotifications();

    for (const notif of pending) {
      try {
        // Send to server
        const response = await fetch("/api/notifications/sync", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(notif),
        });

        if (response.ok) {
          await this.deleteNotification(notif.id);
          console.log("Notification synced:", notif.id);
        }
      } catch (err) {
        console.error("Failed to sync notification:", err);
      }
    }
  }

  showNotification(title, options = {}) {
    const {
      message = "",
      type = "info", // info, success, warning, error
      duration = 3000,
      icon = "",
      action = null,
    } = options;

    const notifEl = document.createElement("div");
    notifEl.className = `offline-notification offline-notification-${type}`;
    notifEl.style.cssText = `
      position: fixed;
      bottom: 80px;
      left: 20px;
      right: 20px;
      padding: 16px;
      border-radius: 8px;
      background: ${this.getBackgroundColor(type)};
      color: white;
      font-weight: 500;
      z-index: 9999;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: slideUp 0.3s ease-out;
      font-size: 14px;
      max-width: 400px;
    `;

    let content = `${icon ? icon + " " : ""}<strong>${title}</strong>`;
    if (message) {
      content += `<br><small>${message}</small>`;
    }

    notifEl.innerHTML = content;

    if (action) {
      const btn = document.createElement("button");
      btn.textContent = action.label;
      btn.style.cssText = `
        margin-left: 10px;
        padding: 6px 12px;
        background: rgba(255,255,255,0.3);
        border: none;
        border-radius: 4px;
        color: white;
        cursor: pointer;
        font-weight: 500;
      `;
      btn.onclick = action.callback;
      notifEl.appendChild(btn);
    }

    document.body.appendChild(notifEl);

    if (duration > 0) {
      setTimeout(() => {
        notifEl.style.animation = "slideDown 0.3s ease-out";
        setTimeout(() => notifEl.remove(), 300);
      }, duration);
    }

    return notifEl;
  }

  getBackgroundColor(type) {
    const colors = {
      success: "#10b981",
      error: "#ef4444",
      warning: "#f59e0b",
      info: "#3b82f6",
    };
    return colors[type] || colors.info;
  }
}

// Initialize
const offlineNotificationManager = new OfflineNotificationManager();

// Add animation keyframes
const style = document.createElement("style");
style.textContent = `
  @keyframes slideUp {
    from {
      transform: translateY(400px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes slideDown {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
