# Voice AI Assistant - Setup and Run Script for Windows
# This script sets up the environment and runs the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Voice AI Assistant Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Virtual environment found." -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install/upgrade dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed successfully." -ForegroundColor Green

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python init_backend.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to initialize database" -ForegroundColor Red
    exit 1
}
Write-Host "Database initialized." -ForegroundColor Green

# Seed data (optional)
Write-Host ""
$seedData = Read-Host "Do you want to seed demo data? (Y/N)"
if ($seedData -eq "Y" -or $seedData -eq "y") {
    Write-Host "Seeding demo data..." -ForegroundColor Yellow
    python scripts\seed_data.py
    Write-Host "Demo data seeded." -ForegroundColor Green
}

# Ask which components to run
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Select components to run:" -ForegroundColor Cyan
Write-Host "1. Backend only" -ForegroundColor White
Write-Host "2. UI only" -ForegroundColor White
Write-Host "3. Both Backend and UI" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
$choice = Read-Host "Enter choice (1-3)"

Write-Host ""
Write-Host "Starting application..." -ForegroundColor Yellow
Write-Host ""

switch ($choice) {
    "1" {
        Write-Host "Starting Flask backend on http://localhost:8000" -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        $env:FLASK_APP = "backend.app"
        $env:FLASK_ENV = "development"
        python -m flask run --host=0.0.0.0 --port=8000
    }
    "2" {
        Write-Host "Starting Streamlit UI..." -ForegroundColor Green
        Write-Host "Make sure backend is running on http://localhost:8000" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        streamlit run ui\supervisor_app.py
    }
    "3" {
        Write-Host "Starting both Backend and UI..." -ForegroundColor Green
        Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "UI will open in browser automatically" -ForegroundColor Cyan
        Write-Host ""
        
        # Start backend in background
        $env:FLASK_APP = "backend.app"
        $env:FLASK_ENV = "development"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m flask run --host=0.0.0.0 --port=8000"
        
        # Wait a moment for backend to start
        Start-Sleep -Seconds 3
        
        # Start UI
        streamlit run ui\supervisor_app.py
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}
