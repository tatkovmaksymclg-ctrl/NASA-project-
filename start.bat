@echo off
cd /d "%~dp0"
echo ==========================================
echo        ASTROMED - MISSION MONITORING
echo ==========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python and try again.
  pause
  exit /b 1
)
echo Installing required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package installation failed.
  pause
  exit /b 1
)
echo Starting AstroMed...
python main.py
pause
