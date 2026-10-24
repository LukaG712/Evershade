# Evershade — Uninstall Script (Windows)
# Removes all Evershade components: Docker containers, desktop shortcut.
# Run as Administrator: Start-Process powershell -Verb RunAs -ArgumentList "-File uninstall.ps1"
#
# WARNING: This will stop and remove all Evershade Docker containers and data.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Continue"

$RemoveDir = $false
$RemoveData = $false
$Force = $false

# Parse arguments
param(
    [Switch]$RemoveDir,
    [Switch]$RemoveData,
    [Switch]$Force,
    [Switch]$Help
)

Write-Host ""
Write-Host "[INFO] ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "[INFO] ║  Evershade Uninstaller                                      ║" -ForegroundColor Blue
Write-Host "[INFO] ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

if ($Help) {
    Write-Host "Usage: powershell -ExecutionPolicy Bypass -File uninstall.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -RemoveDir     Remove the Evershade installation directory"
    Write-Host "  -RemoveData    Remove Docker volumes (persistent data)"
    Write-Host "  -Force         Skip confirmation prompts"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "WARNING: This will stop and remove all Evershade Docker containers."
    Write-Host "Data in Docker volumes will be preserved unless -RemoveData is used."
    exit 0
}

# Detect install directory
$InstallDir = $null

# Try common locations
$UserName = [System.Environment]::UserName
$HomePath = [System.Environment]::GetFolderPath("UserProfile")

$commonPaths = @(
    "$HomePath\Evershade",
    "C:\Evershade"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        $InstallDir = $path
        break
    }
}

if (-not $InstallDir) {
    Write-Host "[WARN] Could not detect Evershade installation directory." -ForegroundColor Yellow
    Write-Host "[WARN] Please specify it manually." -ForegroundColor Yellow
    Write-Host ""
    $InstallDir = Read-Host "Installation directory"
}

if (-not (Test-Path $InstallDir)) {
    Write-Host "[XX] ERROR: Directory '$InstallDir' does not exist." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Installation directory: $InstallDir" -ForegroundColor Green
Write-Host ""

# Confirmation prompt
if (-not $Force) {
    Write-Host "[WARN] The following components will be removed:" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "  [x] Docker containers and networks"
    
    if ($RemoveDir) {
        Write-Host "  [x] Installation directory: $InstallDir"
    }
    
    if ($RemoveData) {
        Write-Host "  [x] Docker volumes (all persistent data)"
    }
    
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to continue? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "[OK] Uninstall cancelled." -ForegroundColor Green
        exit 0
    }
}

Write-Host ""

# Step 1: Stop Docker containers
Write-Host "[->] Stopping Evershade Docker containers..." -ForegroundColor Blue
$composeFile = Join-Path $InstallDir "docker-compose.yml"
if (Test-Path $composeFile) {
    Push-Location $InstallDir
    try {
        $result = docker compose down --remove-orphans 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker containers stopped" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Failed to stop Docker containers (they may already be stopped)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARN] Docker compose not available or containers already stopped" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[WARN] docker-compose.yml not found, skipping Docker cleanup" -ForegroundColor Yellow
}

# Step 2: Remove Docker volumes (optional)
if ($RemoveData) {
    Write-Host ""
    Write-Host "[->] Removing Docker volumes..." -ForegroundColor Blue
    if (Test-Path $composeFile) {
        Push-Location $InstallDir
        try {
            $result = docker compose down -v 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Docker volumes removed" -ForegroundColor Green
            } else {
                Write-Host "[WARN] Failed to remove Docker volumes" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[WARN] Failed to remove Docker volumes" -ForegroundColor Yellow
        } finally {
            Pop-Location
        }
    }
}

# Step 3: Remove desktop shortcut (if created)
Write-Host ""
Write-Host "[->] Removing desktop shortcut..." -ForegroundColor Blue
$desktopPath = [System.Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Evershade.lnk"
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "[OK] Desktop shortcut removed" -ForegroundColor Green
} else {
    Write-Host "[WARN] No desktop shortcut found" -ForegroundColor Yellow
}

# Step 4: Remove installation directory (optional)
if ($RemoveDir) {
    Write-Host ""
    Write-Host "[->] Removing installation directory: $InstallDir" -ForegroundColor Blue
    Remove-Item $InstallDir -Recurse -Force
    Write-Host "[OK] Installation directory removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "[OK] ║  Uninstall complete!                                        ║" -ForegroundColor Green
Write-Host "[OK] ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if (-not $RemoveDir) {
    Write-Host "[WARN] Installation directory preserved at: $InstallDir" -ForegroundColor Yellow
    Write-Host "[WARN] To remove it manually: Remove-Item '$InstallDir' -Recurse -Force" -ForegroundColor Yellow
}

if (-not $RemoveData) {
    Write-Host "[WARN] Docker volumes preserved. To remove them:" -ForegroundColor Yellow
    Write-Host "[WARN]   cd $InstallDir ; docker compose down -v" -ForegroundColor Yellow
}

Write-Host ""
