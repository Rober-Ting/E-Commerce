# 電商訂單管理系統 - 快速參考手冊

> 快速查找常用資訊、指令和程式碼片段

---

## 📑 目錄

- [專案資訊](#專案資訊)
- [常用指令](#常用指令)
- [環境變數](#環境變數)
- [API 端點速查](#api-端點速查)
- [資料模型速查](#資料模型速查)
- [MongoDB 查詢速查](#mongodb-查詢速查)
- [程式碼片段](#程式碼片段)
- [錯誤排查](#錯誤排查)

---

## 專案資訊

### 技術棧
```
後端: FastAPI + Motor (async PyMongo)
資料庫: MongoDB 6.0+
認證: JWT (python-jose)
密碼: bcrypt (passlib)
驗證: Pydantic
```

### 專案結構
```
ecommerce-api/
├── app/
│   ├── main.py          # FastAPI 應用入口
│   ├── config.py        # 配置管理
│   ├── database.py      # MongoDB 連線
│   ├── models/          # Pydantic 模型
│   ├── api/v1/          # API 路由
│   ├── services/        # 業務邏輯
│   ├── utils/           # 工具函數
│   └── middleware/      # 中介軟體
├── tests/               # 測試
├── scripts/             # 腳本
└── Documents/           # 文檔
```

---

## 常用指令

### 環境設定
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
venv\Scripts\activate

# 啟動虛擬環境 (Linux/Mac)
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 開發運行
```bash
# 啟動 FastAPI 開發伺服器（熱重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 啟動生產模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### MongoDB
```bash
# 啟動 MongoDB (Windows)
mongod --dbpath "C:\data\db"

# 啟動 MongoDB Shell
mongosh

# 連接到資料庫
mongosh "mongodb://localhost:27017/ecommerce_db"

# 匯出資料
mongoexport --db=ecommerce_db --collection=users --out=users.json

# 匯入資料
mongoimport --db=ecommerce_db --collection=users --file=users.json
```

### Docker
```bash
# 建立映像
docker build -t ecommerce-api .

# 運行容器
docker run -p 8000:8000 ecommerce-api

# 使用 Docker Compose
docker-compose up -d

# 停止容器
docker-compose down

# 查看日誌
docker-compose logs -f api
```

### 測試
```bash
# 運行所有測試
pytest

# 運行特定測試檔案
pytest tests/test_auth.py

# 顯示測試覆蓋率
pytest --cov=app tests/

# 運行測試並生成 HTML 報告
pytest --cov=app --cov-report=html tests/
```

### Git
```bash
# 初始化倉庫
git init

# 添加所有檔案
git add .

# 提交變更
git commit -m "feat: add user authentication"

# 查看狀態
git status

# 建立分支
git checkout -b feature/user-management

# 合併分支
git merge feature/user-management
```

---

## 環境變數

### `.env` 檔案範例
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ecommerce_db

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=E-Commerce API
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 生成安全的 SECRET_KEY
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## API 端點速查

### Base URL
```
Development: http://localhost:8000
API Prefix: /api/v1
Swagger UI: http://localhost:8000/docs
```

### 認證 API
```
POST   /api/v1/auth/register     # 用戶註冊
POST   /api/v1/auth/login        # 用戶登入
POST   /api/v1/auth/logout       # 用戶登出
GET    /api/v1/auth/me           # 獲取當前用戶 [需認證]
```

### 用戶 API
```
GET    /api/v1/users             # 用戶列表 [需認證: admin]
GET    /api/v1/users/{id}        # 用戶詳情 [需認證]
PUT    /api/v1/users/{id}        # 更新用戶 [需認證]
DELETE /api/v1/users/{id}        # 刪除用戶 [需認證: admin]
POST   /api/v1/users/{id}/addresses  # 新增地址 [需認證]
```

### 商品 API
```
GET    /api/v1/products          # 商品列表 [公開]
GET    /api/v1/products/{id}     # 商品詳情 [公開]
POST   /api/v1/products          # 新增商品 [需認證: admin]
PUT    /api/v1/products/{id}     # 更新商品 [需認證: admin]
DELETE /api/v1/products/{id}     # 刪除商品 [需認證: admin]
```

### 訂單 API
```
GET    /api/v1/orders            # 訂單列表 [需認證]
GET    /api/v1/orders/{id}       # 訂單詳情 [需認證]
POST   /api/v1/orders            # 建立訂單 [需認證]
PATCH  /api/v1/orders/{id}/status  # 更新狀態 [需認證: admin]
DELETE /api/v1/orders/{id}       # 取消訂單 [需認證]
```

### 分析 API
```
GET    /api/v1/analytics/sales/summary     # 銷售總覽 [需認證: admin]
GET    /api/v1/analytics/sales/trends      # 銷售趨勢 [需認證: admin]
GET    /api/v1/analytics/products/top-selling  # 暢銷商品 [需認證: admin]
GET    /api/v1/analytics/customers/top-buyers  # 最佳客戶 [需認證: admin]
```

---

## 資料模型速查

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password_hash: String,
  name: String,
  phone: String,
  role: String,  // "admin", "customer", "vendor"
  addresses: [Address],
  is_active: Boolean,
  created_at: ISODate,
  updated_at: ISODate
}
```

### Products Collection
```javascript
{
  _id: ObjectId,
  name: String (indexed),
  description: String,
  price: Decimal128,
  stock: Number,
  category: String (indexed),
  tags: [String],
  images: [String],
  status: String,  // "active", "inactive", "out_of_stock"
  is_deleted: Boolean,
  created_at: ISODate,
  updated_at: ISODate
}
```

### Orders Collection
```javascript
{
  _id: ObjectId,
  order_number: String (unique, indexed),
  user_id: ObjectId (indexed),
  items: [OrderItem],
  total_amount: Decimal128,
  status: String,  // "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"
  shipping_address: Address,
  created_at: ISODate (indexed),
  updated_at: ISODate
}
```

---

## MongoDB 查詢速查

### 基本查詢
```javascript
// 查詢所有文件
db.users.find()

// 查詢特定條件
db.users.find({ email: "alice@example.com" })

// 查詢一個文件
db.users.findOne({ _id: ObjectId("...") })

// 查詢並投影
db.users.find({}, { name: 1, email: 1, _id: 0 })
```

### 查詢操作符
```javascript
// 比較操作符
db.products.find({ price: { $gt: 1000 } })        // 大於
db.products.find({ price: { $gte: 1000 } })       // 大於等於
db.products.find({ price: { $lt: 5000 } })        // 小於
db.products.find({ price: { $lte: 5000 } })       // 小於等於
db.products.find({ price: { $ne: 1000 } })        // 不等於

// 邏輯操作符
db.products.find({
  $and: [
    { price: { $gte: 1000 } },
    { stock: { $gt: 0 } }
  ]
})

db.products.find({
  $or: [
    { category: "筆記型電腦" },
    { category: "平板電腦" }
  ]
})

// 陣列操作符
db.products.find({ tags: "Apple" })               // 包含
db.products.find({ tags: { $in: ["Apple", "Samsung"] } })
db.products.find({ tags: { $all: ["Apple", "M3"] } })
```

### 更新操作
```javascript
// 更新單一文件
db.products.updateOne(
  { _id: ObjectId("...") },
  { $set: { price: 59900 } }
)

// 更新多個文件
db.products.updateMany(
  { category: "筆記型電腦" },
  { $set: { status: "active" } }
)

// 增加數值
db.products.updateOne(
  { _id: ObjectId("...") },
  { $inc: { stock: -1 } }
)

// 陣列操作
db.products.updateOne(
  { _id: ObjectId("...") },
  { $push: { tags: "新標籤" } }
)

db.products.updateOne(
  { _id: ObjectId("...") },
  { $pull: { tags: "舊標籤" } }
)
```

### 聚合管道
```javascript
// 統計每月銷售額
db.orders.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m", date: "$created_at" } },
      total: { $sum: "$total_amount" },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])

// 最暢銷商品
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product_id",
      total_quantity: { $sum: "$items.quantity" },
      total_revenue: { $sum: "$items.subtotal" }
    }
  },
  { $sort: { total_quantity: -1 } },
  { $limit: 10 }
])
```

### 索引管理
```javascript
// 建立索引
db.users.createIndex({ email: 1 }, { unique: true })
db.products.createIndex({ name: 1, category: 1 })

// 查看索引
db.users.getIndexes()

// 刪除索引
db.users.dropIndex("email_1")
```

---

## 程式碼片段

### FastAPI 路由範例
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """獲取當前用戶資訊"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"]
    )
```

### MongoDB 查詢 (Motor)
```python
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return user
```

### JWT Token 生成
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 密碼加密與驗證
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密密碼
hashed = pwd_context.hash("user_password")

# 驗證密碼
is_valid = pwd_context.verify("user_password", hashed)
```

### Pydantic 模型
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe",
                "phone": "+886912345678"
            }
        }
```

### 錯誤處理
```python
from fastapi import HTTPException, status

# 拋出 HTTP 錯誤
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

# 自定義錯誤類別
class APIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

# 使用
raise APIException(
    code="EMAIL_EXISTS",
    message="Email already registered",
    status_code=400
)
```

### 依賴注入
```python
from fastapi import Depends
from app.database import get_database

async def get_current_user(
    db = Depends(get_database),
    credentials = Depends(security)
):
    # 驗證邏輯
    return user

# 使用
@router.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"user": current_user["name"]}
```

---

## 錯誤排查

### 常見問題與解決方案

#### 1. MongoDB 連線失敗
```
錯誤: pymongo.errors.ServerSelectionTimeoutError

解決方案:
1. 確認 MongoDB 服務已啟動
   - Windows: 檢查服務管理員
   - 指令: mongod --dbpath "C:\data\db"

2. 檢查連線字串
   - 確認 MONGODB_URL 正確
   - 預設: mongodb://localhost:27017

3. 檢查防火牆設定
   - 確認 27017 端口未被封鎖
```

#### 2. JWT Token 錯誤
```
錯誤: jose.exceptions.JWTError

解決方案:
1. 確認 SECRET_KEY 已設定且一致
2. 檢查 Token 是否過期
3. 確認 ALGORITHM 設定正確 (預設: HS256)
4. Token 格式: "Bearer <token>"
```

#### 3. Pydantic 驗證錯誤
```
錯誤: pydantic.error_wrappers.ValidationError

解決方案:
1. 檢查請求資料格式
2. 確認必填欄位已提供
3. 檢查資料型別是否正確
4. 查看 Swagger UI 的 Schema 定義
```

#### 4. CORS 錯誤
```
錯誤: Access to fetch at ... has been blocked by CORS policy

解決方案:
在 main.py 中添加 CORS 中介軟體:

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5. 匯入錯誤
```
錯誤: ModuleNotFoundError: No module named 'app'

解決方案:
1. 確認在專案根目錄執行
2. 確認虛擬環境已啟動
3. 確認 PYTHONPATH 設定
   - 設定: export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

#### 6. 異步函數錯誤
```
錯誤: RuntimeError: no running event loop

解決方案:
1. 確認使用 async/await
2. 使用 Motor (不是 PyMongo) 進行異步操作
3. 路由函數使用 async def
```

### 除錯技巧

#### 1. 查看詳細錯誤
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 使用 print/logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

#### 3. 使用 FastAPI 除錯模式
```python
# main.py
app = FastAPI(debug=True)

# 或在啟動時
uvicorn app.main:app --reload --log-level debug
```

#### 4. MongoDB 查詢除錯
```python
# 查看執行計劃
cursor = db.products.find({ "price": { "$gt": 1000 } })
print(cursor.explain())
```

---

## 測試範例

### cURL 測試
```bash
# 註冊
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!","name":"Test User"}'

# 登入
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'

# 獲取用戶資訊（需要 Token）
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 建立商品（需要 admin Token）
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name":"Test Product","description":"Test","price":100,"stock":10,"category":"Test"}'
```

### Python Requests 測試
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 註冊
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "Test1234!",
    "name": "Test User"
})
print(response.json())

# 登入並獲取 Token
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "Test1234!"
})
token = response.json()["data"]["access_token"]

# 使用 Token 訪問受保護路由
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(response.json())
```

---

## 效能監控

### 查詢效能分析
```javascript
// MongoDB explain
db.products.find({ category: "筆記型電腦" }).explain("executionStats")

// 查看慢查詢
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().limit(10).sort({ ts: -1 })
```

### API 回應時間監控
```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 快速參考連結

### 文檔
- [專案總覽](./PROJECT_SUMMARY.md)
- [開發路線圖](./ecommerce_development_roadmap.md)
- [API 文檔](./ecommerce_api_documentation.md)
- [資料模型](./ecommerce_data_model_design.md)

### 外部資源
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [MongoDB 文檔](https://docs.mongodb.com/)
- [Motor 文檔](https://motor.readthedocs.io/)
- [Pydantic 文檔](https://docs.pydantic.dev/)

---

**快速參考版本**: 1.0  
**最後更新**: 2025-10-22

**提示**: 建議將此文件加入書籤，以便快速查找！ 📌

