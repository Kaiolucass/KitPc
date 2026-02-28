importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyBBHTJbRxW6DCYtzOCUAZ-UGkvOZXD3waw",
  authDomain: "kitpc-17567.firebaseapp.com",
  projectId: "kitpc-17567",
  storageBucket: "kitpc-17567.firebasestorage.app",
  messagingSenderId: "868153808593",
  appId: "1:868153808593:web:15759921e8736b075d57f0"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Mensagem recebida', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});