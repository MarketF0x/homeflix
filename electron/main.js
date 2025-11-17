const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let serverProcess;
let healthTimer = null;
let restartTimer = null;
const restartState = {
  attempts: 0,
  consecutiveHealthFails: 0,
  lastStartAt: 0,
  lastUptimeOkAt: 0,
};
let appStartAt = Date.now();
let gpuCrashCount = 0;
let lastGpuCrashAt = 0;

// Gestion d'un petit fichier de configuration persistant (dans userData)
function flagsPath() {
  try { return path.join(app.getPath('userData'), 'homeflix-electron.json'); } catch { return null; }
}
function loadFlags() {
  try {
    const p = flagsPath();
    if (p && fs.existsSync(p)) {
      return JSON.parse(fs.readFileSync(p, 'utf-8')) || {};
    }
  } catch (_) {}
  return {};
}
function saveFlags(obj) {
  try {
    const p = flagsPath();
    if (!p) return;
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, JSON.stringify(obj, null, 2), 'utf-8');
  } catch (e) {
    console.warn('[WARN] Impossible d\'écrire le fichier de flags:', e.message);
  }
}

const runtimeFlags = loadFlags();

function restartApp(reason = 'unknown') {
  console.warn(`[APP] Redémarrage de l'application (raison: ${reason})`);
  app.isQuitting = true;
  if (healthTimer) { clearInterval(healthTimer); healthTimer = null; }
  if (restartTimer) { clearTimeout(restartTimer); restartTimer = null; }
  if (serverProcess) {
    try { serverProcess.kill(); } catch (_) {}
    serverProcess = null;
  }
  setTimeout(() => {
    app.relaunch();
    app.exit(0);
  }, 500);
}
const SERVER_PORT = 8000;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}`; // Forcer IPv4 au lieu de localhost

// OPTIMISATIONS ELECTRON
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=2048');
// Fallback GPU persistant
if (runtimeFlags.disableGPU) {
  console.warn('[GPU] Accélération matérielle désactivée (flag persistant)');
  app.disableHardwareAcceleration();
  app.commandLine.appendSwitch('disable-gpu');
}
// Stabilisation du Network Service (évite le crash/auto-restart bruyant)
app.commandLine.appendSwitch('enable-features', 'NetworkServiceInProcess');
app.commandLine.appendSwitch('disable-features', 'NetworkServiceSandbox,OutOfProcessSystemDns');

// Démarrer le serveur Python
function startServer() {
  const isWindows = process.platform === 'win32';
  const pythonCmd = isWindows ? 'python' : 'python3';

  let serverPath; let workingDir;
  if (app.isPackaged) {
    const resourcesPath = process.resourcesPath;
    serverPath = path.join(resourcesPath, 'server', 'main.py');
    workingDir = resourcesPath;
  } else {
    serverPath = path.join(__dirname, '..', 'server', 'main.py');
    workingDir = path.join(__dirname, '..');
  }

  console.log('[START] Demarrage serveur Homeflix...');
  console.log('   Empaquete:', app.isPackaged);
  console.log('   Python:', pythonCmd);
  console.log('   Script:', serverPath);
  console.log('   Repertoire:', workingDir);

  serverProcess = spawn(pythonCmd, [serverPath], {
    cwd: workingDir,
    env: { ...process.env },
    shell: isWindows
  });

  serverProcess.stdout.on('data', (data) => {
    console.log(`[SERVER] ${data.toString().trim()}`);
  });

  serverProcess.stderr.on('data', (data) => {
    const text = data.toString();
    text.split(/\r?\n/).forEach(lineRaw => {
      const line = lineRaw.trim();
      if (!line) return;
      if (/(^|\s)INFO[:\s-]/i.test(line)) {
        console.log(`[SERVER] ${line}`);
      } else if (/WARN/i.test(line)) {
        console.warn(`[SERVER WARN] ${line}`);
      } else {
        console.error(`[SERVER ERR] ${line}`);
      }
    });
  });

  serverProcess.on('close', (code, signal) => {
    console.log(`[SERVER] Processus terminé avec code ${code} (signal: ${signal || 'none'})`);
    if (!app.isQuitting) {
      scheduleRestart(`exit code ${code || 'unknown'}`);
    }
  });

  restartState.lastStartAt = Date.now();
  return new Promise(resolve => setTimeout(resolve, 2000));
}

// Attendre que le serveur réponde /api/ping
async function waitForServer(maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    console.log(`[WAIT] Tentative ${i + 1}/${maxAttempts}...`);
    try {
      const result = await new Promise((resolve) => {
        const req = http.get(`${SERVER_URL}/api/ping`, (res) => {
          console.log(`[DEBUG] Status code: ${res.statusCode}`);
          resolve(res.statusCode === 200);
        });
        req.on('error', (err) => {
          console.log(`[DEBUG] Erreur HTTP: ${err.message}`);
          resolve(false);
        });
        req.setTimeout(1000, () => {
          console.log('[DEBUG] Timeout atteint');
          req.destroy();
          resolve(false);
        });
      });
      if (result) {
        console.log('[OK] Serveur prêt !');
        restartState.consecutiveHealthFails = 0;
        restartState.attempts = 0;
        restartState.lastUptimeOkAt = Date.now();
        return true;
      }
    } catch (err) {
      console.log(`[DEBUG] Exception: ${err.message}`);
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  return false;
}

// Health-check périodique et redémarrage si le serveur ne répond plus
function startHealthMonitor(intervalMs = 15000, failThreshold = 3) {
  if (healthTimer) clearInterval(healthTimer);
  healthTimer = setInterval(async () => {
    try {
      const ok = await new Promise((resolve) => {
        const req = http.get(`${SERVER_URL}/api/ping`, (res) => {
          resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.setTimeout(1000, () => { req.destroy(); resolve(false); });
      });
      if (ok) {
        restartState.consecutiveHealthFails = 0;
        restartState.lastUptimeOkAt = Date.now();
      } else {
        restartState.consecutiveHealthFails += 1;
        console.warn(`[HEALTH] ping KO (${restartState.consecutiveHealthFails}/${failThreshold})`);
        if (restartState.consecutiveHealthFails >= failThreshold) {
          console.warn('[HEALTH] redémarrage du serveur (ping KO)');
          performRestart('healthcheck failure');
        }
      }
    } catch (e) {
      restartState.consecutiveHealthFails += 1;
      console.warn(`[HEALTH] erreur de ping: ${e.message}`);
      if (restartState.consecutiveHealthFails >= failThreshold) {
        performRestart('healthcheck exception');
      }
    }
  }, intervalMs);
}

function backoffDelay() {
  // Exponentiel borné: 2s, 4s, 8s, 16s, 30s, 30s...
  const base = 2000;
  const max = 30000;
  const delay = Math.min(max, base * Math.pow(2, restartState.attempts));
  return delay;
}

function scheduleRestart(reason = 'unknown') {
  restartState.attempts += 1;
  const delay = backoffDelay();
  if (restartTimer) clearTimeout(restartTimer);
  console.warn(`[RESTART] Planifié dans ${Math.round(delay/1000)}s (raison: ${reason}, tentative: ${restartState.attempts})`);
  restartTimer = setTimeout(() => performRestart(reason), delay);
}

function performRestart(reason = 'manual') {
  if (restartTimer) { clearTimeout(restartTimer); restartTimer = null; }
  if (serverProcess) {
    try { serverProcess.kill(); } catch (_) {}
    serverProcess = null;
  }
  startServer()
    .then(() => waitForServer(30))
    .then((ready) => {
      if (ready) {
        console.log(`[RESTART] Serveur relancé (raison: ${reason})`);
        restartState.attempts = 0;
      } else {
        console.error('[RESTART] Échec de redémarrage, nouvelle tentative avec backoff...');
        scheduleRestart('restart failed');
      }
    })
    .catch((e) => {
      console.error(`[RESTART] Exception au redémarrage: ${e.message}`);
      scheduleRestart('restart exception');
    });
}

function createWindow() {
  // Créer la fenêtre du navigateur avec optimisations
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    backgroundColor: '#000000',
    icon: path.join(__dirname, 'icon.png'),
    frame: false, // Fenêtre sans bordure (frameless) pour imiter le plein écran sans F11
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      // Optimisations
      backgroundThrottling: false, // Désactiver throttling en arrière-plan
      v8CacheOptions: 'none', // Désactiver le cache V8 temporairement
      spellcheck: false, // Désactiver correcteur orthographique
      devTools: false, // Désactiver l'accès aux DevTools pour l'utilisateur
    },
    show: false, // Ne pas afficher tant que ready-to-show
    title: 'Homeflix'
  });

  // Créer le menu personnalisé
  const menuTemplate = [
    {
      label: 'Fichier',
      submenu: [
        {
          label: 'Actualiser',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.reload();
          }
        },
        {
          label: 'Forcer l\'actualisation',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => {
            mainWindow.webContents.reloadIgnoringCache();
          }
        },
        { type: 'separator' },
        {
          label: 'Quitter',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Affichage',
      submenu: [
        {
          label: 'Zoom +',
          accelerator: 'CmdOrCtrl+Plus',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(currentZoom + 0.5);
          }
        },
        {
          label: 'Zoom -',
          accelerator: 'CmdOrCtrl+-',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomLevel();
            mainWindow.webContents.setZoomLevel(currentZoom - 0.5);
          }
        },
        {
          label: 'Réinitialiser le zoom',
          accelerator: 'CmdOrCtrl+0',
          click: () => {
            mainWindow.webContents.setZoomLevel(0);
          }
        },
        { type: 'separator' },
      ]
    },
    {
      label: 'Aide',
      submenu: [
        {
          label: 'À propos de Homeflix',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'À propos de Homeflix',
              message: 'Homeflix',
              detail: 'Serveur de streaming vidéo personnel\nVersion 2.0.0\n\n© 2025 Homeflix'
            });
          }
        },
        {
          label: 'Guide local',
          click: () => {
            // Ouvrir une fenêtre avec la page d'aide locale
            const helpFile = path.join(__dirname, 'help.html');
            if (fs.existsSync(helpFile)) {
              const helpWin = new BrowserWindow({
                width: 760,
                height: 600,
                backgroundColor: '#111',
                title: 'Aide Homeflix',
                autoHideMenuBar: true,
                webPreferences: { contextIsolation: true, devTools: false }
              });
              helpWin.loadFile(helpFile).catch(err => console.warn('[HELP] Erreur chargement help.html:', err.message));
            } else {
              console.warn('[HELP] help.html introuvable:', helpFile);
            }
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  // Conserver le menu d'application pour les accélérateurs (Ctrl+R, F12...) mais sans barre native visible
  Menu.setApplicationMenu(menu);

  // Charger l'URL du serveur
  mainWindow.loadURL(SERVER_URL);

  // Afficher la fenêtre quand prête
  mainWindow.once('ready-to-show', () => {
    // Maximiser pour donner l'illusion du plein écran sans activer F11
    try { mainWindow.maximize(); } catch {}
    mainWindow.show();
  });

  // Empêcher l'ouverture de nouvelles fenêtres (sécurité)
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Autoriser les liens externes dans le navigateur par défaut
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  // Gérer la fermeture
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Si la fenêtre devient non réactive, relancer l'application pour self-heal
  mainWindow.on('unresponsive', () => {
    console.error('[ERROR] Fenêtre non réactive');
    restartApp('window unresponsive');
  });

  // Gérer les erreurs de chargement
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('[ERROR] Erreur chargement:', errorDescription);
    
    // Réessayer après 2 secondes
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.reload();
      }
    }, 2000);
  });

  // Si le processus de rendu associé à cette fenêtre disparaît, relancer l'app
  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error('[ERROR] Renderer process gone (webContents):', details);
    const reason = (details && details.reason) || 'unknown';
    const fatalReasons = new Set(['crashed', 'oom', 'launch-failed', 'integrity-failure', 'abnormal-exit']);
    const inGrace = (Date.now() - appStartAt) < 10000; // 10s de tolérance au démarrage
    if (!inGrace && fatalReasons.has(reason)) {
      restartApp(`renderer gone (${reason})`);
    } else {
      console.warn('[WARN] Renderer non fatal ou dans la période de grâce, tentative de reload');
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.reloadIgnoringCache();
      }
    }
  });
}

// Quand Electron est prêt
app.whenReady().then(async () => {
  console.log('[APP] Homeflix - Demarrage...');
  // Empêcher les multiples instances (évite plusieurs serveurs)
  const gotLock = app.requestSingleInstanceLock();
  if (!gotLock) {
    app.quit();
    return;
  }
  appStartAt = Date.now();
  
  // Démarrer le serveur + attendre prêt
  await startServer();
  const serverReady = await waitForServer();
  if (!serverReady) {
    console.error('[ERROR] Serveur non prêt pour l’instant, supervision active (pas d’arrêt de l’app).');
  }
  // Créer la fenêtre même si on attend encore; la logique de reload gère l’attente
  createWindow();
  // Lancer health-check périodique
  startHealthMonitor();

  app.on('activate', () => {
    // Sur macOS, recréer une fenêtre si aucune n'existe
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quitter quand toutes les fenêtres sont fermées
app.on('window-all-closed', () => {
  // Sur macOS, les apps restent actives jusqu'à Cmd+Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Arrêter le serveur à la fermeture de l'app
app.on('before-quit', () => {
  console.log('[STOP] Arret du serveur...');
  app.isQuitting = true;
  if (healthTimer) { clearInterval(healthTimer); healthTimer = null; }
  if (restartTimer) { clearTimeout(restartTimer); restartTimer = null; }
  if (serverProcess) {
    serverProcess.kill();
  }
});

// Gérer les crashes
app.on('render-process-gone', (event, webContents, details) => {
  console.error('[ERROR] Processus de rendu crashe (app):', details);
  const reason = (details && details.reason) || 'unknown';
  const fatalReasons = new Set(['crashed', 'oom', 'launch-failed', 'integrity-failure', 'abnormal-exit']);
  const inGrace = (Date.now() - appStartAt) < 10000;
  if (!inGrace && fatalReasons.has(reason)) {
    restartApp(`renderer crash (${reason})`);
  } else {
    console.warn('[WARN] Renderer crash non fatal ou dans la période de grâce (app), on continue');
  }
});

app.on('child-process-gone', (event, details) => {
  console.error('[ERROR] Processus enfant crashe:', details);
  const type = ((details && details.type) || '').toString().toLowerCase();
  const name = ((details && (details.name || details.serviceName)) || '').toString().toLowerCase();
  // Ne pas redémarrer pour les crashes fréquents non bloquants
  if (type === 'utility' && (name.includes('network service') || name.includes('network.mojom.networkservice') || name.includes('network'))) {
    console.warn('[WARN] Network Service s\'est relancé côté Chromium — pas de relance de l\'app');
    return;
  }
  if (type === 'gpu-process') {
    const now = Date.now();
    // Fenêtre de 2 minutes; si plusieurs crashes, activer fallback GPU
    if (now - lastGpuCrashAt > 120000) { gpuCrashCount = 0; }
    lastGpuCrashAt = now;
    gpuCrashCount += 1;
    console.warn(`[WARN] GPU process disparu (compteur=${gpuCrashCount}) — Chromium va tenter de relancer le GPU`);
    if (gpuCrashCount >= 3 && !runtimeFlags.disableGPU) {
      console.warn('[GPU] Trop de crashes GPU: activation du fallback logiciel et relance');
      runtimeFlags.disableGPU = true;
      saveFlags(runtimeFlags);
      return restartApp('enable gpu fallback');
    }
    return; // pas de relance immédiate
  }
  restartApp(`child process gone (${type || 'unknown'}:${name || 'unk'})`);
});

// IPC handlers pour communication avec le renderer
ipcMain.handle('server-status', async () => {
  try {
    const response = await fetch(`${SERVER_URL}/api/ping`);
    return response.ok;
  } catch {
    return false;
  }
});

ipcMain.handle('reload-server', async () => {
  console.log('[RELOAD] Redemarrage du serveur...');
  if (serverProcess) {
    serverProcess.kill();
  }
  await startServer();
  const ok = await waitForServer();
  if (ok) {
    restartState.attempts = 0;
    restartState.consecutiveHealthFails = 0;
  }
  return ok;
});

// Contrôles de fenêtre pour la fenêtre frameless
ipcMain.handle('win:minimize', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.minimize(); return true; } catch { return false; }
});
ipcMain.handle('win:maximize', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.maximize(); return true; } catch { return false; }
});
ipcMain.handle('win:toggle-maximize', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try {
    if (mainWindow.isMaximized()) { mainWindow.unmaximize(); } else { mainWindow.maximize(); }
    return true;
  } catch { return false; }
});
ipcMain.handle('win:is-maximized', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { return mainWindow.isMaximized(); } catch { return false; }
});
ipcMain.handle('win:close', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.close(); return true; } catch { return false; }
});

// Actions de vue/utilitaires
ipcMain.handle('view:reload', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.reload(); return true; } catch { return false; }
});
ipcMain.handle('view:reload-hard', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.webContents.reloadIgnoringCache(); return true; } catch { return false; }
});
ipcMain.handle('view:zoom-in', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { const z = mainWindow.webContents.getZoomLevel(); mainWindow.webContents.setZoomLevel(z + 0.5); return true; } catch { return false; }
});
ipcMain.handle('view:zoom-out', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { const z = mainWindow.webContents.getZoomLevel(); mainWindow.webContents.setZoomLevel(z - 0.5); return true; } catch { return false; }
});
ipcMain.handle('view:zoom-reset', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try { mainWindow.webContents.setZoomLevel(0); return true; } catch { return false; }
});

// Ouvrir la fenêtre d'aide locale
ipcMain.handle('help:open', () => {
  const helpFile = path.join(__dirname, 'help.html');
  if (!fs.existsSync(helpFile)) { console.warn('[HELP] help.html introuvable'); return false; }
  try {
    const helpWin = new BrowserWindow({
      width: 760,
      height: 600,
      backgroundColor: '#111',
      title: 'Aide Homeflix',
      autoHideMenuBar: true,
      webPreferences: { contextIsolation: true, devTools: false }
    });
    helpWin.loadFile(helpFile).catch(err => console.warn('[HELP] Erreur chargement:', err.message));
    return true;
  } catch (e) {
    console.warn('[HELP] Erreur ouverture aide:', e.message);
    return false;
  }
});

// Contrôle de visibilité de la barre de menu (pour survol haut de fenêtre)
ipcMain.handle('menu:set-visible', async (_event, visible) => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  try {
    // autoHideMenuBar doit être à true pour que le masquage fonctionne avec Alt et via API
    mainWindow.setMenuBarVisibility(!!visible);
    return true;
  } catch (e) {
    console.warn('[WARN] setMenuBarVisibility a échoué:', e.message);
    return false;
  }
});
