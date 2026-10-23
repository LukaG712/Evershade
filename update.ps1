# Evershade — Update Script (Windows PowerShell)
# Pulls the latest version-manifest.json and updates all service repositories
# to their pinned commits. Safe to re-run.
#
# Usage:
#   .\update.ps1                  # Update with current profile (standard)
#   .\update.ps1 -Profile full    # Update with a specific profile
#   .\update.ps1 -Force           # Force update even if already up to date
#   .\update.ps1 -PullMain        # Also pull latest changes from main Evershade repo

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$PullMain,
    [ValidateSet("minimal", "standard", "full")]
    [string]$Profile = "standard"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  Evershade Update Script                                     ║" -ForegroundColor Blue
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

# Pull latest changes from main Evershade repo
if ($PullMain) {
    Write-Host ""
    Write-Host "[ARROW] Pulling latest changes from main Evershade repository..." -ForegroundColor Cyan
    if (Test-Path ".git") {
        try {
            git pull 2>&1 | Out-Null
            Write-Host "[OK] Main repository updated" -ForegroundColor Green
        } catch {
            Write-Host "[WARN] No changes to pull or pull failed (this is okay if already up to date)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[WARN] Not a git repository — skipping main repo pull" -ForegroundColor Yellow
    }
}

# Read version manifest
if (-not (Test-Path "version-manifest.json")) {
    Write-Host "[XX] ERROR: version-manifest.json not found. Are you in the Evershade root directory?" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] version-manifest.json found" -ForegroundColor Green

# Extract manifest version for display
$manifest = Get-Content "version-manifest.json" | ConvertFrom-Json
$manifestVersion = $manifest.version
Write-Host "[OK] Manifest version: $manifestVersion" -ForegroundColor Green

# Extract service list based on profile
$profileServices = $manifest.profiles.$Profile

# Filter out infrastructure services
$services = @($profileServices | Where-Object { $_ -notin @("redis", "ollama", "caddy") })

if ($services.Count -eq 0) {
    Write-Host "[XX] ERROR: No services found for profile '$Profile'." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Profile: $Profile" -ForegroundColor Green
Write-Host "[OK] Services to check: $($services.Count)" -ForegroundColor Green
Write-Host ""

$updated = @()
$skipped = @()
$failed = @()
$missing = @()

foreach ($service in $services) {
    $serviceInfo = $manifest.services.$service
    $repoUrl = $serviceInfo.repository
    $commit = $serviceInfo.commit
    if (-not $repoUrl) {
        $repoUrl = "https://github.com/LukaG712/$service"
    }

    $serviceDir = "services/$service"

    # Check if directory exists
    if (-not (Test-Path $serviceDir)) {
        Write-Host "[WARN] $service directory not found — skipping. Run install.ps1 to clone it first." -ForegroundColor Yellow
        $missing += $service
        continue
    }

    # Check if it's a valid git repo
    if (-not (Test-Path "$serviceDir/.git")) {
        Write-Host "[WARN] $service exists but is not a git repo — skipping." -ForegroundColor Yellow
        $skipped += $service
        continue
    }

    # Get current commit
    $currentCommit = & git -C $serviceDir rev-parse --short=7 HEAD 2>$null

    # Check if already at correct commit
    if ($commit -and $currentCommit -eq $commit -and -not $Force) {
        Write-Host "[OK] $service already at correct commit ($commit) — skipping" -ForegroundColor Green
        $skipped += $service
        continue
    }

    # Fetch latest changes
    Write-Host "[ARROW] Updating $service (current: $currentCommit, target: $commit)..." -ForegroundColor Cyan

    $updateSuccess = $false
    try {
        & git -C $serviceDir fetch --depth 100 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Fetch failed"
        }

        if ($commit) {
            # Checkout the pinned commit
            $checkoutResult = & git -C $serviceDir checkout $commit 2>&1
            if ($LASTEXITCODE -eq 0) {
                $newCommit = & git -C $serviceDir rev-parse --short=7 HEAD
                Write-Host "[OK] $service updated: $currentCommit → $newCommit" -ForegroundColor Green
                $updateSuccess = $true
            } else {
                Write-Host "[XX] Failed to checkout commit $commit for $service" -ForegroundColor Red
                Write-Host "      The pinned commit may not exist or the repo may have changed." -ForegroundColor Yellow
            }
        } else {
            # No pinned commit, just pull latest
            $pullResult = & git -C $serviceDir pull --ff-only 2>&1
            if ($LASTEXITCODE -eq 0) {
                $newCommit = & git -C $serviceDir rev-parse --short=7 HEAD
                if ($newCommit -ne $currentCommit) {
                    Write-Host "[OK] $service pulled latest: $currentCommit → $newCommit" -ForegroundColor Green
                } else {
                    Write-Host "[OK] $service already up to date ($newCommit)" -ForegroundColor Green
                }
                $updateSuccess = $true
            } else {
                Write-Host "[WARN] Could not fast-forward $service (no pinned commit) — skipping" -ForegroundColor Yellow
                $skipped += $service
                continue
            }
        }
    } catch {
        Write-Host "[XX] Failed to fetch updates for $service : $_" -ForegroundColor Red
    }

    if ($updateSuccess) {
        $updated += $service
    } else {
        $failed += $service
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "[OK] Updated: $($updated.Count) services" -ForegroundColor Green

if ($skipped.Count -gt 0) {
    Write-Host "[OK] Up to date: $($skipped.Count) services" -ForegroundColor Green
}

if ($missing.Count -gt 0) {
    Write-Host "[WARN] Missing (not cloned): $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "      Run .\install.ps1 -Profile $Profile to clone missing services." -ForegroundColor Yellow
}

if ($failed.Count -gt 0) {
    Write-Host "[XX] Failed: $($failed -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Update incomplete. Possible causes:" -ForegroundColor Red
    Write-Host "  - Network connectivity issues" -ForegroundColor White
    Write-Host "  - Repository not found or private" -ForegroundColor White
    Write-Host "  - Local modifications conflicting with update" -ForegroundColor White
    Write-Host "Try re-running with -Force to retry." -ForegroundColor Yellow
    exit 1
}

# Check for new services in manifest that aren't cloned
if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARN] New services detected in manifest but not yet cloned." -ForegroundColor Yellow
    Write-Host "      Run .\install.ps1 -Profile $Profile to install them." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Update complete!                                           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Updated services:"
foreach ($svc in $updated) {
    Write-Host "  - $svc"
}
Write-Host ""
Write-Host "To apply changes, restart your services:"
Write-Host "  .\stop.ps1; .\start.ps1 -Profile $Profile"
Write-Host ""
