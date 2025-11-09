@echo off
REM Script de lancement HomeOne (Windows)
REM Utilise start-dev.ps1 pour un démarrage propre et un nettoyage auto.

setlocal enableextensions
title HomeOne - Lancement

echo.
echo ========================================
echo   HomeOne - Lancement automatique
echo ========================================
echo.

REM Vérifier PowerShell
where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] PowerShell introuvable. Veuillez lancer manuellement: start-dev.ps1
    pause
    exit /b 1
)

REM Vérifier le script PS
if not exist start-dev.ps1 (
    echo [ERREUR] start-dev.ps1 manquant. Mise a jour requise.
    pause
    exit /b 1
)

REM Lancer le workflow PowerShell (purge + serveur + client + purge a la fin)
powershell -ExecutionPolicy Bypass -File "%~dp0start-dev.ps1"

echo.
echo [INFO] Workflow termine. Tous les processus devraient etre arretes et les ports liberes.
echo.
pause
