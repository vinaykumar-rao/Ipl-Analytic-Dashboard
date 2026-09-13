@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "PYTHON=python") else (set "PYTHON=py")
if not exist .venv\Scripts\python.exe (
    %PYTHON% -m venv .venv
    if errorlevel 1 goto fail
)
if not exist .venv\installed.txt (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto fail
    echo installed>.venv\installed.txt
)
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo Install Python 3.12 or newer from python.org and enable Add Python to PATH.
echo Check the error above. Internet is required for the first dependency installation.
pause
exit /b 1
