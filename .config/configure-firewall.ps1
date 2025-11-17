# ============================================================================
# Configuration automatique du pare-feu Windows pour Homeflix
# ============================================================================
# Ce script cree des regles de pare-feu pour autoriser l'acces reseau
# aux ports 5173 (client Vite) et 8000 (serveur FastAPI)
# ============================================================================

Write-Host "Configuration du pare-feu Windows pour Homeflix..." -ForegroundColor Cyan
Write-Host ""

# Verifier les privileges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERREUR: Ce script necessite des privileges administrateur!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Veuillez:" -ForegroundColor Yellow
    Write-Host "   1. Clic droit sur PowerShell" -ForegroundColor Yellow
    Write-Host "   2. Selectionner 'Executer en tant qu'administrateur'" -ForegroundColor Yellow
    Write-Host "   3. Relancer: .\configure-firewall.ps1" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "OK: Privileges administrateur detectes" -ForegroundColor Green
Write-Host ""

# Fonction pour creer ou mettre a jour une regle de pare-feu
function Add-FirewallRuleIfNeeded {
    param(
        [string]$RuleName,
        [string]$Port,
        [string]$Description
    )
    
    # Verifier si la regle existe deja
    $existingRule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "INFO: La regle '$RuleName' existe deja" -ForegroundColor Yellow
        Write-Host "   Suppression de l'ancienne regle..." -ForegroundColor Gray
        Remove-NetFirewallRule -DisplayName $RuleName
    }
    
    Write-Host "Creation de la regle: $RuleName (port $Port)" -ForegroundColor Cyan
    
    try {
        New-NetFirewallRule `
            -DisplayName $RuleName `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort $Port `
            -Action Allow `
            -Profile Any `
            -Description $Description `
            -ErrorAction Stop | Out-Null
        
        Write-Host "OK: Regle creee avec succes!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "ERREUR lors de la creation: $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host "Creation des regles de pare-feu..." -ForegroundColor White
Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host ""

# Regle 1: Client Vite (port 5173)
$success1 = Add-FirewallRuleIfNeeded `
    -RuleName "Homeflix - Client Vite (5173)" `
    -Port "5173" `
    -Description "Autorise l'acces reseau au client web Homeflix (Vite Dev Server)"

Write-Host ""

# Regle 2: Serveur FastAPI (port 8000)
$success2 = Add-FirewallRuleIfNeeded `
    -RuleName "Homeflix - Serveur API (8000)" `
    -Port "8000" `
    -Description "Autorise l'acces reseau au serveur API Homeflix (FastAPI/Uvicorn)"

Write-Host ""
Write-Host "===============================================" -ForegroundColor DarkGray

# Resume
if ($success1 -and $success2) {
    Write-Host "OK: Toutes les regles ont ete creees!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Votre serveur est maintenant accessible sur le reseau local" -ForegroundColor Cyan
    Write-Host ""
    
    # Afficher l'adresse IP locale
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*" } | Select-Object -First 1).IPAddress
    
    if ($ipAddress) {
        Write-Host "Les utilisateurs distants peuvent acceder via:" -ForegroundColor Yellow
        Write-Host "   http://$ipAddress:5173" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "Conseils:" -ForegroundColor Cyan
    Write-Host "   - Assurez-vous que le serveur et le client sont demarres" -ForegroundColor Gray
    Write-Host "   - Verifiez que votre routeur/box n'a pas de restrictions" -ForegroundColor Gray
    Write-Host "   - Les appareils doivent etre sur le meme reseau Wi-Fi/LAN" -ForegroundColor Gray
}
else {
    Write-Host "AVERTISSEMENT: Certaines regles n'ont pas pu etre creees" -ForegroundColor Yellow
    Write-Host "   Verifiez les messages d'erreur ci-dessus" -ForegroundColor Gray
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host ""

# Option pour afficher les regles creees
$showRules = Read-Host "Voulez-vous afficher les regles creees? (o/n)"
if ($showRules -eq "o" -or $showRules -eq "O") {
    Write-Host ""
    Write-Host "Regles de pare-feu Homeflix:" -ForegroundColor Cyan
    Get-NetFirewallRule -DisplayName "Homeflix*" | Format-Table DisplayName, Enabled, Direction, Action -AutoSize
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
