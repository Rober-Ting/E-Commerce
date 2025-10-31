# 🚀 快速啟動指南

這是 Day 2-3 的快速啟動指南。完整學習內容請參考 [DAY2-3_LEARNING_GUIDE.md](DAY2-3_LEARNING_GUIDE.md)

---

## ⚡ 5 分鐘快速開始

### 步驟 1: 自動化設置（推薦）

```powershell
# 在 ecommerce-api 目錄下執行
.\scripts\setup_env.ps1
```

這個腳本會自動幫你：
- ✅ 生成安全的 SECRET_KEY
- ✅ 建立 .env 檔案
- ✅ 檢查 MongoDB 服務
- ✅ 測試資料庫連線

### 步驟 2: 啟動虛擬環境

```powershell
.\venv\Scripts\Activate.ps1
```

看到 `(venv)` 前綴就表示成功了！

### 步驟 3: 啟動 API 服務

```powershell
uvicorn app.main:app --reload
```

看到以下訊息表示成功：
```
✅ 成功連接到 MongoDB 資料庫: ecommerce_db
✅ 應用程式啟動完成
```

### 步驟 4: 測試 API

打開瀏覽器訪問：
- 📖 **Swagger UI**: http://localhost:8000/docs
- 🏥 **健康檢查**: http://localhost:8000/health
- 🏠 **根路由**: http://localhost:8000

或執行測試腳本：
```powershell
python tests\test_basic.py
```

---

## 🛠️ 手動設置（學習模式）

如果你想理解每一步，可以手動設置：

### 1. 建立 .env 檔案

```powershell
# 複製範例檔案
Copy-Item .env.example .env

# 編輯 .env 檔案
notepad .env
```

### 2. 生成 SECRET_KEY

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

將生成的密鑰複製到 .env 的 `SECRET_KEY=` 後面

### 3. 設定 MongoDB 連線

在 .env 中設定：
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ecommerce_db
```

### 4. 檢查 MongoDB

```powershell
# 檢查服務狀態
Get-Service -Name MongoDB

# 如果未運行，啟動它
Start-Service -Name MongoDB
```

### 5. 啟動應用

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

---

## 🧪 執行測試

### 方法 1: Python 測試腳本

```powershell
python tests\test_basic.py
```

### 方法 2: PowerShell 手動測試

```powershell
# 測試根路由
Invoke-RestMethod -Uri "http://localhost:8000" -Method Get

# 測試健康檢查
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### 方法 3: 瀏覽器測試

直接在瀏覽器訪問 http://localhost:8000/docs 並嘗試各個端點

---

## 🐛 常見問題

### 問題 1: MongoDB 連線失敗

**症狀**：
```
❌ MongoDB 連線失敗: [Errno 111] Connection refused
```

**解決方案**：
```powershell
# 檢查 MongoDB 是否運行
Get-Service -Name MongoDB

# 啟動 MongoDB
Start-Service -Name MongoDB

# 或手動啟動（如果不是服務安裝）
mongod --dbpath "C:\data\db"
```

### 問題 2: 埠號被佔用

**症狀**：
```
ERROR: [Errno 10048] Only one usage of each socket address
```

**解決方案**：
```powershell
# 使用不同埠號
uvicorn app.main:app --reload --port 8001
```

### 問題 3: 找不到模組

**症狀**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解決方案**：
```powershell
# 確認虛擬環境已啟動
.\venv\Scripts\Activate.ps1

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題 4: pydantic_settings 找不到

**症狀**：
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**解決方案**：
```powershell
pip install pydantic-settings
```

---

## 📚 學習資源

### 必讀文檔
1. [DAY2-3_LEARNING_GUIDE.md](DAY2-3_LEARNING_GUIDE.md) - 詳細學習指南
2. [PHASE1_PROGRESS.md](PHASE1_PROGRESS.md) - 開發進度追蹤

### 程式碼結構
```
app/
├── config.py       # 配置管理（環境變數）
├── database.py     # MongoDB 連線管理
└── main.py         # FastAPI 應用入口
```

### 關鍵概念
- **Pydantic Settings**: 型別安全的配置管理
- **Motor**: 異步 MongoDB 驅動
- **FastAPI Events**: 應用生命週期管理
- **Dependency Injection**: 依賴注入模式

---

## ✅ 驗收清單

完成以下所有項目，表示 Day 2-3 完成：

- [ ] .env 檔案建立並配置正確
- [ ] MongoDB 連線成功
- [ ] FastAPI 應用啟動成功
- [ ] http://localhost:8000 可以訪問
- [ ] http://localhost:8000/health 返回 healthy
- [ ] http://localhost:8000/docs 顯示 Swagger UI
- [ ] 測試腳本全部通過
- [ ] 理解配置管理的概念
- [ ] 理解異步資料庫連線
- [ ] 理解應用生命週期

---

## 🎯 下一步

Day 2-3 完成後，你可以：

1. **嘗試動手練習**（DAY2-3_LEARNING_GUIDE.md 中的練習）
2. **進入 Day 3-4**：深入 FastAPI 路由設計
3. **開始 Week 2**：實作用戶認證系統

---

**需要幫助？** 查看詳細學習指南或開發進度文檔！

Happy Coding! 🎉

