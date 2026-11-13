@echo off
REM Start the app. Run setup.bat first on a new PC.
REM Local only:     run.bat
REM LAN demo (phones on same Wi-Fi can open http://<this PC IP>:8518):  run.bat lan
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv not found. Run setup.bat first.
  pause & exit /b 1
)

set ADDR=127.0.0.1
if /i "%1"=="lan" set ADDR=0.0.0.0

echo Open http://127.0.0.1:8518  (close this window to stop)
.venv\Scripts\python.exe -m streamlit run app.py --server.address %ADDR% --server.port 8518 --browser.gatherUsageStats false
pause
