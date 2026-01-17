function showLogoutModal(event) {
    if (event) event.preventDefault();
    document.getElementById('logoutModal').style.display = 'flex';
}

function closeLogoutModal() {
    document.getElementById('logoutModal').style.display = 'none';
}

function confirmLogout() {
    window.location.href = "/logout";
}

// Warn users before they leave the page (navigating back or closing tab)
// Note: Browsers have strict rules about this, mostly only when user has interacted with the page.
window.addEventListener('beforeunload', function (e) {
    // Only warn if they are on a dashboard/internal page
    const path = window.location.pathname;
    if (path.includes('/dashboard') || path.includes('/admin') || path.includes('/student')) {
        const confirmationMessage = 'You have not logged out. Are you sure you want to leave?';
        (e || window.event).returnValue = confirmationMessage;
        return confirmationMessage;
    }
});

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('logoutModal');
    if (event.target == modal) {
        closeLogoutModal();
    }
}
// Notification System
function toggleNotifs(event) {
    if (event) event.stopPropagation();
    const dropdown = document.getElementById('notif-dropdown');
    const isVisible = dropdown.style.display === 'block';

    // Close other dropdowns if any
    document.querySelectorAll('.notif-dropdown').forEach(d => d.style.display = 'none');

    if (!isVisible) {
        dropdown.style.display = 'block';
        fetchNotifications();
    } else {
        dropdown.style.display = 'none';
    }
}

async function fetchNotifications() {
    try {
        const response = await fetch('/api/notifications');
        const data = await response.json();
        const list = document.getElementById('notif-list');
        const badge = document.getElementById('notif-badge');

        const unreadCount = data.notifications.filter(n => !n.is_read).length;
        if (unreadCount > 0) {
            badge.innerText = unreadCount;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }

        if (data.notifications.length === 0) {
            list.innerHTML = '<div class="notif-empty">No notifications yet</div>';
            return;
        }

        list.innerHTML = data.notifications.map(n => `
            <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markAsRead('${n._id}', '${n.link}')">
                <span class="title">${n.title}</span>
                <span class="msg">${n.message}</span>
                <span class="time">${n.created_at}</span>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error fetching notifications:', err);
    }
}

async function markAsRead(id, link) {
    try {
        await fetch(`/api/notifications/read/${id}`, { method: 'POST' });
        window.location.href = link;
    } catch (err) {
        window.location.href = link;
    }
}

// Close dropdowns on click outside
document.addEventListener('click', () => {
    const dropdown = document.getElementById('notif-dropdown');
    if (dropdown) dropdown.style.display = 'none';
});

// Initial fetch for badge
if (document.getElementById('notif-badge')) {
    fetchNotifications();
    // Poll every minute
    setInterval(fetchNotifications, 60000);
}
