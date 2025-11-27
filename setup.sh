#!/bin/bash

echo "================================================"
echo "DocuQuery Application - Quick Setup"
echo "================================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi
echo "[OK] Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js 16+"
    exit 1
fi
echo "[OK] Node.js found: $(node --version)"

# Check Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "[WARNING] Tesseract OCR not found"
    echo "Please install Tesseract:"
    echo "  macOS: brew install tesseract"
    echo "  Linux: sudo apt-get install tesseract-ocr"
else
    echo "[OK] Tesseract found: $(tesseract --version | head -n 1)"
fi

echo
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
echo "Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Copy .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "[NOTE] Please edit backend/.env with your settings"
fi

cd ..

echo
echo "Setting up frontend..."
cd frontend

# Install npm packages
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
fi

cd ..

echo
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo
echo "Next steps:"
echo "1. Update backend/.env with your settings"
echo "2. Run ./start.sh to start the application"
echo

chmod +x start.sh
