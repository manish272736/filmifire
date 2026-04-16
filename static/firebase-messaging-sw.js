// firebase-messaging-sw.js
// Place this file at: static/firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyB2SyciXeQJSkDKOyFUv8EBqgOFcB9e_rw",
  authDomain: "filmifire-fa205.firebaseapp.com",
  projectId: "filmifire-fa205",
  storageBucket: "filmifire-fa205.firebasestorage.app",
  messagingSenderId: "739326239723",
  appId: "1:739326239723:web:3b58de0bf185599b066fae"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const title = payload.notification?.title || 'FilmiFire';
  const body = payload.notification?.body || '';
  const url = payload.data?.url || 'https://filmifire.com';
  self.registration.showNotification(title, {
    body: body,
    icon: '/static/favicon-32x32.png',
    badge: '/static/favicon-32x32.png',
    data: { url: url },
    requireInteraction: false
  });
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = event.notification.data?.url || 'https://filmifire.com';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(function(clientList) {
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});