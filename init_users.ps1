# User Initialization Script
# Creates default admin account and optional test users

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Initializing User Accounts" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check for virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    
    # Run Python script in virtual environment
    & "venv\Scripts\python.exe" scripts/init_admin.py
} else {
    Write-Host "Warning: Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Using system Python..." -ForegroundColor Yellow
    python scripts/init_admin.py
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Gray
Write-Host " Initialization Complete" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Tip: To re-initialize, manually delete users from database first" -ForegroundColor Yellow
Write-Host ""
