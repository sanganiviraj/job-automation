#!/bin/bash
# Quick Start Script for Job Application Automation
# Linux/Mac Shell Script

echo ""
echo "========================================"
echo " Job Application Automation System"
echo " Quick Start Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[1/5] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please ensure Python 3.10+ is installed"
        exit 1
    fi
else
    echo "[1/5] Virtual environment already exists"
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Install Playwright browsers
echo "[4/5] Installing Playwright browsers..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "WARNING: Playwright installation had issues"
    echo "You may need to run: playwright install chromium --force"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[5/5] Creating .env file from template..."
    cp .env.template .env
    echo ""
    echo "========================================"
    echo " IMPORTANT: Configure your settings!"
    echo "========================================"
    echo ""
    echo "Please edit .env file and add:"
    echo " - Your personal information"
    echo " - OpenAI API key"
    echo " - Job filtering keywords"
    echo ""
else
    echo "[5/5] .env file already exists"
fi

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo " 1. Edit .env file with your details"
echo " 2. Place your resume in data/resumes/base_resume.pdf"
echo " 3. Edit data/companies.csv with target companies"
echo " 4. Run: python main.py --test --limit 3"
echo ""
echo "For detailed instructions, see:"
echo " - INSTALLATION.md"
echo " - USAGE.md"
echo ""
