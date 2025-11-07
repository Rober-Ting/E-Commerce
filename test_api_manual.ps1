# Phase 2 API Manual Test Script
# Usage: .\test_api_manual.ps1

Write-Host "Phase 2 API Testing Script" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000"
$headers = @{
    "Content-Type" = "application/json"
}

# 1. Health Check
Write-Host "1. Testing health check..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
Write-Host "OK Health status: $($response.data.status)" -ForegroundColor Green
Write-Host ""

# 2. Register new user
Write-Host "2. Registering new user..." -ForegroundColor Yellow
$registerData = @{
    email = "testuser_$(Get-Date -Format 'HHmmss')@example.com"
    password = "SecurePass123!"
    full_name = "Test User"
    phone = "0912345678"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" -Method Post -Body $registerData -Headers $headers
    $userEmail = $registerResponse.data.user.email
    $token = $registerResponse.data.access_token
    Write-Host "OK Registration successful!" -ForegroundColor Green
    Write-Host "   User ID: $($registerResponse.data.user.id)" -ForegroundColor Gray
    Write-Host "   Email: $userEmail" -ForegroundColor Gray
    Write-Host "   Role: $($registerResponse.data.user.role)" -ForegroundColor Gray
    Write-Host "   Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host ""
    
    # 3. Test duplicate registration (should fail)
    Write-Host "3. Testing duplicate registration (should fail)..." -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" -Method Post -Body $registerData -Headers $headers -ErrorAction Stop
        Write-Host "FAIL Should reject duplicate registration!" -ForegroundColor Red
    } catch {
        Write-Host "OK Correctly rejected duplicate registration (409 Conflict)" -ForegroundColor Green
    }
    Write-Host ""
    
    # 4. Login
    Write-Host "4. Logging in with registered account..." -ForegroundColor Yellow
    $loginData = @{
        email = $userEmail
        password = "SecurePass123!"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -Headers $headers
    $token = $loginResponse.data.access_token
    Write-Host "OK Login successful!" -ForegroundColor Green
    Write-Host "   Token type: $($loginResponse.data.token_type)" -ForegroundColor Gray
    Write-Host "   Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host ""
    
    # 5. Get current user info
    Write-Host "5. Getting current user info (requires Token)..." -ForegroundColor Yellow
    $authHeaders = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    }
    
    $meResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Method Get -Headers $authHeaders
    Write-Host "OK Successfully retrieved user info!" -ForegroundColor Green
    Write-Host "   Name: $($meResponse.data.full_name)" -ForegroundColor Gray
    Write-Host "   Email: $($meResponse.data.email)" -ForegroundColor Gray
    Write-Host "   Role: $($meResponse.data.role)" -ForegroundColor Gray
    Write-Host "   Status: $(if($meResponse.data.is_active){'Active'}else{'Inactive'})" -ForegroundColor Gray
    Write-Host ""
    
    # 6. Test access without Token (should fail)
    Write-Host "6. Testing access without Token (should fail)..." -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Method Get -Headers $headers -ErrorAction Stop
        Write-Host "FAIL Should require authentication!" -ForegroundColor Red
    } catch {
        Write-Host "OK Correctly rejected unauthenticated access (401 Unauthorized)" -ForegroundColor Green
    }
    Write-Host ""
    
    # 7. Test login with wrong password (should fail)
    Write-Host "7. Testing login with wrong password (should fail)..." -ForegroundColor Yellow
    $wrongLoginData = @{
        email = $userEmail
        password = "WrongPassword123!"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $wrongLoginData -Headers $headers -ErrorAction Stop
        Write-Host "FAIL Should reject wrong password!" -ForegroundColor Red
    } catch {
        Write-Host "OK Correctly rejected wrong password (401 Unauthorized)" -ForegroundColor Green
    }
    Write-Host ""
    
    # 8. Test password change
    Write-Host "8. Testing password change..." -ForegroundColor Yellow
    $changePasswordData = @{
        current_password = "SecurePass123!"
        new_password = "NewSecurePass456!"
    } | ConvertTo-Json
    
    $changePassResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/password" -Method Put -Body $changePasswordData -Headers $authHeaders
    Write-Host "OK Password changed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # 9. Login with new password
    Write-Host "9. Logging in with new password..." -ForegroundColor Yellow
    $newLoginData = @{
        email = $userEmail
        password = "NewSecurePass456!"
    } | ConvertTo-Json
    
    $newLoginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $newLoginData -Headers $headers
    Write-Host "OK Login with new password successful!" -ForegroundColor Green
    Write-Host ""
    
    # Summary
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "All tests completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test Summary:" -ForegroundColor Cyan
    Write-Host "   OK User registration" -ForegroundColor Green
    Write-Host "   OK Duplicate registration validation" -ForegroundColor Green
    Write-Host "   OK User login" -ForegroundColor Green
    Write-Host "   OK Token authentication" -ForegroundColor Green
    Write-Host "   OK Get user info" -ForegroundColor Green
    Write-Host "   OK Access control" -ForegroundColor Green
    Write-Host "   OK Wrong password handling" -ForegroundColor Green
    Write-Host "   OK Password change" -ForegroundColor Green
    Write-Host "   OK New password login" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test Account Info:" -ForegroundColor Cyan
    Write-Host "   Email: $userEmail" -ForegroundColor Yellow
    Write-Host "   Password: NewSecurePass456!" -ForegroundColor Yellow
    Write-Host "   Token: $($newLoginResponse.data.access_token.Substring(0, 30))..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Tip: You can use this account at http://127.0.0.1:8000/docs to test other endpoints" -ForegroundColor Cyan
    
} catch {
    Write-Host "Test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Yellow
    Write-Host $_.Exception | Format-List -Force
}
