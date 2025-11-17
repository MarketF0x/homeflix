/**
 * Système de logging pour le frontend Homeflix
 * Permet d'activer/désactiver les logs de debug facilement
 */

// En production, mettre à false
const DEBUG_MODE = import.meta.env.DEV || false;

class Logger {
  constructor(module) {
    this.module = module;
  }

  debug(...args) {
    if (DEBUG_MODE) {
      console.log(`[${this.module}]`, ...args);
    }
  }

  info(...args) {
    console.info(`[${this.module}]`, ...args);
  }

  warn(...args) {
    console.warn(`[${this.module}]`, ...args);
  }

  error(...args) {
    console.error(`[${this.module}]`, ...args);
  }
}

// Créer des loggers pour chaque module
export const videoLogger = new Logger('Video');
export const apiLogger = new Logger('API');
export const playerLogger = new Logger('Player');
export const networkLogger = new Logger('Network');

export default Logger;
