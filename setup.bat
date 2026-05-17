@echo off
echo ============================================
echo   AI Resume Analyzer v3 - Setup Script
echo   Built by Alisha Saleem - UMT Lahore
echo ============================================
echo.
echo [1/4] Creating virtual environment...
python -m venv venv
echo [2/4] Activating virtual environment...
call venv\Scripts\activate
echo [3/4] Installing dependencies...
pip install -r requirements.txt
echo [4/4] Done!
echo.
echo ============================================
echo  NEXT STEPS:
echo  1. Place Resume.csv in:  data\resume\
echo  2. Place category folders in:  data\data\
echo     (ENGINEERING, MEDICAL, ACCOUNTING etc.)
echo  3. Double-click run.bat to start the app
echo ============================================
pause
