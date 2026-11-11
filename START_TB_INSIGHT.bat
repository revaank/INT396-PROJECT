@echo off
setlocal
cd /d "%~dp0"
set "VENV=%~dp0.venv"
set "PY=%VENV%\Scripts\python.exe"
set "BOOTSTRAP="
where py >nul 2>nul
if not errorlevel 1 set "BOOTSTRAP=py -3"
if not defined BOOTSTRAP (
  where python >nul 2>nul
  if not errorlevel 1 set "BOOTSTRAP=python"
)
if not defined BOOTSTRAP (
  echo Python was not found. Installing Python 3.12 for this Windows user with winget...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Automatic Python setup is unavailable because winget is not installed.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/ and run this file again.
    pause
    exit /b 1
  )
  winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 goto setup_error
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "BOOTSTRAP=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  if not defined BOOTSTRAP if exist "%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe" set "BOOTSTRAP=%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe"
)
if not defined BOOTSTRAP goto setup_error
if not exist "%PY%" (
  echo Setting up TB Insight for the first time...
  %BOOTSTRAP% -m venv "%VENV%"
  if errorlevel 1 goto setup_error
)
if not exist "%VENV%\.deps_installed" (
  echo Installing application packages. Internet access is needed the first time.
  "%PY%" -m pip install --upgrade pip
  if errorlevel 1 goto setup_error
  "%PY%" -m pip install -r requirements.txt
  if errorlevel 1 goto setup_error
  echo ready>"%VENV%\.deps_installed"
)
if not exist "data\raw\dataful_20833\india_admin1.geojson" (
  echo Getting the India state boundary file for the interactive map...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri 'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1_simplified.geojson' -OutFile 'data\raw\dataful_20833\india_admin1.geojson' -TimeoutSec 45 } catch { Write-Host 'Map boundary download unavailable. The rest of the dashboard will still open.' }"
)
"%PY%" -m streamlit run app\main.py
exit /b %errorlevel%
:setup_error
echo Setup did not complete. Check your Python installation and internet connection, then run this file again.
pause
exit /b 1
