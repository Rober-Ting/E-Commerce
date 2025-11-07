# ⚡ Debug 模式 - 3 分鐘快速開始

## 🚀 立即開始（3 步驟）

### 步驟 1️⃣：停止目前的 API

如果 API 正在運行，按 `Ctrl+C` 停止

### 步驟 2️⃣：啟動 Debug 模式

```powershell
# 確保在 ecommerce-api 目錄
cd ecommerce-api

# 啟動虛擬環境（如果還沒啟動）
.\venv\Scripts\Activate.ps1

# 以 Debug 模式啟動 API
uvicorn app.main:app --reload --log-level debug
```

### 步驟 3️⃣：觀察詳細日誌

你會看到完整的啟動過程，包括：
- ✅ 配置載入
- ✅ FastAPI 實例建立
- ✅ CORS 設定
- ✅ MongoDB 連線（4個步驟）
- ✅ 資料庫驗證

---

## 🧪 測試 API（觀察日誌變化）

**另開一個 PowerShell 視窗**：

```powershell
# 測試根路由
Invoke-RestMethod -Uri "http://localhost:8000"

# 測試健康檢查
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

**回到 API 視窗**，你會看到：
```
收到根路由請求 GET /
返回根路由回應: 歡迎使用電商訂單管理系統 API

收到健康檢查請求 GET /health
正在驗證資料庫連線...
✓ 資料庫連線正常
返回健康檢查回應: {...}
```

---

## 🎯 你會看到什麼？

### 啟動時的詳細日誌

```
================================================================================
開始載入 FastAPI 應用模組
當前設定 - DEBUG: True
當前設定 - PROJECT_NAME: E-Commerce API
當前設定 - MONGODB_URL: mongodb://localhost:27017
當前設定 - MONGODB_DB_NAME: ecommerce_db
================================================================================
正在建立 FastAPI 應用實例...
✅ FastAPI 應用實例建立完成: E-Commerce API v1.0.0

正在設定 CORS 中介軟體...
允許的來源: ['*']
✅ CORS 中介軟體設定完成

[Uvicorn 啟動...]

================================================================================
🚀 應用程式啟動事件觸發
================================================================================
步驟 1/3: 準備連接 MongoDB...

正在連接 MongoDB: mongodb://localhost:27017
步驟 1/4: 建立 AsyncIOMotorClient 實例...
  ✓ 客戶端建立完成: <class 'motor.motor_asyncio.AsyncIOMotorClient'>

步驟 2/4: 選擇資料庫 'ecommerce_db'...
  ✓ 資料庫實例: ecommerce_db

步驟 3/4: 執行 ping 命令測試連線...
  ✓ Ping 回應: {'ok': 1.0}

步驟 4/4: 獲取伺服器資訊...
  ✓ MongoDB 版本: 7.0.5
  ✓ 伺服器位址: ('localhost', 27017)

✅ 成功連接到 MongoDB 資料庫: ecommerce_db

步驟 2/3: 驗證資料庫連線...
  ✓ 資料庫客戶端: AsyncIOMotorClient(...)
  ✓ 資料庫實例: ecommerce_db

步驟 3/3: 初始化完成
✅ 應用程式啟動完成
================================================================================
```

---

## 🔍 進階：使用 VSCode Debugger

### 快速步驟

1. 在 VSCode 中打開 `app/main.py`
2. 在第 67 行左側點擊，設置斷點 🔴
3. 按 `F5` 鍵啟動 Debug
4. 程式會在斷點處暫停
5. 按 `F10` 單步執行，觀察每一步

### Debug 控制鍵

- `F5` - 繼續執行
- `F10` - 單步跳過
- `F11` - 單步進入
- `Shift+F5` - 停止

---

## 📚 完整指南

- 📖 **完整學習**：`DEBUG_GUIDE.md`
- 🔄 **效果對比**：`DEBUG_COMPARISON.md`
- 🎓 **實戰練習**：`DEBUG_GUIDE.md` 中的三個練習

---

## 💡 實用命令

### 保存日誌到檔案
```powershell
uvicorn app.main:app --reload --log-level debug > debug.log 2>&1
```

### 只看特定級別
```powershell
# 只看 DEBUG
uvicorn app.main:app --reload --log-level debug | Select-String "DEBUG"

# 只看 ERROR
uvicorn app.main:app --reload --log-level debug | Select-String "ERROR"
```

### 關閉 Debug 模式
在 `.env` 中設定：
```env
DEBUG=false
LOG_LEVEL=INFO
```

---

## ✅ 快速檢查清單

完成以下步驟，確認 Debug 模式正常運作：

- [ ] API 以 debug 模式啟動成功
- [ ] 看到詳細的配置載入訊息
- [ ] 看到 MongoDB 連線的 4 個步驟
- [ ] 看到 MongoDB 版本和地址
- [ ] 測試 API 時看到請求處理日誌
- [ ] 理解每一步的執行順序

---

## 🎉 完成！

現在你可以：
- ✅ 看到 API 啟動的每一個步驟
- ✅ 追蹤 MongoDB 連線過程
- ✅ 觀察每個 API 請求的處理
- ✅ 理解程式的執行流程

**這就是真正的學習方式！** 🚀

---

**下一步**：閱讀 `DEBUG_GUIDE.md` 學習更多進階技巧！

