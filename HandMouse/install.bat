@echo off
echo ========================================
echo Advanced Hand Control System Installation
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Installing required packages...
echo This may take several minutes...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Installation failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Creating configuration files...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist assets\icons mkdir assets\icons
if not exist assets\sounds mkdir assets\sounds
if not exist assets\themes mkdir assets\themes
if not exist data mkdir data

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run the application using:
echo   python main.py
echo or
echo   run.bat
echo.
pause
