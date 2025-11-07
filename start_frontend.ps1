# Start Frontend HTTP Server
# This allows frontend to use http:// instead of file://

Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Write-Host ""

# Use Python built-in HTTP server
Write-Host "Frontend URL: http://localhost:8080" -ForegroundColor Green
Write-Host "Backend URL: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Open in browser: http://localhost:8080/frontend_demo.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Gray
Write-Host ""

# Start HTTP server on port 8080
python -m http.server 8080
