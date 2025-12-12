# Service Status Check Script

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Service Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check MongoDB
Write-Host "1. Checking MongoDB..." -ForegroundColor Yellow
$mongoService = Get-Service -Name "*MongoDB*" -ErrorAction SilentlyContinue
if ($mongoService) {
    if ($mongoService.Status -eq "Running") {
        Write-Host "   Status: RUNNING" -ForegroundColor Green
    } else {
        Write-Host "   Status: STOPPED" -ForegroundColor Red
        Write-Host "   Action: Run 'net start MongoDB'" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Status: NOT FOUND" -ForegroundColor Red
    Write-Host "   Note: MongoDB may be running as standalone process" -ForegroundColor Yellow
}
Write-Host ""

# 2. Check Backend (Python/uvicorn)
Write-Host "2. Checking Backend Server..." -ForegroundColor Yellow
$pythonProcess = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcess) {
    Write-Host "   Status: RUNNING (Python processes found)" -ForegroundColor Green
} else {
    Write-Host "   Status: NOT RUNNING" -ForegroundColor Red
    Write-Host "   Action: Run '.\start_backend.ps1'" -ForegroundColor Yellow
}
Write-Host ""

# 3. Test Backend Connection
Write-Host "3. Testing Backend Connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   Status: CONNECTED" -ForegroundColor Green
    Write-Host "   URL: http://127.0.0.1:8000" -ForegroundColor Cyan
} catch {
    Write-Host "   Status: CONNECTION FAILED" -ForegroundColor Red
    Write-Host "   Error: Cannot connect to http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host "   Action: Ensure backend is running" -ForegroundColor Yellow
}
Write-Host ""

# 4. Check Port 8000
Write-Host "4. Checking Port 8000..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "   Status: IN USE (Process ID: $($port8000.OwningProcess))" -ForegroundColor Green
} else {
    Write-Host "   Status: NOT IN USE" -ForegroundColor Red
    Write-Host "   Note: Backend server is not listening on port 8000" -ForegroundColor Yellow
}
Write-Host ""

# 5. Check Port 8080
Write-Host "5. Checking Port 8080..." -ForegroundColor Yellow
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($port8080) {
    Write-Host "   Status: IN USE (Process ID: $($port8080.OwningProcess))" -ForegroundColor Green
} else {
    Write-Host "   Status: NOT IN USE" -ForegroundColor Yellow
    Write-Host "   Action: Run '.\start_orders_demo.ps1' to start frontend" -ForegroundColor Yellow
}
Write-Host ""

# 6. Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

if (-not $mongoService -or $mongoService.Status -ne "Running") {
    Write-Host "Action Required: Start MongoDB" -ForegroundColor Red
    $allGood = $false
}

if (-not $pythonProcess) {
    Write-Host "Action Required: Start Backend (.\start_backend.ps1)" -ForegroundColor Red
    $allGood = $false
}

if (-not $port8000) {
    Write-Host "Action Required: Backend not listening on port 8000" -ForegroundColor Red
    $allGood = $false
}

if ($allGood) {
    Write-Host "All services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Frontend: http://localhost:8080/frontend_orders_demo.html" -ForegroundColor Cyan
    Write-Host "Backend API: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
}

Write-Host ""

