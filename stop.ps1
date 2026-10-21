# Unified Workflow — Stop Script (Windows PowerShell)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "Stopping all services..." -ForegroundColor Cyan

docker compose down

Write-Host "Services stopped." -ForegroundColor Green
Write-Host ""
Write-Host "To remove volumes and data: docker compose down -v" -ForegroundColor Gray
Write-Host "To start again: .\start.ps1" -ForegroundColor Gray
