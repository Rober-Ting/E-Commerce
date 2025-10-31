# 🔍 Debug 模式完整指南

## 🎯 你將學會

1. **增強日誌模式** - 看到每一步的詳細執行過程
2. **VSCode Debugger** - 單步調試，查看變數值
3. **斷點調試** - 在關鍵位置暫停程式

---

## 📊 方案 1：增強日誌模式（已完成！）

### ✨ 已添加的 Debug 功能

我已經為你增強了所有核心文件的日誌輸出：

#### 1. `config.py` 增強
- ✅ 新增 `LOG_LEVEL` 配置
- ✅ 支援動態調整日誌級別

#### 2. `main.py` 增強
- ✅ 詳細的模組載入日誌
- ✅ FastAPI 實例建立過程
- ✅ CORS 中介軟體配置過程
- ✅ 啟動事件的 3 步驟追蹤
- ✅ 每個 API 端點的請求/回應日誌
- ✅ 資料庫連線驗證

#### 3. `database.py` 增強
- ✅ MongoDB 連線的 4 步驟追蹤
- ✅ 伺服器資訊顯示
- ✅ 詳細的錯誤追蹤

### 🚀 立即測試

**停止目前運行的 API（如果有），然後重新啟動**：

```powershell
# 在 ecommerce-api 目錄
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

### 📋 你將看到的新日誌

#### 模組載入階段：
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
```

#### 啟動事件階段：
```
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

#### API 請求階段：
```
收到根路由請求 GET /
返回根路由回應: 歡迎使用電商訂單管理系統 API

收到健康檢查請求 GET /health
正在驗證資料庫連線...
✓ 資料庫連線正常
返回健康檢查回應: {'status': 'healthy', ...}
```

---

## 🐛 方案 2：VSCode Debugger（單步調試）

### 步驟 1：設置完成

我已經為你創建了 `.vscode/launch.json` 配置文件！

### 步驟 2：設置斷點

1. 打開 `app/main.py`
2. 在你想暫停的行號左側點擊，出現紅點 🔴
3. 建議的斷點位置：
   - 第 67 行：`await connect_to_mongo()` - 觀察連線過程
   - 第 110 行：`logger.debug("收到根路由請求 GET /")` - 觀察請求處理
   - 第 139 行：`await db.client.admin.command('ping')` - 觀察資料庫操作

### 步驟 3：啟動 Debug

**方法 1：使用快捷鍵**
- 按 `F5` 鍵

**方法 2：使用介面**
1. 點擊左側的「執行和偵錯」圖標（▶️ 🐛）
2. 選擇「Debug FastAPI」
3. 點擊綠色播放按鈕

### 步驟 4：使用 Debugger

當程式在斷點處暫停時：

#### 查看變數值
- 左側「變數」面板顯示所有當前變數
- 滑鼠懸停在代碼上查看值

#### 控制執行
- `F5` - 繼續執行
- `F10` - 單步跳過（執行當前行）
- `F11` - 單步進入（進入函數內部）
- `Shift+F11` - 單步跳出（離開當前函數）
- `Ctrl+Shift+F5` - 重新啟動
- `Shift+F5` - 停止

#### Debug Console
在下方「偵錯主控台」可以執行 Python 表達式：
```python
# 查看設定
settings.MONGODB_URL
settings.DEBUG

# 查看資料庫狀態
db.client
db.db.name

# 執行任意 Python 代碼
type(db.client)
```

---

## 🎓 實戰演練

### 練習 1：追蹤啟動流程 ⭐

**目標**：理解 FastAPI 應用如何啟動

1. 在 `app/main.py` 第 67 行設置斷點（`await connect_to_mongo()`）
2. 按 `F5` 啟動 Debug
3. 程式會在斷點處暫停
4. 按 `F11` 進入 `connect_to_mongo` 函數
5. 觀察 `database.py` 中的每一步執行
6. 在 Debug Console 中輸入：
   ```python
   settings.MONGODB_URL
   db.client
   ```

**學習點**：
- 理解異步函數的執行順序
- 觀察 Motor 客戶端的建立過程
- 了解 ping 命令如何測試連線

### 練習 2：追蹤 API 請求 ⭐⭐

**目標**：理解 HTTP 請求的處理流程

1. 在 `app/main.py` 第 110 行設置斷點（根路由函數內）
2. 啟動 Debug
3. 打開瀏覽器訪問 `http://localhost:8000`
4. 程式會在斷點處暫停
5. 觀察 `response` 變數的建立過程
6. 按 `F10` 單步執行，觀察每一行

**學習點**：
- 理解 FastAPI 路由裝飾器的作用
- 觀察請求資料的結構
- 了解回應是如何建立的

### 練習 3：模擬資料庫錯誤 ⭐⭐⭐

**目標**：理解錯誤處理機制

1. 停止 MongoDB 服務：
   ```powershell
   Stop-Service -Name MongoDB
   ```

2. 在 `app/database.py` 第 44 行設置斷點（ping 命令）
3. 啟動 Debug
4. 觀察異常的捕獲和處理
5. 在 Debug Console 查看錯誤詳情：
   ```python
   import sys
   sys.exc_info()
   ```

**學習點**：
- 理解 try-except 的執行流程
- 觀察異常物件的結構
- 了解錯誤日誌的記錄方式

---

## 🔧 進階 Debug 技巧

### 1. 條件斷點

右鍵點擊斷點 → 編輯斷點 → 設置條件

例如：只在資料庫斷線時暫停
```python
db_status == "disconnected"
```

### 2. 日誌點（Logpoint）

右鍵點擊行號 → 新增日誌點

不會暫停程式，只輸出訊息：
```
資料庫連線狀態: {db_status}
```

### 3. 監看表達式

在「監看」面板添加表達式，持續觀察值的變化：
```python
db.client.address
settings.DEBUG
len(response)
```

### 4. 呼叫堆疊

查看「呼叫堆疊」面板，了解函數的調用順序：
```
startup_event
  ↓
connect_to_mongo
  ↓
AsyncIOMotorClient.__init__
```

---

## 📊 日誌級別說明

在 `.env` 中可以調整日誌級別：

```env
# DEBUG - 所有詳細訊息（最詳細）
LOG_LEVEL=DEBUG

# INFO - 一般資訊（預設）
LOG_LEVEL=INFO

# WARNING - 警告訊息
LOG_LEVEL=WARNING

# ERROR - 只顯示錯誤
LOG_LEVEL=ERROR
```

### 各級別的輸出

| 級別 | 顯示內容 | 適用場景 |
|------|---------|---------|
| DEBUG | 所有步驟、變數值 | 開發和學習 |
| INFO | 主要事件 | 正常運行 |
| WARNING | 潛在問題 | 生產環境 |
| ERROR | 錯誤訊息 | 問題排查 |

---

## 🎯 Debug 最佳實踐

### 開發階段
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### 測試階段
```env
DEBUG=true
LOG_LEVEL=INFO
```

### 生產環境
```env
DEBUG=false
LOG_LEVEL=WARNING
```

---

## 📝 Debug Checklist

學習 Debug 時，逐步完成以下項目：

### 基礎技能
- [ ] 啟動增強日誌模式
- [ ] 閱讀並理解詳細日誌輸出
- [ ] 在 VSCode 中設置斷點
- [ ] 使用 F5 啟動 Debug
- [ ] 使用 F10 單步執行

### 進階技能
- [ ] 使用 F11 進入函數內部
- [ ] 在 Debug Console 執行表達式
- [ ] 查看呼叫堆疊
- [ ] 設置條件斷點
- [ ] 使用監看表達式

### 實戰應用
- [ ] 完成練習 1：追蹤啟動流程
- [ ] 完成練習 2：追蹤 API 請求
- [ ] 完成練習 3：模擬資料庫錯誤
- [ ] 能夠獨立 debug 新功能
- [ ] 能夠排查實際問題

---

## 💡 Debug 小技巧

### 1. 快速重啟
修改代碼後，使用 `Ctrl+Shift+F5` 快速重啟 Debug

### 2. 跳過框架代碼
在 `launch.json` 中設置 `"justMyCode": true`，只 debug 你的代碼

### 3. 保存日誌
```powershell
uvicorn app.main:app --reload --log-level debug > debug.log 2>&1
```

### 4. 彩色日誌（進階）
安裝 `colorlog` 套件可以讓日誌更易讀：
```powershell
pip install colorlog
```

---

## 🐛 常見 Debug 問題

### 問題 1：斷點不生效

**原因**：代碼已被執行

**解決**：在啟動時就會執行的代碼（如模組載入），需要在啟動前設置斷點

### 問題 2：看不到變數值

**原因**：變數不在當前作用域

**解決**：使用呼叫堆疊切換到對應的函數框架

### 問題 3：Debug 啟動失敗

**檢查**：
1. 虛擬環境是否啟動
2. 工作目錄是否正確
3. Python 直譯器路徑是否正確

---

## 🚀 現在開始 Debug！

### 快速開始（推薦）

1. **停止目前的 API**（如果正在運行）
2. **重新啟動**，看增強的日誌：
   ```powershell
   uvicorn app.main:app --reload --log-level debug
   ```

3. **測試 API**，觀察詳細日誌：
   ```powershell
   # 另開視窗
   Invoke-RestMethod -Uri "http://localhost:8000/health"
   ```

### 進階模式

1. 在 VSCode 中打開 `app/main.py`
2. 在第 67 行設置斷點
3. 按 `F5` 啟動 Debug
4. 觀察啟動過程的每一步

---

## 📚 延伸學習

1. [VSCode Python Debugging](https://code.visualstudio.com/docs/python/debugging)
2. [Python logging 模組](https://docs.python.org/3/library/logging.html)
3. [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
4. [Motor 異步操作](https://motor.readthedocs.io/)

---

**Happy Debugging! 🐛🔍**

記住：**Debug 不是找錯誤，而是理解程式如何運作！**

