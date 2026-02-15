@echo off
REM Simple run script for Job Application Automation

echo.
echo ========================================
echo  Job Application Automation System
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python main.py %*

pause
