# ---------------------------------------------------------------
# HomeOne - Launcher complet (Backend + Frontend + Nettoyage auto)
# Mode silencieux - fermeture automatique
# ---------------------------------------------------------------

# Cache la fenêtre PowerShell immédiatement
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'
$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow($consolePtr, 0) | Out-Null

Set-Location $PSScriptRoot

# ---------------------------------------------------------------
# Étape 1 : Vérifications de base (silencieuses)
# ---------------------------------------------------------------
if (-not (Test-Path "$PSScriptRoot\server\main.py")) {
    [System.Windows.Forms.MessageBox]::Show("ERREUR : 'server\main.py' introuvable.", "HomeOne Launcher", 0, 16) | Out-Null
    exit
}
if (-not (Test-Path "$PSScriptRoot\client\package.json")) {
    [System.Windows.Forms.MessageBox]::Show("ERREUR : 'client\package.json' introuvable.", "HomeOne Launcher", 0, 16) | Out-Null
    exit
}

# ---------------------------------------------------------------
# Étape 2 : Activation de l'environnement virtuel (silencieuse)
# ---------------------------------------------------------------
$venvPath = "$PSScriptRoot\.venv310\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
}

# ---------------------------------------------------------------
# Étape 3 : Nettoyage des anciens processus Node (Vite)
# ---------------------------------------------------------------
try {
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
} catch {
    # Silencieux
}

# ---------------------------------------------------------------
# Étape 4 : Lancer le backend FastAPI
# ---------------------------------------------------------------
Start-Process powershell -WindowStyle Hidden -ArgumentList "cd '$PSScriptRoot\server'; python main.py"

# ---------------------------------------------------------------
# Étape 5 : Lancer le frontend React sur port fixe 5173
# ---------------------------------------------------------------
Start-Process powershell -WindowStyle Hidden -ArgumentList "cd '$PSScriptRoot\client'; npm run dev"

# ---------------------------------------------------------------
# Étape 6 : Attendre le démarrage de Vite
# ---------------------------------------------------------------
Start-Sleep -Seconds 10

# ---------------------------------------------------------------
# Étape 7 : Ouvrir en mode Application (Chrome/Edge) et fermer le lanceur
# ---------------------------------------------------------------
$targetUrl = "http://localhost:5173"

Start-Sleep -Seconds 2
$chromePaths = @(
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
)
$edgePaths = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe"
)

$browser = $null
foreach ($p in $chromePaths + $edgePaths) {
    if (Test-Path $p) { $browser = $p; break }
}

if ($browser) {
    Start-Process $browser "--app=$targetUrl --new-window"
} else {
    Start-Process $targetUrl
}

# Le lanceur se ferme automatiquement après avoir ouvert le navigateur
exit
