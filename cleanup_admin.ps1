# PowerShell script to cleanup old admin account and create new one
# Usage: .\cleanup_admin.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Cleanup Old Admin Account & Create New One" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please make sure venv exists" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 2: Delete old admin account
Write-Host "Step 2: Deleting old admin account (admin@ecommerce.local)..." -ForegroundColor Yellow
python scripts/cleanup_old_admin.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Cleanup script failed" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Step 3: Create new admin account
Write-Host "Step 3: Creating new admin account (admin@ecommerce.com)..." -ForegroundColor Yellow
python scripts/init_admin.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Failed to create new admin account" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "All Done! Admin account updated successfully!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "New Admin Account:" -ForegroundColor Cyan
Write-Host "  Email:    admin@ecommerce.com" -ForegroundColor White
Write-Host "  Password: Admin123!" -ForegroundColor White
Write-Host ""
Write-Host "You can now login with the new admin account!" -ForegroundColor Green
Write-Host ""


