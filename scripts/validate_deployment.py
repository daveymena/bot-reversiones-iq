#!/usr/bin/env python3
"""
Script de validación para asegurar que el bot está listo para Git y EasyPanel
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentValidator:
    """Validador de deployment"""
    
    def __init__(self):
        self.checks: Dict[str, bool] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def validate_all(self) -> bool:
        """Ejecutar todas las validaciones"""
        print("🔍 VALIDANDO DEPLOYMENT...")
        print("=" * 60)
        
        self._check_security()
        self._check_structure()
        self._check_docker()
        self._check_documentation()
        self._check_configuration()
        
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_security(self):
        """Validar seguridad"""
        print("\n🔐 VALIDACIONES DE SEGURIDAD")
        print("-" * 60)
        
        # Verificar .env
        if Path(".env").exists():
            try:
                env_content = Path(".env").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                env_content = Path(".env").read_text(encoding='latin-1')
            
            # Verificar que no tiene credenciales reales
            has_real_creds = (
                "daveymena16@gmail.com" in env_content or
                "6715320Dvd" in env_content or
                "@gmail.com" in env_content and "tu@email.com" not in env_content
            )
            
            if has_real_creds:
                self.errors.append("❌ .env contiene credenciales reales (RIESGO DE SEGURIDAD)")
            else:
                self.checks[".env sin credenciales reales"] = True
                print("✅ .env sin credenciales reales")
        
        # Verificar .gitignore
        if Path(".gitignore").exists():
            try:
                gitignore = Path(".gitignore").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                gitignore = Path(".gitignore").read_text(encoding='latin-1')
            
            if ".env" in gitignore:
                self.checks[".gitignore incluye .env"] = True
                print("✅ .gitignore incluye .env")
            else:
                self.errors.append("❌ .gitignore no incluye .env")
            
            if "__pycache__" in gitignore:
                self.checks[".gitignore incluye __pycache__"] = True
                print("✅ .gitignore incluye __pycache__")
            else:
                self.warnings.append("⚠️ .gitignore no incluye __pycache__")
        
        # Verificar .env.example
        if Path(".env.example").exists():
            self.checks[".env.example existe"] = True
            print("✅ .env.example existe")
        else:
            self.errors.append("❌ .env.example no existe")
    
    def _check_structure(self):
        """Validar estructura de carpetas"""
        print("\n📁 VALIDACIONES DE ESTRUCTURA")
        print("-" * 60)
        
        required_dirs = [
            "core",
            "strategies",
            "data",
            "gui",
            "ai",
            "models",
            "docs",
            "scripts",
        ]
        
        for dir_name in required_dirs:
            if Path(dir_name).is_dir():
                self.checks[f"Carpeta {dir_name}/ existe"] = True
                print(f"✅ Carpeta {dir_name}/ existe")
            else:
                self.errors.append(f"❌ Carpeta {dir_name}/ no existe")
        
        # Verificar archivos principales
        required_files = [
            "main_modern.py",
            "main_headless.py",
            "config.py",
            "requirements.txt",
            "requirements_cloud.txt",
        ]
        
        for file_name in required_files:
            if Path(file_name).is_file():
                self.checks[f"Archivo {file_name} existe"] = True
                print(f"✅ Archivo {file_name} existe")
            else:
                self.errors.append(f"❌ Archivo {file_name} no existe")
    
    def _check_docker(self):
        """Validar configuración Docker"""
        print("\n🐳 VALIDACIONES DE DOCKER")
        print("-" * 60)
        
        # Verificar Dockerfile
        if Path("Dockerfile").exists():
            try:
                dockerfile = Path("Dockerfile").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                dockerfile = Path("Dockerfile").read_text(encoding='latin-1')
            
            if "main_headless.py" in dockerfile:
                self.checks["Dockerfile usa main_headless.py"] = True
                print("✅ Dockerfile usa main_headless.py")
            else:
                self.errors.append("❌ Dockerfile no usa main_headless.py")
            
            if "HEALTHCHECK" in dockerfile:
                self.checks["Dockerfile tiene HEALTHCHECK"] = True
                print("✅ Dockerfile tiene HEALTHCHECK")
            else:
                self.warnings.append("⚠️ Dockerfile no tiene HEALTHCHECK")
        else:
            self.errors.append("❌ Dockerfile no existe")
        
        # Verificar docker-compose.yml
        if Path("docker-compose.yml").exists():
            self.checks["docker-compose.yml existe"] = True
            print("✅ docker-compose.yml existe")
        else:
            self.errors.append("❌ docker-compose.yml no existe")
        
        # Verificar requirements_cloud.txt
        if Path("requirements_cloud.txt").exists():
            try:
                req_cloud = Path("requirements_cloud.txt").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                req_cloud = Path("requirements_cloud.txt").read_text(encoding='latin-1')
            
            if "PySide6" not in req_cloud:
                self.checks["requirements_cloud.txt sin PySide6"] = True
                print("✅ requirements_cloud.txt sin PySide6")
            else:
                self.warnings.append("⚠️ requirements_cloud.txt incluye PySide6")
        else:
            self.errors.append("❌ requirements_cloud.txt no existe")
    
    def _check_documentation(self):
        """Validar documentación"""
        print("\n📚 VALIDACIONES DE DOCUMENTACIÓN")
        print("-" * 60)
        
        required_docs = [
            "README.md",
            "docs/DEPLOYMENT_EASYPANEL.md",
        ]
        
        for doc in required_docs:
            if Path(doc).is_file():
                self.checks[f"Documentación {doc} existe"] = True
                print(f"✅ Documentación {doc} existe")
            else:
                self.errors.append(f"❌ Documentación {doc} no existe")
    
    def _check_configuration(self):
        """Validar configuración"""
        print("\n⚙️ VALIDACIONES DE CONFIGURACIÓN")
        print("-" * 60)
        
        # Verificar config.py
        if Path("config.py").exists():
            try:
                config = Path("config.py").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                config = Path("config.py").read_text(encoding='latin-1')
            
            if "class Config" in config:
                self.checks["config.py tiene clase Config"] = True
                print("✅ config.py tiene clase Config")
            else:
                self.errors.append("❌ config.py no tiene clase Config")
        else:
            self.errors.append("❌ config.py no existe")
        
        # Verificar main_headless.py
        if Path("main_headless.py").exists():
            try:
                headless = Path("main_headless.py").read_text(encoding='utf-8')
            except UnicodeDecodeError:
                headless = Path("main_headless.py").read_text(encoding='latin-1')
            
            if "logging" in headless:
                self.checks["main_headless.py tiene logging"] = True
                print("✅ main_headless.py tiene logging")
            else:
                self.warnings.append("⚠️ main_headless.py no tiene logging")
            
            if "signal" in headless:
                self.checks["main_headless.py maneja señales"] = True
                print("✅ main_headless.py maneja señales")
            else:
                self.warnings.append("⚠️ main_headless.py no maneja señales")
    
    def _print_results(self):
        """Imprimir resultados"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS")
        print("=" * 60)
        
        if self.checks:
            print(f"\n✅ VALIDACIONES EXITOSAS: {len(self.checks)}")
            for check in self.checks:
                print(f"   ✓ {check}")
        
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORES: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        
        print("\n" + "=" * 60)
        
        if not self.errors:
            print("✅ BOT LISTO PARA GIT Y EASYPANEL")
            print("=" * 60)
            return True
        else:
            print("❌ REVISAR ERRORES ANTES DE DESPLEGAR")
            print("=" * 60)
            return False

def main():
    """Punto de entrada"""
    validator = DeploymentValidator()
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
