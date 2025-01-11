@echo off
echo Starting DarkSheets...
echo Please make sure Tor Browser is installed and running.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    echo You can download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Set PYTHONPATH to include the src directory
set "PYTHONPATH=%SCRIPT_DIR%;%SCRIPT_DIR%\src;%PYTHONPATH%"

REM Install requirements if needed
echo Checking/installing requirements...
python -m pip install -r "%SCRIPT_DIR%\requirements.txt"

REM Run the application
echo Starting DarkSheets application...
python "%SCRIPT_DIR%\run_darksheets.py"

if errorlevel 1 (
    echo.
    echo Error running DarkSheets. Here are the details:
    python "%SCRIPT_DIR%\run_darksheets.py"
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo.
echo DarkSheets closed successfully.
pause
