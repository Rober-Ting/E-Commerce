# ========================================
# 環境設置腳本
# ========================================
# 此腳本幫助你快速設置開發環境
# 包括：建立 .env 檔案、生成 SECRET_KEY、檢查 MongoDB

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  電商 API 環境設置腳本" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# 切換到專案根目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "📁 專案目錄: $projectRoot`n" -ForegroundColor Blue

# ========================================
# 步驟 1: 檢查 .env 檔案
# ========================================
Write-Host "步驟 1: 檢查 .env 檔案" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

if (Test-Path ".env") {
    Write-Host "⚠️  .env 檔案已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "是否要覆蓋現有的 .env 檔案？(y/N)"
    
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "✅ 保留現有 .env 檔案" -ForegroundColor Green
        $createEnv = $false
    } else {
        Write-Host "⚠️  將覆蓋現有 .env 檔案" -ForegroundColor Yellow
        $createEnv = $true
    }
} else {
    Write-Host "📝 .env 檔案不存在，將建立新檔案" -ForegroundColor Blue
    $createEnv = $true
}

# ========================================
# 步驟 2: 生成 SECRET_KEY
# ========================================
Write-Host "`n步驟 2: 生成 SECRET_KEY" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    $secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
    Write-Host "✅ 成功生成 SECRET_KEY" -ForegroundColor Green
    Write-Host "   $secretKey" -ForegroundColor Gray
} catch {
    Write-Host "❌ 生成 SECRET_KEY 失敗" -ForegroundColor Red
    Write-Host "   請確認 Python 已正確安裝" -ForegroundColor Yellow
    $secretKey = "PLEASE-CHANGE-THIS-SECRET-KEY-" + (Get-Random -Maximum 99999)
    Write-Host "   使用臨時密鑰: $secretKey" -ForegroundColor Yellow
}

# ========================================
# 步驟 3: MongoDB 配置
# ========================================
Write-Host "`n步驟 3: MongoDB 配置" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "請輸入 MongoDB 連線資訊（直接按 Enter 使用預設值）:`n" -ForegroundColor Blue

$mongoUrl = Read-Host "MongoDB URL [mongodb://localhost:27017]"
if ([string]::IsNullOrWhiteSpace($mongoUrl)) {
    $mongoUrl = "mongodb://localhost:27017"
}

$dbName = Read-Host "資料庫名稱 [ecommerce_db]"
if ([string]::IsNullOrWhiteSpace($dbName)) {
    $dbName = "ecommerce_db"
}

Write-Host "`n✅ MongoDB 配置:" -ForegroundColor Green
Write-Host "   URL: $mongoUrl" -ForegroundColor Gray
Write-Host "   資料庫: $dbName" -ForegroundColor Gray

# ========================================
# 步驟 4: 建立 .env 檔案
# ========================================
if ($createEnv) {
    Write-Host "`n步驟 4: 建立 .env 檔案" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    $envContent = @"
# ========================================
# MongoDB 資料庫配置
# ========================================
MONGODB_URL=$mongoUrl
MONGODB_DB_NAME=$dbName

# ========================================
# JWT 認證配置
# ========================================
SECRET_KEY=$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ========================================
# API 基礎配置
# ========================================
API_V1_PREFIX=/api/v1
PROJECT_NAME=E-Commerce API
DEBUG=true

# ========================================
# CORS 跨域資源共享配置
# ========================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

# ========================================
# 應用程式配置
# ========================================
PORT=8000
HOST=0.0.0.0
"@

    try {
        $envContent | Out-File -FilePath ".env" -Encoding utf8 -Force
        Write-Host "✅ .env 檔案建立成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ 建立 .env 檔案失敗: $_" -ForegroundColor Red
    }
}

# ========================================
# 步驟 5: 檢查 MongoDB 服務
# ========================================
Write-Host "`n步驟 5: 檢查 MongoDB 服務" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    $mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    
    if ($mongoService) {
        if ($mongoService.Status -eq "Running") {
            Write-Host "✅ MongoDB 服務正在運行" -ForegroundColor Green
        } else {
            Write-Host "⚠️  MongoDB 服務已安裝但未運行" -ForegroundColor Yellow
            $startService = Read-Host "是否要啟動 MongoDB 服務？(y/N)"
            
            if ($startService -eq "y" -or $startService -eq "Y") {
                Start-Service -Name "MongoDB"
                Write-Host "✅ MongoDB 服務已啟動" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "⚠️  找不到 MongoDB 服務" -ForegroundColor Yellow
        Write-Host "   可能的情況：" -ForegroundColor Blue
        Write-Host "   1. MongoDB 未安裝為 Windows 服務" -ForegroundColor Gray
        Write-Host "   2. 需要手動啟動 mongod" -ForegroundColor Gray
        Write-Host "   3. 使用 MongoDB Atlas 雲端服務" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  無法檢查 MongoDB 服務狀態" -ForegroundColor Yellow
}

# ========================================
# 步驟 6: 測試 MongoDB 連線
# ========================================
Write-Host "`n步驟 6: 測試 MongoDB 連線" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$testMongo = Read-Host "是否要測試 MongoDB 連線？(Y/n)"

if ($testMongo -ne "n" -and $testMongo -ne "N") {
    Write-Host "正在測試連線..." -ForegroundColor Blue
    
    $testScript = @"
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    try:
        client = AsyncIOMotorClient('$mongoUrl', serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print('SUCCESS')
        client.close()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

asyncio.run(test_connection())
"@

    try {
        $result = $testScript | python 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -match 'SUCCESS') {
            Write-Host "✅ MongoDB 連線測試成功！" -ForegroundColor Green
        } else {
            Write-Host "❌ MongoDB 連線測試失敗" -ForegroundColor Red
            Write-Host "   錯誤訊息: $result" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ 無法執行連線測試" -ForegroundColor Red
        Write-Host "   $_" -ForegroundColor Yellow
    }
}

# ========================================
# 完成
# ========================================
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  設置完成！" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n📋 下一步操作：`n" -ForegroundColor Blue

Write-Host "1. 啟動 API 服務器：" -ForegroundColor Yellow
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload`n" -ForegroundColor Gray

Write-Host "2. 訪問 API 文檔：" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs`n" -ForegroundColor Gray

Write-Host "3. 執行測試：" -ForegroundColor Yellow
Write-Host "   python tests\test_basic.py`n" -ForegroundColor Gray

Write-Host "4. 查看學習指南：" -ForegroundColor Yellow
Write-Host "   DAY2-3_LEARNING_GUIDE.md`n" -ForegroundColor Gray

Write-Host "🎉 祝你學習愉快！" -ForegroundColor Green
Write-Host ""

