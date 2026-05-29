@echo off
REM Pokedex Knob Installer - Windows. Doppelklick.
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 fehlt.
    echo Bitte von https://www.python.org/downloads/ installieren
    echo   - beim Setup "Add python.exe to PATH" anhaken!
    echo Danach diesen Installer erneut doppelklicken.
    pause
    exit /b 1
)

set "VENV=%USERPROFILE%\.pokedex-installer\venv"
if not exist "%VENV%\Scripts\python.exe" (
    echo Richte Tools ein ^(einmalig, ~20 MB^)...
    python -m venv "%VENV%" || ( echo venv-Fehler & pause & exit /b 1 )
    "%VENV%\Scripts\python" -m pip install --quiet --upgrade pip
    "%VENV%\Scripts\pip" install --quiet esptool pyserial pillow requests || (
        echo pip-Fehler ^(Internet?^) & pause & exit /b 1 )
)

cls
"%VENV%\Scripts\python" install.py
echo.
pause
endlocal
