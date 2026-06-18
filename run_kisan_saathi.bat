@echo off
title Kisan Saathi Launcher
echo ==================================================
echo           🌾 STARTING KISAN SAATHI 🌾
echo ==================================================
echo.

:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

:: Check and activate virtual environment
if exist venv\Scripts\activate.bat (
    echo [1/2] Activating virtual environment venv...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo [1/2] Activating virtual environment dot-venv...
    call .venv\Scripts\activate.bat
) else (
    echo [!] WARNING: No virtual environment folder found. Running with global python.
)

echo.
echo [2/2] Launching Streamlit interface...
echo.
streamlit run app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Launcher exited with an error.
    pause
)
