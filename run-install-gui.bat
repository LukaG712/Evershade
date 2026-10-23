@echo off
REM Evershade — GUI Installer Launcher (Windows)
REM Launches the visual installer wizard for Evershade on Windows.
REM Requires Python 3.6+ with Tkinter (included by default).

title Evershade Installer

echo.
echo ========================================
echo   Evershade GUI Installer
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.6+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo [OK] Python detected: %PYTHON_VER%

REM Check if Tkinter is available
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Tkinter is not available.
    echo.
    echo Please reinstall Python from python.org and ensure Tkinter is included.
    echo.
    pause
    exit /b 1
)

echo [OK] Tkinter is available.
echo.
echo Launching Evershade Installer...
echo.

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Launch the GUI installer
python install-gui-win.py

REM If the installer exits with an error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installer exited with an error.
    pause
)
