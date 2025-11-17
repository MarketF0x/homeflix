# Script pour générer automatiquement le numéro de version avant build
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$buildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$versionFile = Join-Path $PSScriptRoot "client\public\version.json"
$versionContent = @{
    version = $timestamp
    buildDate = $buildDate
} | ConvertTo-Json

Set-Content -Path $versionFile -Value $versionContent -Encoding UTF8

Write-Host "✅ Version générée: $timestamp" -ForegroundColor Green
Write-Host "📅 Date: $buildDate" -ForegroundColor Cyan
