/**
 * Script pour nettoyer les console.log excessifs dans le frontend
 * Garde seulement console.error et remplace le reste par le logger
 */

const fs = require('fs');
const path = require('path');

const filesToClean = [
  'client/src/VideoDetail.jsx',
  'client/src/VideoPlayer.jsx',
  'client/src/App.jsx',
  'client/src/NetworkInfo.jsx'
];

const rootDir = path.join(__dirname, '..');

filesToClean.forEach(file => {
  const filePath = path.join(rootDir, file);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Fichier introuvable: ${file}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf-8');
  const original = content;
  
  // Supprimer les console.log de debug qui ne sont pas dans des callbacks inline
  content = content.replace(/^\s*console\.log\([^)]+\);?\s*$/gm, '');
  
  // Remplacer les console.log inline non-error
  content = content.replace(/console\.log\('✅[^']+'\)/g, '');
  content = content.replace(/console\.log\('🔊[^']+'\)/g, '');
  content = content.replace(/console\.log\('📝[^']+'\)/g, '');
  content = content.replace(/console\.log\('🎬[^']+'\)/g, '');
  content = content.replace(/console\.log\('🔄[^']+'\)/g, '');
  content = content.replace(/console\.log\('🖼️[^']+'\)/g, '');
  content = content.replace(/console\.log\('📥[^']+'\)/g, '');
  content = content.replace(/console\.log\('⏳[^']+'\)/g, '');
  content = content.replace(/console\.log\('▶️[^']+'\)/g, '');
  
  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`✅ ${file}`);
  }
});

console.log('\n✅ Nettoyage des console.log terminé');
