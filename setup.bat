@echo off
REM One-time setup on a new Windows PC. Needs Python 3.13 and internet (first time only).
cd /d "%~dp0"

set PY=
py -3.13 --version >nul 2>&1 && set PY=py -3.13
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo [ERROR] Python 3.13 not found. Install Python 3.13 and check "Add python.exe to PATH".
  pause & exit /b 1
)
%PY% --version | findstr /b "Python 3.13" >nul || echo [WARN] Only Python 3.13 was verified. Continuing anyway.

if not exist .venv\Scripts\python.exe (
  echo Creating .venv ...
  %PY% -m venv .venv || (echo [ERROR] venv creation failed & pause & exit /b 1)
)

echo Installing libraries (can take several minutes) ...
.venv\Scripts\python.exe -m pip install -r requirements-ocr.txt || (echo [ERROR] pip install failed & pause & exit /b 1)

REM Skip the model download if both model files were already copied into models\
if exist models\craft_mlt_25k.pth if exist models\korean_g2.pth (
  echo OCR models already in models\ - skipping download.
) else (
  echo Downloading OCR models, first time only ...
  .venv\Scripts\python.exe scripts\prepare_models.py || (echo [ERROR] model download failed & pause & exit /b 1)
)

echo.
echo Setup done. Start the app by double-clicking run.bat
pause
