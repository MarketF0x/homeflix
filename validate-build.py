#!/usr/bin/env python3
"""
Script de validation de build de production
Vérifie que le build est prêt pour la distribution
"""

import os
import json
import sys
from pathlib import Path

class BuildValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.root_dir = Path(__file__).parent
        
    def validate(self):
        """Exécute toutes les validations"""
        print("🔍 Validation du build de production...\n")
        
        self.check_build_exists()
        self.check_package_json()
        self.check_license()
        self.check_documentation()
        self.check_settings()
        self.check_no_secrets()
        self.check_dependencies()
        
        self.print_results()
        
        return len(self.errors) == 0
    
    def check_build_exists(self):
        """Vérifie que le build client existe"""
        build_dir = self.root_dir / "client" / "dist"
        
        if not build_dir.exists():
            self.errors.append("❌ Le dossier client/dist n'existe pas. Exécutez 'npm run build' d'abord.")
            return
        
        # Vérifier les fichiers essentiels
        index_html = build_dir / "index.html"
        if not index_html.exists():
            self.errors.append("❌ client/dist/index.html manquant")
        else:
            print("✅ Build client présent")
        
        # Vérifier la taille du build
        total_size = sum(f.stat().st_size for f in build_dir.rglob('*') if f.is_file())
        total_mb = total_size / (1024 * 1024)
        
        if total_mb > 5:
            self.warnings.append(f"⚠️  Build client volumineux: {total_mb:.2f} MB")
        else:
            print(f"✅ Taille du build: {total_mb:.2f} MB")
    
    def check_package_json(self):
        """Vérifie le package.json"""
        pkg_file = self.root_dir / "package.json"
        
        if not pkg_file.exists():
            self.errors.append("❌ package.json manquant")
            return
        
        with open(pkg_file, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
        
        # Vérifier les champs essentiels
        required = ['name', 'version', 'description', 'license', 'author']
        for field in required:
            if field not in pkg or not pkg[field]:
                self.errors.append(f"❌ package.json: champ '{field}' manquant ou vide")
        
        # Vérifier la version
        if 'version' in pkg:
            version = pkg['version']
            if version.startswith('0.'):
                self.warnings.append(f"⚠️  Version {version} suggère une version beta")
            else:
                print(f"✅ Version: {version}")
        
        # Vérifier la licence
        if pkg.get('license') == 'MIT':
            print("✅ Licence: MIT")
        else:
            self.warnings.append(f"⚠️  Licence non standard: {pkg.get('license')}")
    
    def check_license(self):
        """Vérifie le fichier LICENSE"""
        license_file = self.root_dir / "LICENSE"
        
        if not license_file.exists():
            self.errors.append("❌ Fichier LICENSE manquant")
            return
        
        with open(license_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que c'est bien la licence MIT
        if 'MIT License' not in content:
            self.warnings.append("⚠️  Le fichier LICENSE ne semble pas être MIT")
        else:
            print("✅ Fichier LICENSE présent")
        
        # Vérifier la date de copyright
        import datetime
        current_year = datetime.datetime.now().year
        if str(current_year) not in content:
            self.warnings.append(f"⚠️  Copyright year devrait inclure {current_year}")
    
    def check_documentation(self):
        """Vérifie la documentation"""
        docs = {
            'README.md': 'Guide principal',
            'docs/GUIDE_UTILISATEUR.md': 'Guide utilisateur',
            'CHANGELOG.md': 'Historique des versions',
        }
        
        for doc, desc in docs.items():
            doc_file = self.root_dir / doc
            if not doc_file.exists():
                self.errors.append(f"❌ {doc} manquant ({desc})")
            else:
                # Vérifier que le fichier n'est pas vide
                if doc_file.stat().st_size < 100:
                    self.warnings.append(f"⚠️  {doc} semble incomplet")
                else:
                    print(f"✅ Documentation: {doc}")
    
    def check_settings(self):
        """Vérifie les fichiers de configuration"""
        settings = self.root_dir / "settings.yaml"
        
        if not settings.exists():
            self.warnings.append("⚠️  settings.yaml manquant (sera créé à l'installation)")
            return
        
        with open(settings, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier qu'il n'y a pas de clés API en dur
        if 'api_key:' in content and 'api_key: ""' not in content and 'api_key: ' not in content:
            if len(content.split('api_key:')[1].split('\n')[0].strip().strip('"')) > 5:
                self.errors.append("❌ Clé API TMDb détectée dans settings.yaml")
        
        print("✅ Configuration vérifiée")
    
    def check_no_secrets(self):
        """Vérifie l'absence de secrets"""
        # Fichiers à vérifier
        files_to_check = [
            self.root_dir / "client" / "src",
            self.root_dir / "server",
        ]
        
        dangerous_patterns = [
            'password = "',
            'api_key = "',
            'secret = "',
            'token = "',
        ]
        
        secrets_found = []
        
        for base_path in files_to_check:
            if not base_path.exists():
                continue
            
            for file_path in base_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for pattern in dangerous_patterns:
                            if pattern in content.lower():
                                secrets_found.append(str(file_path.relative_to(self.root_dir)))
                    except:
                        pass
        
        if secrets_found:
            self.warnings.append(f"⚠️  Secrets potentiels dans: {', '.join(set(secrets_found))}")
        else:
            print("✅ Aucun secret détecté")
    
    def check_dependencies(self):
        """Vérifie les dépendances"""
        # Vérifier requirements.txt
        req_file = self.root_dir / "server" / "requirements.txt"
        if not req_file.exists():
            self.errors.append("❌ server/requirements.txt manquant")
        else:
            print("✅ Dépendances Python présentes")
        
        # Vérifier package.json client
        client_pkg = self.root_dir / "client" / "package.json"
        if not client_pkg.exists():
            self.errors.append("❌ client/package.json manquant")
        else:
            print("✅ Dépendances Node.js présentes")
    
    def print_results(self):
        """Affiche les résultats de validation"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE VALIDATION")
        print("="*60 + "\n")
        
        if self.warnings:
            print("⚠️  AVERTISSEMENTS:\n")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print("❌ ERREURS:\n")
            for error in self.errors:
                print(f"  {error}")
            print()
            print("🚫 Build NON VALIDE pour distribution")
            return
        
        if self.warnings:
            print("⚠️  Build VALIDE avec avertissements")
        else:
            print("✅ Build PARFAIT - Prêt pour distribution!")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    validator = BuildValidator()
    success = validator.validate()
    sys.exit(0 if success else 1)
