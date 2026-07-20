@echo off
setlocal

echo === CS:GO / CS2 Settings Porter - Build ===

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH. Install it from https://www.python.org/downloads/
    exit /b 1
)

echo Installing/upgrading dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist CSGOSettingsPorter.spec del /q CSGOSettingsPorter.spec

echo Building executable...
pyinstaller --onefile --windowed --name="CSGOSettingsPorter" --clean --noconfirm main.py

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete: dist\CSGOSettingsPorter.exe
endlocal
