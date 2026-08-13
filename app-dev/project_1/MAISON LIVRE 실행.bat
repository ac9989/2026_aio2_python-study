@echo off
cd /d "%~dp0"
echo ================================
echo   MAISON LIVRE STARTING...
echo ================================
echo.

if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" launcher.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" launcher.py
) else (
    python launcher.py
)

echo.
echo ================================
echo MAISON LIVRE stopped
echo ================================
pause
