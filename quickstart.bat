@echo off
REM Quick Start Script for Job Application Automation
REM Windows Batch File

echo.
echo ========================================
echo  Job Application Automation System
echo  Quick Start Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.10+ is installed
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment already exists
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Install Playwright browsers
echo [4/5] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright installation had issues
    echo You may need to run: playwright install chromium --force
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo [5/5] Creating .env file from template...
    copy .env.template .env
    echo.
    echo ========================================
    echo  IMPORTANT: Configure your settings!
    echo ========================================
    echo.
    echo Please edit .env file and add:
    echo  - Your personal information
    echo  - OpenAI API key
    echo  - Job filtering keywords
    echo.
) else (
    echo [5/5] .env file already exists
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo  1. Edit .env file with your details
echo  2. Place your resume in data/resumes/base_resume.pdf
echo  3. Edit data/companies.csv with target companies
echo  4. Run: python main.py --test --limit 3
echo.
echo For detailed instructions, see:
echo  - INSTALLATION.md
echo  - USAGE.md
echo.

pause
