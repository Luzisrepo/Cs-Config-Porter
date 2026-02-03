@echo off
echo ============================================
echo CS:GO Settings Porter - Build Script
echo ============================================
echo.

:: Set the current directory as the script directory
cd /d "%~dp0"

echo Step 1: Checking Python installation...
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    echo.
    echo Trying to find Python manually...
    
    :: Check common Python installation locations
    if exist "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe" (
        set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe
    ) else if exist "C:\Program Files\Python313\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python313\python.exe
    ) else if exist "C:\Program Files\Python312\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python312\python.exe
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python311\python.exe
    ) else if exist "C:\Program Files\Python310\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python310\python.exe
    ) else if exist "C:\Program Files\Python39\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python39\python.exe
    ) else if exist "C:\Program Files\Python38\python.exe" (
        set PYTHON_PATH=C:\Program Files\Python38\python.exe
    ) else (
        echo ERROR: Could not find Python!
        echo Please install Python from https://python.org
        pause
        exit /b 1
    )
    echo Found Python at: %PYTHON_PATH%
) else (
    set PYTHON_PATH=python
)

echo.
echo Step 2: Checking PyInstaller installation...
"%PYTHON_PATH%" -c "import pyinstaller; print('✓ PyInstaller is installed')" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    "%PYTHON_PATH%" -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "CSGOSettingsPorter.spec" del CSGOSettingsPorter.spec

echo.
echo Step 4: Building executable...
echo Using Python: %PYTHON_PATH%

"%PYTHON_PATH%" -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name="CSGOSettingsPorter" ^
    --clean ^
    --noconfirm ^
    csporter.py

echo.
if exist "dist\CSGOSettingsPorter.exe" (
    echo ============================================
    echo ✅ BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo 📁 Executable: %cd%\dist\CSGOSettingsPorter.exe
    echo.
    echo 🚀 To run: Double-click the .exe file
    echo 📦 Size: 
    for %%F in ("dist\CSGOSettingsPorter.exe") do echo    %%F - %%~zF bytes
) else (
    echo ============================================
    echo ❌ BUILD FAILED!
    echo ============================================
    echo.
    echo Possible issues:
    echo 1. Try running Command Prompt as Administrator
    echo 2. Check if antivirus is blocking PyInstaller
    echo 3. Try: python -m pip uninstall pyinstaller
    echo 4. Then: python -m pip install pyinstaller
)

echo.
pause