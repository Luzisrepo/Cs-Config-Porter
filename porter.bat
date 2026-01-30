@echo off
title CS:GO/CS2 Settings Porter
color 0A

echo ========================================
echo   CS:GO/CS2 Settings Porter (Batch)
echo ========================================

set STEAM_PATH=C:\Program Files (x86)\Steam\userdata
set CFG_PATH=730\local\cfg

:menu
cls
echo.
echo 1. List Steam accounts
echo 2. Port settings between accounts
echo 3. Create backup
echo 4. Restore backup
echo 5. Exit
echo.
set /p choice="Select option (1-5): "

if "%choice%"=="1" goto list
if "%choice%"=="2" goto port
if "%choice%"=="3" goto backup
if "%choice%"=="4" goto restore
if "%choice%"=="5" exit
goto menu

:list
cls
echo.
echo Steam accounts with CS configs:
echo.
dir "%STEAM_PATH%" /AD /B | findstr "^[0-9][0-9]*$"
echo.
pause
goto menu

:port
cls
echo.
set /p SOURCE_ID=Enter SOURCE account ID: 
set /p TARGET_ID=Enter TARGET account ID: 

if not exist "%STEAM_PATH%\%SOURCE_ID%\%CFG_PATH%" (
    echo Source account not found!
    pause
    goto menu
)

if not exist "%STEAM_PATH%\%TARGET_ID%" mkdir "%STEAM_PATH%\%TARGET_ID%"
if not exist "%STEAM_PATH%\%TARGET_ID%\730" mkdir "%STEAM_PATH%\%TARGET_ID%\730"
if not exist "%STEAM_PATH%\%TARGET_ID%\730\local" mkdir "%STEAM_PATH%\%TARGET_ID%\730\local"
if not exist "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%" mkdir "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%"

echo.
echo Creating backup of target account...
xcopy "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%" "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%_backup_%date:/=-%_%time::=-%" /E /I /H /Y >nul

echo Copying config files...
del /Q "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%\*.*" >nul 2>&1
xcopy "%STEAM_PATH%\%SOURCE_ID%\%CFG_PATH%\*.*" "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%" /E /I /H /Y >nul

echo.
echo ✓ Settings copied from %SOURCE_ID% to %TARGET_ID%
echo.
echo Note: You may need to restart CS:GO/CS2 for changes to take effect.
echo.
pause
goto menu

:backup
cls
echo.
set /p ACCOUNT_ID=Enter account ID to backup: 

if not exist "%STEAM_PATH%\%ACCOUNT_ID%\%CFG_PATH%" (
    echo Account not found!
    pause
    goto menu
)

set BACKUP_DIR="%STEAM_PATH%\..\cs_backups"
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

xcopy "%STEAM_PATH%\%ACCOUNT_ID%\%CFG_PATH%" "%BACKUP_DIR%\%ACCOUNT_ID%_%date:/=-%_%time::=-%" /E /I /H /Y >nul

echo.
echo ✓ Backup created successfully!
echo.
pause
goto menu

:restore
cls
echo.
echo Available backups in %STEAM_PATH%\..\cs_backups\
echo.
dir "%STEAM_PATH%\..\cs_backups" /AD /B
echo.
set /p BACKUP_NAME=Enter backup folder name: 
set /p TARGET_ID=Enter target account ID: 

if not exist "%STEAM_PATH%\..\cs_backups\%BACKUP_NAME%" (
    echo Backup not found!
    pause
    goto menu
)

if not exist "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%" mkdir "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%"

echo.
echo Restoring backup...
del /Q "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%\*.*" >nul 2>&1
xcopy "%STEAM_PATH%\..\cs_backups\%BACKUP_NAME%\*.*" "%STEAM_PATH%\%TARGET_ID%\%CFG_PATH%" /E /I /H /Y >nul

echo.
echo ✓ Backup restored to account %TARGET_ID%
echo.
pause
goto menu