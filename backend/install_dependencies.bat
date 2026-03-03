@echo off
echo ========================================
echo   MINDWELL - DEPENDENCY INSTALLATION
echo ========================================
echo.
echo This will install all required Python packages
echo for the MindWell Emotional Wellness Web App
echo.
pause
echo.
echo Installing dependencies...
echo.

pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo.
echo Next steps:
echo 1. Make sure you have a .env file with GEMINI_API_KEY
echo    (see .env.example for reference)
echo 2. Run start_web.bat to launch the web app
echo.
echo ========================================
pause
