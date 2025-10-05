@echo off
echo Starting Advanced Hand Control System...
echo.
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application crashed or failed to start!
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo - Missing dependencies (run install.bat)
    echo - Camera not connected or in use
    echo - Microphone permissions
    echo.
    pause
)
