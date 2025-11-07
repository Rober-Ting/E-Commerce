# Start Backend FastAPI Server

Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (Test-Path ".\venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    .\venv\Scripts\activate
} else {
    Write-Host "Virtual environment not found, using global Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "API URL: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Gray
Write-Host ""

# Start FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
