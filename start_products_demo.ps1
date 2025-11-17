# Phase 3 商品管理 Demo 启动脚本

Write-Host "`n🚀 启动 Phase 3 商品管理 Demo" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Green

# 检查 Python
Write-Host "🔍 检查 Python..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python 已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ 未找到 Python" -ForegroundColor Red
    exit 1
}

# 检查端口 8080 是否被占用
Write-Host "`n🔍 检查端口 8080..." -ForegroundColor Cyan
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($port8080) {
    Write-Host "   ⚠️  端口 8080 已被占用" -ForegroundColor Yellow
    Write-Host "   正在尝试关闭占用进程..." -ForegroundColor Yellow
    $processId = $port8080.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# 检查后端是否运行
Write-Host "`n🔍 检查后端服务器..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ 后端服务器正在运行" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  后端服务器未运行" -ForegroundColor Yellow
    Write-Host "   请先运行: .\start_backend.ps1" -ForegroundColor Yellow
    Write-Host "`n是否继续启动前端？[Y/N]" -ForegroundColor Cyan
    $continue = Read-Host
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 0
    }
}

Write-Host "`n📡 启动前端服务器..." -ForegroundColor Cyan
Write-Host "   端口: 8080" -ForegroundColor White
Write-Host "   目录: $PWD" -ForegroundColor White

Write-Host "`n🌐 访问地址：" -ForegroundColor Green
Write-Host "   商品管理 Demo: http://localhost:8080/frontend_products_demo.html" -ForegroundColor Yellow
Write-Host "   用户认证 Demo: http://localhost:8080/frontend_demo.html" -ForegroundColor Yellow

Write-Host "`n👤 测试账户：" -ForegroundColor Green
Write-Host "   管理员: admin@test.com / Admin123!" -ForegroundColor White
Write-Host "   普通用户: customer@test.com / Customer123!" -ForegroundColor White

Write-Host "`n💡 提示：" -ForegroundColor Cyan
Write-Host "   • 按 Ctrl+C 停止服务器" -ForegroundColor White
Write-Host "   • 查看使用指南: docs/01-getting-started/PHASE3_FRONTEND_DEMO_GUIDE.md" -ForegroundColor White

Write-Host "`n" -ForegroundColor White

# 启动 HTTP 服务器
python -m http.server 8080



