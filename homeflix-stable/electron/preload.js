const { contextBridge, ipcRenderer } = require('electron');

// Exposer des APIs sécurisées au renderer process
contextBridge.exposeInMainWorld('homeflix', {
  // Indiquer explicitement que l'app tourne dans Electron
  isElectron: true,
  // Vérifier le statut du serveur
  checkServerStatus: () => ipcRenderer.invoke('server-status'),

  // Redémarrer le serveur
  reloadServer: () => ipcRenderer.invoke('reload-server'),

  // Contrôles de fenêtre (frameless)
  winMinimize: () => ipcRenderer.invoke('win:minimize'),
  winMaximize: () => ipcRenderer.invoke('win:maximize'),
  winToggleMaximize: () => ipcRenderer.invoke('win:toggle-maximize'),
  winIsMaximized: () => ipcRenderer.invoke('win:is-maximized'),
  winClose: () => ipcRenderer.invoke('win:close'),

  // Actions d'affichage
  viewReload: () => ipcRenderer.invoke('view:reload'),
  viewReloadHard: () => ipcRenderer.invoke('view:reload-hard'),
  viewZoomIn: () => ipcRenderer.invoke('view:zoom-in'),
  viewZoomOut: () => ipcRenderer.invoke('view:zoom-out'),
  viewZoomReset: () => ipcRenderer.invoke('view:zoom-reset'),

  // Aide locale
  helpOpen: () => ipcRenderer.invoke('help:open'),

  // Version de l'app
  version: '2.0.0',

  // Platform info
  platform: process.platform
});

console.log('🔧 Preload script chargé');
