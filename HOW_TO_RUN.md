# 🏃 如何運行這個專案

## 🎓 學習模式 vs 快速模式

### 選項 A: 學習模式（推薦新手）

如果你想**深入理解每個步驟**，請跟著這個流程：

#### 1️⃣ 閱讀學習指南
```powershell
# 使用你喜歡的編輯器打開
notepad DAY2-3_LEARNING_GUIDE.md
# 或
code DAY2-3_LEARNING_GUIDE.md
```

這份指南會教你：
- 為什麼需要配置管理？
- 什麼是異步程式設計？
- 依賴注入是什麼？
- 如何測試 API？

#### 2️⃣ 理解關鍵代碼

打開並閱讀這三個核心文件，理解每一行的作用：

```powershell
# 配置管理
code app\config.py

# 資料庫連線
code app\database.py

# FastAPI 應用
code app\main.py
```

💡 **學習建議**：每個文件都有詳細的註釋（docstring），認真閱讀它們！

#### 3️⃣ 手動設置環境

```powershell
# 1. 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. 建立 .env 檔案
Copy-Item .env.example .env

# 3. 編輯 .env，貼上你的 SECRET_KEY
notepad .env

# 4. 檢查 MongoDB
Get-Service -Name MongoDB

# 如果沒運行
Start-Service -Name MongoDB
```

#### 4️⃣ 啟動並測試

```powershell
# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 啟動 API
uvicorn app.main:app --reload
```

打開瀏覽器測試每個端點，理解它們的作用。

---

### 選項 B: 快速模式（適合有經驗的開發者）

如果你想**快速開始開發**：

```powershell
# 一鍵設置
.\scripts\setup_env.ps1

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 啟動 API
uvicorn app.main:app --reload

# 另開一個終端機，執行測試
python tests\test_basic.py
```

完成！🎉

---

## 🧪 測試你的理解

完成設置後，嘗試這些練習來驗證你的理解：

### 練習 1: 修改配置 ⭐

在 `config.py` 中新增一個配置：

```python
# 新增分頁設定
DEFAULT_PAGE_SIZE: int = 10
MAX_PAGE_SIZE: int = 100
```

然後在 `.env` 中覆蓋預設值：
```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=50
```

重新啟動 API，確認新配置生效。

### 練習 2: 增強健康檢查 ⭐⭐

修改 `/health` 端點，加入真實的資料庫連線檢查：

```python
@app.get("/health", tags=["Health"])
async def health_check():
    from app.database import db
    
    # 測試資料庫連線
    db_status = "connected"
    try:
        await db.client.admin.command('ping')
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": settings.PROJECT_NAME,
        "database": db_status
    }
```

### 練習 3: 新增資料庫資訊端點 ⭐⭐⭐

創建一個新端點，顯示資料庫版本和連線資訊：

```python
@app.get("/db-info", tags=["Database"])
async def database_info():
    from app.database import db
    try:
        server_info = await db.client.server_info()
        
        # 列出所有資料庫
        db_list = await db.client.list_database_names()
        
        # 獲取當前資料庫的集合
        collections = await db.db.list_collection_names()
        
        return {
            "mongodb_version": server_info.get("version"),
            "current_database": settings.MONGODB_DB_NAME,
            "total_databases": len(db_list),
            "collections_in_current_db": collections,
            "connection": "successful"
        }
    except Exception as e:
        return {
            "error": str(e),
            "connection": "failed"
        }
```

測試這個新端點：
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/db-info" -Method Get
```

---

## 🐛 常見問題速查

### ❌ 連線錯誤
```
❌ MongoDB 連線失敗: Connection refused
```

**檢查清單**：
1. ✅ MongoDB 服務是否運行？
2. ✅ .env 中的 MONGODB_URL 正確嗎？
3. ✅ 防火牆是否阻擋了連線？

**快速修復**：
```powershell
Start-Service -Name MongoDB
# 或
mongod --dbpath "C:\data\db"
```

### ❌ 埠號被佔用
```
ERROR: [Errno 10048] Only one usage...
```

**快速修復**：
```powershell
# 使用不同埠號
uvicorn app.main:app --reload --port 8001
```

### ❌ 模組找不到
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**快速修復**：
```powershell
.\venv\Scripts\Activate.ps1
pip install pydantic-settings
```

---

## 📚 關鍵文件說明

| 文件 | 作用 | 何時閱讀 |
|------|------|----------|
| `QUICK_START.md` | 5 分鐘快速開始 | 想要快速運行時 |
| `DAY2-3_LEARNING_GUIDE.md` | 深入學習指南 | 想要理解原理時 |
| `HOW_TO_RUN.md` | 本文件 | 實際操作時 |
| `PHASE1_PROGRESS.md` | 開發進度追蹤 | 查看整體進度時 |

---

## 🎯 驗收標準

完成以下所有項目，表示 Day 2-3 成功完成：

```
✅ .env 檔案已建立並配置正確
✅ MongoDB 連線成功
✅ FastAPI 應用成功啟動
✅ http://localhost:8000 顯示歡迎訊息
✅ http://localhost:8000/health 返回 {"status": "healthy"}
✅ http://localhost:8000/docs 顯示 Swagger UI
✅ 測試腳本全部通過（test_basic.py）
✅ 理解配置管理的概念
✅ 理解異步資料庫連線
✅ 理解 FastAPI 的生命週期
```

---

## 🚀 下一步

Day 2-3 完成後，你可以選擇：

### 選項 1: 繼續深入學習
- 完成 DAY2-3_LEARNING_GUIDE.md 中的所有練習
- 閱讀延伸資源
- 嘗試優化現有代碼

### 選項 2: 進入下一階段
- Day 4-5: 通用模型與工具函數
- Week 2: 用戶認證系統
- Week 3: 商品管理功能

### 選項 3: 實驗與探索
- 嘗試部署到 Docker
- 整合 MongoDB Atlas（雲端資料庫）
- 加入 Redis 快取層

---

## 💡 學習建議

### 對於初學者：
1. 📖 **先理解，再動手**：閱讀學習指南後再寫代碼
2. 🔍 **逐行分析**：理解每一行代碼的作用
3. 🧪 **多實驗**：修改參數，看看會發生什麼
4. 📝 **做筆記**：記錄你的理解和困惑

### 對於有經驗的開發者：
1. 🏗️ **關注架構**：理解為什麼這樣設計
2. 🔧 **思考改進**：有更好的實作方式嗎？
3. 📊 **效能考量**：連線池大小、超時設定等
4. 🧩 **延伸學習**：FastAPI、Motor、Pydantic 的進階功能

---

**準備好了嗎？開始你的 FastAPI + MongoDB 之旅！** 🚀

有問題？查看 `DAY2-3_LEARNING_GUIDE.md` 或開發進度文檔！

