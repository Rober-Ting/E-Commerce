# Day 2-3: 資料庫連線與配置 - 學習指南

## 🎯 學習目標

透過本教程，你將學習：
1. **配置管理模式** - 為什麼需要配置管理？
2. **環境變數** - 如何安全管理敏感資訊
3. **異步資料庫連線** - Motor 與 AsyncIO 的概念
4. **依賴注入** - FastAPI 的核心設計模式
5. **應用生命週期** - 啟動與關閉事件處理
6. **測試驅動開發** - 如何測試你的 API

---

## 📖 第一部分：理解配置管理（config.py）

### 🤔 為什麼需要配置管理？

想像你正在開發一個應用程式：
- **開發環境**: 使用本地 MongoDB (localhost)
- **測試環境**: 使用測試專用資料庫
- **生產環境**: 使用雲端 MongoDB (安全連線)

如果把這些配置寫死在代碼裡，每次切換環境都要改代碼！**配置管理就是為了解決這個問題**。

### 💡 關鍵設計模式：

#### 1. **Pydantic Settings**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    SECRET_KEY: str = "your-secret-key"
```

**為什麼使用 Pydantic？**
- ✅ **型別驗證**: 確保配置值的型別正確
- ✅ **自動載入**: 從 .env 檔案自動讀取
- ✅ **預設值**: 沒有 .env 時使用預設值
- ✅ **IDE 支援**: 程式碼提示和自動完成

#### 2. **環境變數優先級**
```
.env 檔案 > 系統環境變數 > 預設值
```

#### 3. **單例模式 (Singleton)**
```python
settings = Settings()  # 全域唯一實例
```

整個應用只有一個 settings 實例，避免重複讀取。

### 🔍 深入理解：Property 裝飾器

```python
@property
def allowed_origins_list(self) -> list:
    return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
```

**為什麼這樣設計？**
- 環境變數只能是字串
- 但 CORS 需要列表
- 使用 `@property` 動態轉換，保持資料來源的簡潔

---

## 📖 第二部分：理解異步資料庫連線（database.py）

### 🤔 什麼是異步 (Async)？

想像一個餐廳：
- **同步 (Sync)**: 服務員接單後，站在廚房等菜煮好才能接下一單
- **異步 (Async)**: 服務員接單後，去服務其他客人，菜好了再回來拿

**Web API 中的異步**：處理 MongoDB 查詢時，不會阻塞其他請求！

### 💡 關鍵設計模式：

#### 1. **資料庫連線池 (Connection Pool)**

```python
class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()  # 全域單例
```

**為什麼這樣設計？**
- ✅ **連線重用**: 避免每次請求都建立新連線
- ✅ **效能優化**: 連線池自動管理連線數量
- ✅ **資源管理**: 統一的連線與斷線控制

#### 2. **連線測試：Ping 命令**

```python
await db.client.admin.command('ping')
```

這是 MongoDB 的健康檢查，確認連線真的成功！

#### 3. **依賴注入 (Dependency Injection)**

```python
def get_database() -> AsyncIOMotorDatabase:
    return db.db
```

**在 FastAPI 中使用：**
```python
@app.get("/users")
async def get_users(database: AsyncIOMotorDatabase = Depends(get_database)):
    users = await database.users.find().to_list(100)
    return users
```

**好處**：
- 測試時可以注入假的資料庫
- 代碼解耦，易於維護

---

## 📖 第三部分：理解應用生命週期（main.py）

### 🤔 為什麼需要啟動/關閉事件？

資料庫連線是有成本的：
- **啟動時**: 建立連線池，測試連線
- **關閉時**: 正確關閉連線，釋放資源

不正確關閉可能導致：
- 資料庫連線洩漏
- 資料損壞
- 系統資源耗盡

### 💡 FastAPI 事件處理

```python
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
```

**執行順序**：
1. 應用啟動 → `startup_event` 執行
2. 接收請求 → 處理業務邏輯
3. 應用關閉 (Ctrl+C) → `shutdown_event` 執行

### 🔍 CORS 中介軟體

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境：允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**什麼是 CORS？**
瀏覽器安全機制，防止惡意網站竊取資料。

**範例**：
- 前端運行在 `localhost:3000`
- API 運行在 `localhost:8000`
- 沒有 CORS 設定 → 瀏覽器阻止請求 ❌
- 有 CORS 設定 → 允許跨域請求 ✅

---

## 🧪 第四部分：實際測試

### 步驟 1: 確認 MongoDB 運行

```powershell
# 檢查 MongoDB 服務狀態
Get-Service -Name MongoDB

# 如果沒運行，啟動它
Start-Service -Name MongoDB

# 或使用 mongod 直接啟動（如果不是服務安裝）
mongod --dbpath "C:\data\db"
```

### 步驟 2: 建立 .env 檔案

```powershell
cd ecommerce-api
Copy-Item .env.example .env
```

然後編輯 `.env` 檔案，設定真實的配置。

### 步驟 3: 生成安全的 SECRET_KEY

**為什麼需要 SECRET_KEY？**
用於 JWT token 簽名，確保 token 不被偽造。

```python
# 使用 Python 生成
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步驟 4: 啟動應用

```powershell
# 啟動虛擬環境（如果還沒啟動）
.\venv\Scripts\Activate.ps1

# 啟動 API 服務器
uvicorn app.main:app --reload
```

**重要參數說明**：
- `app.main:app` - 從 `app/main.py` 載入 `app` 物件
- `--reload` - 代碼變更時自動重啟（開發專用）

### 步驟 5: 測試 API 端點

#### 方法 1: 瀏覽器測試
1. 開啟瀏覽器
2. 訪問 `http://localhost:8000` - 查看歡迎訊息
3. 訪問 `http://localhost:8000/health` - 檢查健康狀態
4. 訪問 `http://localhost:8000/docs` - Swagger UI (互動式文檔)

#### 方法 2: PowerShell 測試
```powershell
# 測試根路由
Invoke-RestMethod -Uri "http://localhost:8000" -Method Get

# 測試健康檢查
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# 詳細輸出
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get | Select-Object -Expand Content
```

#### 方法 3: Python 測試腳本
創建 `tests/test_basic.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print("✅ 根路由測試通過")
    print(f"   訊息: {data['message']}")

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ 健康檢查測試通過")
    print(f"   狀態: {data['status']}")
    print(f"   資料庫: {data['database']}")

if __name__ == "__main__":
    test_root()
    test_health()
    print("\n🎉 所有測試通過！")
```

運行測試：
```powershell
python tests\test_basic.py
```

---

## 🔍 第五部分：除錯與問題排查

### 常見問題 1: MongoDB 連線失敗

**錯誤訊息**：
```
❌ MongoDB 連線失敗: [Errno 111] Connection refused
```

**解決方案**：
1. 確認 MongoDB 服務運行
2. 檢查 `.env` 中的 `MONGODB_URL`
3. 嘗試用 MongoDB Compass 連線測試

### 常見問題 2: 埠號已被佔用

**錯誤訊息**：
```
ERROR: [Errno 10048] Only one usage of each socket address
```

**解決方案**：
```powershell
# 指定不同埠號
uvicorn app.main:app --reload --port 8001
```

### 常見問題 3: 模組找不到

**錯誤訊息**：
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**解決方案**：
```powershell
pip install pydantic-settings
```

---

## 📝 第六部分：動手練習

### 練習 1: 新增配置項

在 `config.py` 中新增一個配置：

```python
# 分頁設定
DEFAULT_PAGE_SIZE: int = 10
MAX_PAGE_SIZE: int = 100
```

然後在 `.env` 中測試覆蓋預設值。

### 練習 2: 增強健康檢查

修改 `/health` 端點，加入資料庫連線檢查：

```python
@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "connected"
    try:
        # 測試資料庫連線
        from app.database import db
        await db.client.admin.command('ping')
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": settings.PROJECT_NAME,
        "database": db_status
    }
```

### 練習 3: 新增資料庫狀態端點

創建一個新端點顯示資料庫資訊：

```python
@app.get("/db-info", tags=["Database"])
async def database_info():
    from app.database import db
    try:
        # 獲取伺服器資訊
        server_info = await db.client.server_info()
        return {
            "database_name": settings.MONGODB_DB_NAME,
            "mongodb_version": server_info.get("version"),
            "connection": "successful"
        }
    except Exception as e:
        return {
            "error": str(e),
            "connection": "failed"
        }
```

---

## ✅ 驗收清單

完成以下所有項目，表示你已經掌握 Day 2-3 的內容：

- [ ] 理解為什麼需要配置管理
- [ ] 知道如何使用環境變數
- [ ] 理解異步程式設計的概念
- [ ] 理解依賴注入的好處
- [ ] 成功啟動 FastAPI 應用
- [ ] MongoDB 連線成功
- [ ] `/` 和 `/health` 端點可以正常訪問
- [ ] Swagger UI 文檔可以正常顯示
- [ ] 能夠使用 PowerShell 或 Python 測試 API
- [ ] 完成至少一個動手練習

---

## 🚀 下一步

完成 Day 2-3 後，你將進入：
- **Day 3-4**: 深入 FastAPI 路由與中介軟體
- **Day 4-5**: 用戶認證與 JWT
- **Week 2**: 實作用戶、商品、訂單管理

---

## 📚 延伸閱讀

1. [Pydantic Settings 官方文檔](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
2. [Motor 異步驅動文檔](https://motor.readthedocs.io/)
3. [FastAPI 依賴注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
4. [Python AsyncIO 入門](https://docs.python.org/3/library/asyncio.html)

---

**Happy Coding! 🎉**

