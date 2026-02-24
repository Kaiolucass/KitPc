importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "SUA_API_KEY",
  projectId: "SEU_PROJECT_ID",
  messagingSenderId: "SEU_SENDER_ID",
  appId: "SEU_APP_ID"
});

const messaging = firebase.messaging();

// Exibe a notificação quando o site está fechado
messaging.onBackgroundMessage((payload) => {
  console.log('Notificação recebida em segundo plano:', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/Imagens/favicon.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});