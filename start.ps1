# Evershade — Startup Script (Windows PowerShell)
# Validates configuration, checks dependencies, and starts services.

[CmdletBinding()]
param(
    [ValidateSet("minimal", "standard", "full")]
    [string]$Profile = "standard",
    [ValidateSet("desktop", "server")]
    [string]$Mode = "desktop"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  Starting Evershade (profile: $Profile, mode: $Mode)                       ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check Docker
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "[OK] Docker is available: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[XX] ERROR: Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker compose version 2>$null
    Write-Host "[OK] Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "[XX] ERROR: Docker Compose is not available." -ForegroundColor Red
    exit 1
}

# Create .env from .env.example if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[WARN] .env not found. Copying from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[WARN] Please edit .env with your API keys before starting." -ForegroundColor Yellow
    } else {
        Write-Host "[XX] ERROR: Neither .env nor .env.example found." -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] .env file found" -ForegroundColor Green

# Load .env for validation
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and $line -notmatch '^#' -and $line -match '=') {
        $key = $line.Split('=', 2)[0].Trim()
        $value = $line.Split('=', 2)[1].Trim()
        $envVars[$key] = $value
    }
}

# Validate API keys in server mode
if ($Mode -eq "server") {
    Write-Host "[WARN] Server mode detected — validating security configuration..." -ForegroundColor Yellow
    
    $defaultKeys = @{
        "EVERSHADE_GREENIE_API_KEY" = "change-me-greenie"
        "EVERSHADE_SLINKER_API_KEY" = "change-me-slinker"
        "EVERSHADE_TRAPPER_API_KEY" = "change-me-trapper"
        "EVERSHADE_GOBBER_API_KEY" = "change-me-gobber"
        "EVERSHADE_ENCRYPTION_KEY" = "change-me-encryption-key"
    }
    
    $insecure = $false
    foreach ($key in $defaultKeys.Keys) {
        $defaultValue = $defaultKeys[$key]
        $actualValue = $envVars[$key]
        if ($actualValue -eq $defaultValue -or [string]::IsNullOrEmpty($actualValue)) {
            Write-Host "[XX] INSECURE: $key is using the default or empty value" -ForegroundColor Red
            $insecure = $true
        }
    }
    
    if ($insecure) {
        Write-Host ""
        Write-Host "ERROR: Server mode refuses to start with default or insecure credentials." -ForegroundColor Red
        Write-Host "Fix .env with secure keys, then retry." -ForegroundColor Yellow
        Write-Host "Generate keys: openssl rand -hex 32" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[OK] Security validation passed for server mode" -ForegroundColor Green
} else {
    # Desktop mode: warn about defaults but allow
    $hasDefaultKeys = $false
    $checkKeys = @{
        "EVERSHADE_GREENIE_API_KEY" = "change-me-greenie"
        "EVERSHADE_ENCRYPTION_KEY" = "change-me-encryption-key"
    }
    foreach ($key in $checkKeys.Keys) {
        $defaultValue = $checkKeys[$key]
        $actualValue = $envVars[$key]
        if ($actualValue -eq $defaultValue) {
            Write-Host "[WARN] $key is using the default value (ok for desktop mode)" -ForegroundColor Yellow
            $hasDefaultKeys = $true
        }
    }
    if ($hasDefaultKeys) {
        Write-Host "[WARN] Default keys detected — fine for local development, insecure for production" -ForegroundColor Yellow
    }
}

# Check required service directories based on profile
$manifest = Get-Content "version-manifest.json" | ConvertFrom-Json
$profileServices = $manifest.profiles.$Profile
$requiredDirs = @($profileServices | Where-Object { $_ -notin @("redis", "ollama", "caddy") })

$missingDirs = $false
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path "services/$dir")) {
        Write-Host "[XX] ERROR: Directory 'services/$dir' not found." -ForegroundColor Red
        Write-Host "[WARN] Run .\install.ps1 -Profile $Profile to install missing services." -ForegroundColor Yellow
        $missingDirs = $true
    }
}

if ($missingDirs) {
    exit 1
}
Write-Host "[OK] Required service directories found" -ForegroundColor Green

# Validate docker-compose.yml
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[XX] ERROR: docker-compose.yml not found." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] docker-compose.yml found" -ForegroundColor Green

# Validate docker-compose configuration
try {
    docker compose --profile $Profile config --quiet 2>$null
    Write-Host "[OK] Docker Compose configuration valid" -ForegroundColor Green
} catch {
    Write-Host "[XX] ERROR: Invalid docker-compose configuration for profile '$Profile'." -ForegroundColor Red
    exit 1
}

# Check if Junie CLI is available (for code agents)
try {
    $junieVersion = junie --version 2>$null
    if ($junieVersion) {
        Write-Host "[OK] Junie CLI is available" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Junie CLI not found on PATH — code agents will not work" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Junie CLI not found on PATH — code agents will not work" -ForegroundColor Yellow
}

# Start services
Write-Host ""
Write-Host "Starting services with profile: $Profile" -ForegroundColor Cyan
Write-Host ""

docker compose --profile $Profile up -d

Write-Host ""
Write-Host "[OK] Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Greenie:    http://localhost:8080"
Write-Host "  Slammer:    http://localhost:5173"
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor Cyan
Write-Host "  Swagger:   http://localhost:8080/docs"
Write-Host "  ReDoc:     http://localhost:8080/redoc"
Write-Host ""
Write-Host "To stop services:  .\stop.ps1" -ForegroundColor Gray
Write-Host "To view logs:      docker compose logs -f" -ForegroundColor Gray
Write-Host ""
