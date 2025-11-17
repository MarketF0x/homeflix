import { useEffect } from 'react';
import { API } from "./config.js";

export default function NetworkInfo() {
  useEffect(() => {
    // Vérifier et rediriger automatiquement vers la bonne URL
    fetch(`${API}/network-config`)
      .then(res => res.json())
      .then(config => {
        const currentHost = window.location.hostname;
        const currentPort = window.location.port;
        const currentProtocol = window.location.protocol;
        
        // Extraire les IPs de la config
        const wifiIP = config.WiFiURL ? config.WiFiURL.replace('http://', '').split(':')[0] : null;
        const tailscaleIP = config.TailscaleURL ? config.TailscaleURL.replace('http://', '').split(':')[0] : null;
        
        console.log('Détection réseau:', { currentHost, wifiIP, tailscaleIP });
        
        // Si on est sur localhost, ne rien faire (accès local)
        if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
          console.log('✓ Accès local détecté');
          return;
        }
        
        // Si on est déjà sur l'IP WiFi locale, tout va bien
        if (currentHost === wifiIP) {
          console.log('✓ Réseau WiFi local détecté');
          return;
        }
        
        // Si on utilise Tailscale, vérifier si on est sur le même réseau local
        if (currentHost === tailscaleIP && wifiIP) {
          console.log('⚠ Utilisation de Tailscale - test du réseau local...');
          
          // Utiliser une image beacon pour tester l'accès WiFi (contourne CORS)
          const testImage = new Image();
          const timeout = setTimeout(() => {
            console.log('✗ IP WiFi non accessible - accès distant confirmé');
            testImage.src = '';
          }, 2000); // 2 secondes max
          
          testImage.onload = () => {
            clearTimeout(timeout);
            console.log(`✓ IP WiFi accessible - redirection vers ${wifiIP}`);
            const wifiURL = `${currentProtocol}//${wifiIP}:${currentPort}${window.location.pathname}${window.location.search}${window.location.hash}`;
            window.location.replace(wifiURL);
          };
          
          testImage.onerror = () => {
            clearTimeout(timeout);
            console.log('✗ IP WiFi non accessible - reste sur Tailscale');
          };
          
          // Tester avec un endpoint léger (favicon ou api)
          testImage.src = `http://${wifiIP}:${currentPort}/favicon.ico?t=${Date.now()}`;
        }
      })
      .catch(err => console.error('Erreur détection réseau:', err));
  }, []);

  // Composant invisible - ne rend rien
  return null;
}


