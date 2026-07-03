@echo off
REM ================================================================
REM  Beverage Detection System - Windows Launcher (Improved)
REM  Automatically sets up and runs the application with virtual env
REM ================================================================

REM Change to the script's directory to ensure proper context
cd /d "%~dp0"

title Beverage Detection System - Setup and Launch

echo.
echo ================================================================
echo   BEVERAGE DETECTION SYSTEM v1.0 - IMPROVED LAUNCHER
echo   Windows Launcher with Virtual Environment
echo ================================================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start logging setup process
echo [%date% %time%] Starting setup process >> logs\install.log

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.10 or 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    echo [%date% %time%] ERROR: Python not found >> logs\install.log
    pause
    exit /b 1
)

REM Check Python version for torch compatibility
echo [CHECK] Verifying Python version...
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Convert to numbers for comparison
set /a PYTHON_MAJOR=%MAJOR%
set /a PYTHON_MINOR=%MINOR%

REM Check if Python version is 3.10 or 3.11 (compatible with torch)
if %PYTHON_MAJOR% neq 3 (
    echo [ERROR] Unsupported Python major version: %PYTHON_VERSION%
    echo.
    echo This application requires Python 3.10 or 3.11 for torch compatibility.
    echo Please install a compatible Python version.
    echo.
    echo [%date% %time%] ERROR: Unsupported Python major version: %PYTHON_VERSION% >> logs\install.log
    pause
    exit /b 1
)

if %PYTHON_MINOR% lss 10 (
    echo [ERROR] Unsupported Python minor version: %PYTHON_VERSION%
    echo.
    echo This application requires Python 3.10 or 3.11 for torch compatibility.
    echo Please install a compatible Python version.
    echo.
    echo [%date% %time%] ERROR: Unsupported Python minor version: %PYTHON_VERSION% >> logs\install.log
    pause
    exit /b 1
)

if %PYTHON_MINOR% gtr 11 (
    echo [ERROR] Unsupported Python minor version: %PYTHON_VERSION%
    echo.
    echo This application requires Python 3.10 or 3.11 for torch compatibility.
    echo Please install a compatible Python version.
    echo.
    echo [%date% %time%] ERROR: Unsupported Python minor version: %PYTHON_VERSION% >> logs\install.log
    pause
    exit /b 1
)

echo [OK] Python %PYTHON_VERSION% found and is compatible with torch
echo [%date% %time%] Python %PYTHON_VERSION% verified >> logs\install.log

REM Create virtual environment if it doesn't exist
echo.
echo [SETUP] Checking for virtual environment...
if not exist ".venv" goto create_venv
echo [OK] Virtual environment already exists
goto activate_venv

:create_venv
echo [SETUP] Creating virtual environment (.venv)...
echo [%date% %time%] Creating virtual environment >> logs\install.log
python -m venv .venv

if %errorlevel% equ 0 goto venv_success
echo.
echo [ERROR] Failed to create virtual environment!
echo.
echo Possible causes:
echo   1. Insufficient disk space
echo   2. Permission issues
echo   3. Antivirus software blocking Python
echo.
echo [%date% %time%] ERROR: Failed to create virtual environment >> logs\install.log
pause
exit /b 1

:venv_success
echo [OK] Virtual environment created successfully!

:activate_venv

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call .venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    echo.
    echo [%date% %time%] ERROR: Failed to activate virtual environment >> logs\install.log
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo [%date% %time%] Virtual environment activated >> logs\install.log

REM Upgrade pip in virtual environment
echo [SETUP] Upgrading pip in virtual environment...
python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip!
    echo.
    echo [%date% %time%] ERROR: Failed to upgrade pip >> logs\install.log
    pause
    exit /b 1
)

echo [OK] Pip upgraded successfully
echo [%date% %time%] Pip upgraded >> logs\install.log

REM Check if requirements are already installed
echo.
echo [SETUP] Checking if packages are already installed...
python -c "import cv2, numpy, PIL, ultralytics, torch, torchvision, ttkbootstrap, pandas, yaml, requests, tqdm" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] All required packages already installed
    goto skip_install
)

echo [SETUP] Installing required packages from requirements.txt...
echo This will take 5-10 minutes on first run...
echo [%date% %time%] Starting package installation >> logs\install.log

python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install packages!
    echo.
    echo Troubleshooting tips:
    echo   1. Check your internet connection
    echo   2. Ensure you have Python 3.10 or 3.11 (torch compatibility)
    echo   3. If behind a corporate firewall, configure proxy settings
    echo   4. Try running as administrator
    echo   5. Clear pip cache: python -m pip cache purge
    echo.
    echo [%date% %time%] ERROR: Package installation failed >> logs\install.log
    pause
    exit /b 1
)

echo.
echo [OK] All packages installed successfully!
echo [%date% %time%] All packages installed >> logs\install.log

:skip_install

echo.
echo ================================================================
echo   Starting Application...
echo ================================================================
echo.

REM Run the application normally (no redirection to allow GUI)
echo [%date% %time%] Starting application main.py >> logs\app.log
start "" python main.py
set APP_EXIT_CODE=0

echo.
echo [OK] Application started successfully!
echo The beverage detection system should now be running.
echo.
echo [%date% %time%] Application started successfully >> logs\app.log

echo [%date% %time%] Application launched in background >> logs\app.log

echo.
echo ================================================================
echo   SETUP COMPLETE
echo ================================================================
echo.
echo The Beverage Detection System is now running in the background.
echo You should see the application window shortly.
echo.
echo To close the application, use the window's close button.
echo.

echo Press any key to close this setup window...
