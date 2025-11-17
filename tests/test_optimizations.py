#!/usr/bin/env python3
"""
Script de test des optimisations Homeflix
Mesure les performances avant/après optimisations
"""

import time
import sqlite3
import requests
from pathlib import Path

# Couleurs pour terminaux
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_test(name, value, unit="", status="info"):
    colors = {"success": GREEN, "warning": YELLOW, "error": RED, "info": BLUE}
    color = colors.get(status, RESET)
    print(f"{color}✓ {name:.<45} {value} {unit}{RESET}")

def test_database_optimizations():
    """Teste les optimisations SQLite"""
    print_section("📊 BASE DE DONNÉES (SQLite)")
    
    db_path = Path(__file__).parent / "server" / "homeflix.db"
    
    if not db_path.exists():
        print_test("Database", "NOT FOUND", "", "error")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. Vérifier WAL mode
    cursor.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    status = "success" if journal_mode.upper() == "WAL" else "warning"
    print_test("WAL Mode", journal_mode.upper(), "", status)
    
    # 2. Vérifier cache size
    cursor.execute("PRAGMA cache_size")
    cache_size = cursor.fetchone()[0]
    cache_mb = abs(cache_size) / 1024  # Négatif = KB
    print_test("Cache Size", f"{cache_mb:.1f}", "MB", "success" if cache_mb >= 1 else "warning")
    
    # 3. Vérifier synchronous
    cursor.execute("PRAGMA synchronous")
    sync_mode = cursor.fetchone()[0]
    sync_modes = {0: "OFF", 1: "NORMAL", 2: "FULL", 3: "EXTRA"}
    print_test("Synchronous", sync_modes.get(sync_mode, str(sync_mode)), "", "success")
    
    # 4. Nombre de vidéos
    cursor.execute("SELECT COUNT(*) FROM videos")
    video_count = cursor.fetchone()[0]
    print_test("Vidéos totales", video_count, "", "success")
    
    # 5. Test performance requête simple
    start = time.perf_counter()
    cursor.execute("SELECT * FROM videos LIMIT 100")
    results = cursor.fetchall()
    elapsed = (time.perf_counter() - start) * 1000
    status = "success" if elapsed < 10 else "warning"
    print_test("SELECT 100 vidéos", f"{elapsed:.2f}", "ms", status)
    
    # 6. Test requête avec index
    start = time.perf_counter()
    cursor.execute("SELECT * FROM videos WHERE year = 2023 AND genre LIKE '%Action%' LIMIT 20")
    results = cursor.fetchall()
    elapsed = (time.perf_counter() - start) * 1000
    status = "success" if elapsed < 15 else "warning"
    print_test("SELECT avec index composé", f"{elapsed:.2f}", "ms", status)
    
    # 7. Vérifier les index
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND sql IS NOT NULL
    """)
    indexes = cursor.fetchall()
    print_test("Index créés", len(indexes), "", "success" if len(indexes) > 5 else "warning")
    
    conn.close()

def test_api_performance():
    """Teste les performances de l'API"""
    print_section("⚡ API BACKEND (FastAPI)")
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Test ping
        start = time.perf_counter()
        response = requests.get(f"{base_url}/api/ping", timeout=5)
        elapsed = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            print_test("Serveur actif", "✓", "", "success")
            print_test("Latence ping", f"{elapsed:.2f}", "ms", "success" if elapsed < 50 else "warning")
        else:
            print_test("Serveur", "ERREUR", "", "error")
            return
        
        # 2. Test compression GZip
        headers = {'Accept-Encoding': 'gzip'}
        response = requests.get(f"{base_url}/api/categories", headers=headers, timeout=10)
        
        if 'content-encoding' in response.headers:
            encoding = response.headers['content-encoding']
            status = "success" if encoding == "gzip" else "warning"
            print_test("Compression GZip", encoding.upper(), "", status)
        else:
            print_test("Compression GZip", "DÉSACTIVÉE", "", "warning")
        
        # 3. Test temps de réponse catégories (cold)
        start = time.perf_counter()
        response = requests.get(f"{base_url}/api/categories", timeout=10)
        elapsed = (time.perf_counter() - start) * 1000
        status = "success" if elapsed < 100 else "warning"
        print_test("GET /categories (cold)", f"{elapsed:.2f}", "ms", status)
        
        # 4. Test temps de réponse catégories (cached)
        start = time.perf_counter()
        response = requests.get(f"{base_url}/api/categories", timeout=10)
        elapsed = (time.perf_counter() - start) * 1000
        status = "success" if elapsed < 50 else "warning"
        print_test("GET /categories (cached)", f"{elapsed:.2f}", "ms", status)
        
        # 5. Taille de la réponse
        if response.status_code == 200:
            content_size = len(response.content) / 1024  # KB
            print_test("Taille réponse", f"{content_size:.1f}", "KB", "info")
            
            # Estimation gain compression
            if 'content-encoding' in response.headers and response.headers['content-encoding'] == 'gzip':
                # Estimation: gzip réduit JSON de ~70%
                uncompressed_estimate = content_size * 3.3
                gain_percent = ((uncompressed_estimate - content_size) / uncompressed_estimate) * 100
                print_test("Gain compression estimé", f"{gain_percent:.0f}", "%", "success")
        
    except requests.exceptions.RequestException as e:
        print_test("API Backend", "INACCESSIBLE", "", "error")
        print(f"{RED}   Erreur: {e}{RESET}")

def test_frontend_build():
    """Teste le build frontend"""
    print_section("🎨 FRONTEND (React + Vite)")
    
    dist_path = Path(__file__).parent / "client" / "dist"
    
    if not dist_path.exists():
        print_test("Build dist/", "NON TROUVÉ", "", "warning")
        print(f"{YELLOW}   Exécutez 'cd client && npm run build'{RESET}")
        return
    
    # 1. Analyser les fichiers JS
    js_files = list(dist_path.glob("assets/*.js"))
    total_js_size = sum(f.stat().st_size for f in js_files) / 1024  # KB
    
    print_test("Fichiers JS", len(js_files), "", "info")
    print_test("Taille totale JS", f"{total_js_size:.1f}", "KB", "success" if total_js_size < 500 else "warning")
    
    # 2. Analyser les fichiers CSS
    css_files = list(dist_path.glob("assets/*.css"))
    total_css_size = sum(f.stat().st_size for f in css_files) / 1024  # KB
    
    print_test("Fichiers CSS", len(css_files), "", "info")
    print_test("Taille totale CSS", f"{total_css_size:.1f}", "KB", "success")
    
    # 3. Vérifier code splitting (plusieurs chunks JS)
    status = "success" if len(js_files) >= 3 else "warning"
    print_test("Code splitting actif", "✓" if len(js_files) >= 3 else "✗", "", status)
    
    # 4. Trouver le plus gros chunk
    if js_files:
        largest_chunk = max(js_files, key=lambda f: f.stat().st_size)
        largest_size = largest_chunk.stat().st_size / 1024  # KB
        print_test("Plus gros chunk", f"{largest_size:.1f}", "KB", "info")
        print_test("  └─", largest_chunk.name[:50], "", "info")

def test_electron_config():
    """Teste la configuration Electron"""
    print_section("🖥️ ELECTRON")
    
    electron_path = Path(__file__).parent / "electron"
    
    if not electron_path.exists():
        print_test("Dossier electron/", "NON TROUVÉ", "", "warning")
        return
    
    # 1. Vérifier package.json
    package_json = electron_path / "package.json"
    if package_json.exists():
        print_test("package.json", "✓", "", "success")
        
        import json
        with open(package_json) as f:
            pkg = json.load(f)
            version = pkg.get("version", "N/A")
            print_test("Version", version, "", "info")
    
    # 2. Vérifier main.js
    main_js = electron_path / "main.js"
    if main_js.exists():
        print_test("main.js", "✓", "", "success")
        
        with open(main_js, encoding='utf-8') as f:
            content = f.read()
            
            # Vérifier optimisations
            has_v8_cache = "v8CacheOptions" in content
            has_mem_limit = "max-old-space-size" in content
            has_background_throttling = "backgroundThrottling" in content
            
            print_test("  └─ V8 Code Cache", "✓" if has_v8_cache else "✗", "", 
                      "success" if has_v8_cache else "warning")
            print_test("  └─ Memory Limit", "✓" if has_mem_limit else "✗", "", 
                      "success" if has_mem_limit else "warning")
            print_test("  └─ Background Throttling", "OFF" if has_background_throttling else "ON", "", 
                      "success" if has_background_throttling else "info")
    
    # 3. Vérifier node_modules
    node_modules = electron_path / "node_modules"
    if node_modules.exists():
        print_test("node_modules/", "✓", "", "success")
        
        # Compter packages
        packages = [p for p in node_modules.iterdir() if p.is_dir() and not p.name.startswith('.')]
        print_test("  └─ Packages installés", len(packages), "", "info")
    else:
        print_test("node_modules/", "MANQUANT", "", "warning")
        print(f"{YELLOW}   Exécutez 'cd electron && npm install'{RESET}")

def main():
    """Fonction principale"""
    print(f"\n{BLUE}╔{'═'*58}╗{RESET}")
    print(f"{BLUE}║{' '*15}🚀 TEST OPTIMISATIONS HOMEFLIX{' '*15}║{RESET}")
    print(f"{BLUE}╚{'═'*58}╝{RESET}")
    
    print(f"\n{YELLOW}Ce script vérifie que les optimisations sont bien actives.{RESET}")
    print(f"{YELLOW}Résultats attendus après optimisations :{RESET}")
    print(f"  • WAL Mode: {GREEN}WAL{RESET}")
    print(f"  • Cache DB: {GREEN}≥ 2MB{RESET}")
    print(f"  • API GZip: {GREEN}ACTIVÉ{RESET}")
    print(f"  • Bundle JS: {GREEN}< 500KB{RESET}")
    print(f"  • Code Split: {GREEN}✓{RESET}\n")
    
    # Tests
    test_database_optimizations()
    test_api_performance()
    test_frontend_build()
    test_electron_config()
    
    print_section("✅ RÉSUMÉ")
    print(f"{GREEN}Tests terminés !{RESET}\n")
    print(f"{BLUE}Pour des mesures plus précises :{RESET}")
    print(f"  • Chrome DevTools → Lighthouse")
    print(f"  • Network → Analyze bundle size")
    print(f"  • Performance → Record session\n")

if __name__ == "__main__":
    main()
