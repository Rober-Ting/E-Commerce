# 🔄 Debug 模式對比

## 📊 修改前 vs 修改後

### ❌ 修改前（普通模式）

你只能看到簡單的結果：

```
INFO:     Started server process [21536]
INFO:     Waiting for application startup.
2025-10-31 09:24:37,501 - app.main - INFO - 🚀 應用程式啟動中...
2025-10-31 09:24:37,502 - app.database - INFO - 正在連接 MongoDB: mongodb://localhost:27017
2025-10-31 09:24:37,999 - app.database - INFO - ✅ 成功連接到 MongoDB 資料庫: ecommerce_db
2025-10-31 09:24:38,006 - app.main - INFO - ✅ 應用程式啟動完成
INFO:     Application startup complete.
```

**問題**：
- 😕 不知道內部發生了什麼
- 😕 看不到每一步的過程
- 😕 無法追蹤變數的值
- 😕 難以學習和理解

---

### ✅ 修改後（Debug 模式）

你可以看到**完整的執行過程**：

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

INFO:     Started server process [12345]
INFO:     Waiting for application startup.

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
  ✓ 資料庫客戶端: AsyncIOMotorClient(MongoClient(host=['localhost:27017'], ...)
  ✓ 資料庫實例: ecommerce_db

步驟 3/3: 初始化完成
✅ 應用程式啟動完成
================================================================================

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**優勢**：
- ✅ 看到每個步驟的執行順序
- ✅ 了解配置如何載入
- ✅ 追蹤資料庫連線的詳細過程
- ✅ 知道 MongoDB 版本和地址
- ✅ 清楚的視覺分隔和結構

---

## 🔍 API 請求對比

### ❌ 修改前

訪問 `http://localhost:8000/health`：

```
INFO:     127.0.0.1:56561 - "GET /health HTTP/1.1" 200 OK
```

**看到什麼**：只知道請求成功了

---

### ✅ 修改後

訪問 `http://localhost:8000/health`：

```
收到健康檢查請求 GET /health
正在驗證資料庫連線...
✓ 資料庫連線正常
返回健康檢查回應: {'status': 'healthy', 'service': 'E-Commerce API', 'database': 'connected'}
INFO:     127.0.0.1:56561 - "GET /health HTTP/1.1" 200 OK
```

**看到什麼**：
- ✅ 收到了什麼請求
- ✅ 執行了哪些檢查
- ✅ 資料庫狀態如何
- ✅ 回應的內容是什麼

---

## 🎓 學習效果對比

### 普通模式
```
你: "API 啟動了，但我不知道它做了什麼..."
```

### Debug 模式
```
你: "我看到了！
    1. 先載入配置
    2. 建立 FastAPI 實例
    3. 設定 CORS
    4. 連接 MongoDB（4個步驟）
    5. 驗證連線
    6. 完成啟動！"
```

---

## 🚀 立即體驗

### 步驟 1：停止目前的 API

如果 API 正在運行，按 `Ctrl+C` 停止

### 步驟 2：重新啟動（Debug 模式）

```powershell
# 在 ecommerce-api 目錄
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

### 步驟 3：觀察啟動日誌

你會看到詳細的步驟說明！

### 步驟 4：測試 API 請求

**另開一個 PowerShell 視窗**：

```powershell
# 測試根路由
Invoke-RestMethod -Uri "http://localhost:8000"

# 測試健康檢查
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

**回到 API 視窗**，觀察詳細的請求處理日誌！

---

## 🎯 實際範例

### 範例 1：成功啟動

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

[啟動 uvicorn...]

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

### 範例 2：MongoDB 連線失敗

假設 MongoDB 沒有運行：

```
================================================================================
開始載入 FastAPI 應用模組
[配置載入...]
================================================================================

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
❌ MongoDB 連線失敗: [Errno 111] Connection refused
錯誤類型: ServerSelectionTimeoutError
錯誤詳情: [詳細堆疊追蹤]
```

**你可以清楚看到**：
- 在哪一步失敗了（步驟 3/4）
- 失敗的原因（Connection refused）
- 錯誤的類型（ServerSelectionTimeoutError）

---

### 範例 3：API 請求處理

訪問 `http://localhost:8000/`：

```
收到根路由請求 GET /
返回根路由回應: 歡迎使用電商訂單管理系統 API
INFO:     127.0.0.1:12345 - "GET / HTTP/1.1" 200 OK
```

訪問 `http://localhost:8000/health`：

```
收到健康檢查請求 GET /health
正在驗證資料庫連線...
✓ 資料庫連線正常
返回健康檢查回應: {'status': 'healthy', 'service': 'E-Commerce API', 'database': 'connected'}
INFO:     127.0.0.1:12345 - "GET /health HTTP/1.1" 200 OK
```

---

## 📊 日誌信息對比表

| 信息類型 | 普通模式 | Debug 模式 |
|---------|---------|-----------|
| 配置載入 | ❌ 看不到 | ✅ 顯示所有配置值 |
| FastAPI 初始化 | ❌ 看不到 | ✅ 顯示實例建立過程 |
| CORS 設定 | ❌ 看不到 | ✅ 顯示允許的來源 |
| MongoDB 連線步驟 | ❌ 只看結果 | ✅ 4個步驟詳細追蹤 |
| 資料庫資訊 | ❌ 看不到 | ✅ 版本、地址等 |
| API 請求處理 | ❌ 只看 HTTP 狀態 | ✅ 完整的處理流程 |
| 資料庫驗證 | ❌ 假設連線正常 | ✅ 每次請求都驗證 |
| 回應內容 | ❌ 看不到 | ✅ 顯示回應物件 |

---

## 🎓 學習建議

### 第一次使用（今天）
1. ✅ 重新啟動 API，觀察詳細日誌
2. ✅ 測試幾個 API 端點
3. ✅ 理解啟動流程的每一步

### 深入學習（明天）
1. 📖 閱讀 `DEBUG_GUIDE.md`
2. 🐛 使用 VSCode Debugger
3. 🔍 設置斷點，單步執行

### 進階實踐（後天）
1. 🧪 完成 Debug 練習
2. 🔧 嘗試修改代碼
3. 📝 自己添加 Debug 日誌

---

## 💡 小技巧

### 保存日誌到檔案

```powershell
uvicorn app.main:app --reload --log-level debug > debug.log 2>&1
```

然後可以慢慢分析：
```powershell
notepad debug.log
```

### 只看 DEBUG 訊息

```powershell
uvicorn app.main:app --reload --log-level debug | Select-String "DEBUG"
```

### 關閉 Debug 模式

在 `.env` 中：
```env
DEBUG=false
LOG_LEVEL=INFO
```

---

## 🎯 現在就試試！

**立即執行**：

```powershell
# 1. 停止目前的 API（如果正在運行）
# 按 Ctrl+C

# 2. 重新啟動 Debug 模式
uvicorn app.main:app --reload --log-level debug

# 3. 觀察詳細的啟動日誌！
```

**然後測試**：

```powershell
# 另開視窗
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

**回到 API 視窗**，看看詳細的處理過程！

---

**享受 Debug 帶來的學習樂趣！** 🎉🔍

現在你不只是運行 API，而是**真正理解它如何工作**！

