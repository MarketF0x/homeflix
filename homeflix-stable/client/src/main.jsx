import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./styles/main.css";
import App from "./App.jsx";
import { I18nProvider } from "./i18n.jsx";
// Désactive le Service Worker et le cache côté Electron pour éviter d'anciennes versions de CSS/JS
if (typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
  const isElectron = navigator.userAgent && navigator.userAgent.includes('Electron');
  if (isElectron) {
    navigator.serviceWorker.getRegistrations?.().then((regs) => {
      regs.forEach((r) => r.unregister());
    }).catch(() => {});
    // Purge les caches du navigateur
    try {
      if (window.caches && caches.keys) {
        caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
      }
    } catch {}
    console.log('⚠️ Service Worker et caches désactivés sous Electron');
  }
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider>
      <App />
    </I18nProvider>
  </React.StrictMode>
);

