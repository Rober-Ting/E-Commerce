# 测试运行脚本
# 方便快速运行测试

Write-Host "=" -ForegroundColor Cyan
Write-Host "🧪 Pytest 测试运行器" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path ".\venv\Scripts\activate.ps1")) {
    Write-Host "❌ 错误: 找不到虚拟环境" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "1️⃣  激活虚拟环境..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "2️⃣  检查 pytest 是否安装..." -ForegroundColor Green
$pytestVersion = & python -m pytest --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pytest 未安装，正在安装..." -ForegroundColor Yellow
    pip install pytest pytest-asyncio httpx
} else {
    Write-Host "✅ $pytestVersion" -ForegroundColor Green
}

Write-Host ""
Write-Host "3️⃣  运行测试..." -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# 运行测试
python -m pytest tests/test_day4_5.py -v --tb=short

Write-Host ""
Write-Host "=" -ForegroundColor Cyan
Write-Host "✅ 测试完成！" -ForegroundColor Green
Write-Host ""

# 显示帮助信息
Write-Host "💡 其他有用的命令:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_day4_5.py -v              # 详细模式"
Write-Host "  pytest tests/test_day4_5.py -v -s           # 显示 print 输出"
Write-Host "  pytest tests/test_day4_5.py::TestHelpers    # 只运行 TestHelpers"
Write-Host "  pytest tests/test_day4_5.py -k objectid     # 运行包含 'objectid' 的测试"
Write-Host ""


