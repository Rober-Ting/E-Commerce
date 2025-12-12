# Phase 4 订单管理 Demo 启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Phase 4 订单管理 Demo 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查后端是否运行
Write-Host "检查后端服务器..." -ForegroundColor Yellow
$response = $null
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
} catch {
    # 忽略错误
}

if ($null -eq $response) {
    Write-Host ""
    Write-Host "❌ 后端服务器未运行！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先启动后端服务器:" -ForegroundColor Yellow
    Write-Host "  .\start_backend.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "或手动运行:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\activate" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host ""
    pause
    exit
}

Write-Host "✅ 后端服务器正在运行" -ForegroundColor Green
Write-Host ""

# 启动前端
Write-Host "启动前端 Demo..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 前端地址: http://localhost:8080/frontend_orders_demo.html" -ForegroundColor Cyan
Write-Host "📡 后端地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Phase 4 订单管理功能测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "功能列表:" -ForegroundColor Yellow
Write-Host "  ✅ 商品浏览和添加到购物车" -ForegroundColor White
Write-Host "  ✅ 购物车管理（增删改）" -ForegroundColor White
Write-Host "  ✅ 订单创建（填写收货地址、选择支付方式）" -ForegroundColor White
Write-Host "  ✅ 我的订单列表（筛选、查看详情）" -ForegroundColor White
Write-Host "  ✅ 取消订单（恢复库存）" -ForegroundColor White
Write-Host "  ✅ 管理员：查看所有订单" -ForegroundColor White
Write-Host "  ✅ 管理员：更新订单状态" -ForegroundColor White
Write-Host "  ✅ 管理员：订单统计数据" -ForegroundColor White
Write-Host ""
Write-Host "测试账户:" -ForegroundColor Yellow
Write-Host "  👤 Customer: customer@test.com / Customer123!" -ForegroundColor White
Write-Host "  🏪 Vendor:   vendor@test.com / Vendor123!" -ForegroundColor White
Write-Host "  🔐 Admin:    admin@ecommerce.com / Admin123!" -ForegroundColor White
Write-Host ""
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "  1. 先用 customer 账户登录，体验购物和下单流程" -ForegroundColor White
Write-Host "  2. 切换到 admin 账户，查看所有订单和统计数据" -ForegroundColor White
Write-Host "  3. 打开浏览器开发者工具 (F12) 查看 API 请求" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 启动 HTTP 服务器
python -m http.server 8080

