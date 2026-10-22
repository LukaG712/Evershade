# Evershade — Bootstrap Installation Script (Windows PowerShell)
# Clones all service repositories into the expected directories.
# Safe to re-run: will skip existing repositories unless -Force is used.

[CmdletBinding()]
param(
    [switch]$Force,
    [ValidateSet("minimal", "standard", "full")]
    [string]$Profile = "standard"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  Evershade Bootstrap Installer                               ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check Git
try {
    $gitVersion = git --version 2>$null
    Write-Host "[OK] Git is available: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[XX] ERROR: Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Read version manifest
if (-not (Test-Path "version-manifest.json")) {
    Write-Host "[XX] ERROR: version-manifest.json not found. Are you in the Evershade root directory?" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] version-manifest.json found" -ForegroundColor Green

# Extract service list based on profile
$manifest = Get-Content "version-manifest.json" | ConvertFrom-Json
$profileServices = $manifest.profiles.$Profile

# Filter out infrastructure services
$services = @($profileServices | Where-Object { $_ -notin @("redis", "ollama", "caddy") })

if ($services.Count -eq 0) {
    Write-Host "[XX] ERROR: No services found for profile '$Profile'." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Profile: $Profile" -ForegroundColor Green
Write-Host "[OK] Services to install: $($services.Count)" -ForegroundColor Green
Write-Host ""

$failed = @()
$skipped = @()
$cloned = @()

foreach ($service in $services) {
    $repoUrl = $manifest.services.$service.repository
    if (-not $repoUrl) {
        $repoUrl = "https://github.com/LukaG712/$service"
    }

    # Check if directory already exists
    if (Test-Path $service) {
        if ($Force) {
            Write-Host "[WARN] Removing existing $service directory (forced)..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $service
        } elseif (Test-Path "$service/.git") {
            Write-Host "[WARN] $service already exists (git repo) — skipping. Use -Force to reclone." -ForegroundColor Yellow
            $skipped += $service
            continue
        } else {
            Write-Host "[WARN] $service directory exists but is not a git repo — skipping. Use -Force to replace." -ForegroundColor Yellow
            $skipped += $service
            continue
        }
    }

    Write-Host "[ARROW] Cloning $service from $repoUrl ..." -ForegroundColor Cyan
    
    try {
        git clone --depth 1 $repoUrl $service 2>&1 | Out-Null
        Write-Host "[OK] $service cloned successfully" -ForegroundColor Green
        $cloned += $service
    } catch {
        Write-Host "[XX] Failed to clone $service : $_" -ForegroundColor Red
        $failed += $service
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "[OK] Cloned: $($cloned.Count) services" -ForegroundColor Green

if ($skipped.Count -gt 0) {
    Write-Host "[WARN] Skipped: $($skipped -join ', ')" -ForegroundColor Yellow
}

if ($failed.Count -gt 0) {
    Write-Host "[XX] Failed: $($failed -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation incomplete. Fix the failed services and re-run." -ForegroundColor Red
    exit 1
}

# Create .env from .env.example if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host ""
        Write-Host "[WARN] .env not found. Copying from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[WARN] Please edit .env with your API keys before starting." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Installation complete!                                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env with your API keys"
Write-Host "  2. Run .\start.ps1 -Profile $Profile to start services"
Write-Host ""
