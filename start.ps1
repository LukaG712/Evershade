# Unified Workflow — Startup Script (Windows PowerShell)
# Validates configuration, checks dependencies, and starts all services.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Unified Workflow — Starting Services" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check Docker
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "[✓] Docker is available: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] ERROR: Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker compose version 2>$null
    Write-Host "[✓] Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "[✗] ERROR: Docker Compose is not available." -ForegroundColor Red
    exit 1
}

# Create .env from .env.example if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[!] .env not found. Copying from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[!] Please edit .env with your API keys before starting." -ForegroundColor Yellow
        Write-Host "[!] Press Ctrl+C to edit, or Enter to continue with defaults..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "[✗] ERROR: Neither .env nor .env.example found." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[✓] .env file found" -ForegroundColor Green

# Check required directories
foreach ($dir in @("Evershade Valley", "Polter", "Spectra")) {
    if (-not (Test-Path $dir)) {
        Write-Host "[✗] ERROR: Directory '$dir' not found." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[✓] All service directories found" -ForegroundColor Green

# Validate docker-compose.yml
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[✗] ERROR: docker-compose.yml not found." -ForegroundColor Red
    exit 1
}

Write-Host "[✓] docker-compose.yml found" -ForegroundColor Green

# Check if Junie CLI is available (for code agents)
try {
    $junieVersion = junie --version 2>$null
    if ($junieVersion) {
        Write-Host "[✓] Junie CLI is available" -ForegroundColor Green
    } else {
        Write-Host "[!] Junie CLI not found on PATH — code agents will not work" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Junie CLI not found on PATH — code agents will not work" -ForegroundColor Yellow
}

# Start services
Write-Host ""
Write-Host "Starting all services..." -ForegroundColor Cyan
Write-Host ""

docker compose up -d

Write-Host ""
Write-Host "[✓] Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Evershade Valley:  http://localhost:8080"
Write-Host "  Polter:  http://localhost:8000"
Write-Host "  Spectra: http://localhost:3000"
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor Cyan
Write-Host "  Swagger:   http://localhost:8080/docs"
Write-Host "  ReDoc:     http://localhost:8080/redoc"
Write-Host ""
Write-Host "To stop services:  .\stop.ps1" -ForegroundColor Gray
Write-Host "To view logs:      docker compose logs -f" -ForegroundColor Gray
Write-Host ""
