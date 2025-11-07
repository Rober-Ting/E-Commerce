# 電商訂單管理系統 - 技術架構設計

## 1. 整體架構

### 1.1 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  (Postman / Swagger UI / Frontend App)                  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/HTTPS
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API Gateway / Nginx                    │
│              (Load Balancer - Optional)                  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                 Application Layer                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           FastAPI Application                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │   Auth     │  │  Products  │  │   Orders   │ │  │
│  │  │  Service   │  │  Service   │  │  Service   │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘ │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │   Users    │  │ Analytics  │  │   Utils    │ │  │
│  │  │  Service   │  │  Service   │  │  Service   │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Middleware Layer                         │  │
│  │  • Authentication (JWT)                           │  │
│  │  • Authorization (RBAC)                           │  │
│  │  • Error Handling                                 │  │
│  │  • Logging                                        │  │
│  │  • CORS                                           │  │
│  │  • Rate Limiting                                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  Data Access Layer                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            PyMongo / Motor Driver                 │  │
│  │  • Connection Pool Management                     │  │
│  │  • Query Optimization                             │  │
│  │  • Transaction Support                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  Database Layer                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              MongoDB 6.0+                         │  │
│  │                                                   │  │
│  │  [users]  [products]  [orders]  [categories]     │  │
│  │                                                   │  │
│  │  • Indexes                                        │  │
│  │  • Replica Set (Optional)                        │  │
│  │  • Sharding (Future)                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 技術選型

### 2.1 後端框架: FastAPI

#### 選擇理由
1. **高效能**: 基於 Starlette 和 Pydantic，效能優異
2. **自動 API 文檔**: 內建 Swagger UI 和 ReDoc
3. **型別檢查**: 使用 Python Type Hints
4. **異步支援**: 原生支援 async/await
5. **資料驗證**: Pydantic 自動驗證
6. **現代化**: Python 3.6+ 新特性

#### 替代方案
- **Flask**: 輕量級，但需要更多手動配置
- **Django**: 功能完整但較重量級，適合大型專案

### 2.2 資料庫驅動: PyMongo + Motor

#### PyMongo (同步)
```python
# 適合: 一般 CRUD 操作
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
```

#### Motor (異步)
```python
# 適合: 高併發場景，與 FastAPI 完美搭配
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
```

**建議**: 本專案使用 **Motor** 實現異步操作

### 2.3 認證機制: JWT (JSON Web Tokens)

#### 套件選擇
```python
# PyJWT + passlib
pip install python-jose[cryptography] passlib[bcrypt]
```

#### Token 結構
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "customer",
  "exp": 1698765432
}
```

### 2.4 資料驗證: Pydantic

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None
```

---

## 3. 專案結構

### 3.1 推薦目錄結構

```
ecommerce-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 應用入口
│   ├── config.py                  # 配置管理
│   ├── database.py                # MongoDB 連線
│   │
│   ├── models/                    # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── common.py
│   │
│   ├── schemas/                   # MongoDB Schema (可選)
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   └── product_schema.py
│   │
│   ├── api/                       # API 路由
│   │   ├── __init__.py
│   │   ├── deps.py               # 依賴注入
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   └── analytics.py
│   │
│   ├── services/                  # 業務邏輯層
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── analytics_service.py
│   │
│   ├── repositories/              # 資料存取層 (可選)
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── product_repository.py
│   │   └── order_repository.py
│   │
│   ├── utils/                     # 工具函數
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, 密碼加密
│   │   ├── validators.py         # 自定義驗證器
│   │   └── helpers.py            # 輔助函數
│   │
│   └── middleware/                # 中介軟體
│       ├── __init__.py
│       ├── error_handler.py
│       ├── logging.py
│       └── rate_limiter.py
│
├── tests/                         # 測試
│   ├── __init__.py
│   ├── conftest.py               # pytest 配置
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_products.py
│   └── test_orders.py
│
├── scripts/                       # 腳本
│   ├── init_db.py                # 初始化資料庫
│   ├── seed_data.py              # 測試資料
│   └── create_indexes.py         # 建立索引
│
├── docs/                          # 文檔
│   ├── api_documentation.md
│   └── deployment_guide.md
│
├── .env.example                   # 環境變數範例
├── .env                          # 環境變數 (不提交)
├── .gitignore
├── requirements.txt              # 依賴套件
├── Dockerfile                    # Docker 配置
├── docker-compose.yml            # Docker Compose 配置
├── pytest.ini                    # pytest 配置
├── README.md                     # 專案說明
└── alembic/                      # 資料庫遷移 (MongoDB 不常用)
```

---

## 4. 核心模組設計

### 4.1 認證與授權模組

#### 功能
- 用戶註冊與登入
- JWT Token 生成與驗證
- 密碼加密與驗證
- 權限檢查

#### 關鍵程式碼架構

```python
# app/utils/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: list):
    async def role_checker(current_user = Depends(get_current_user)):
        # 從資料庫獲取用戶角色並檢查
        user = await db.users.find_one({"_id": current_user})
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return role_checker
```

### 4.2 商品管理模組

#### Service Layer
```python
# app/services/product_service.py
from typing import Optional, List
from bson import ObjectId
from app.models.product import ProductCreate, ProductUpdate, ProductInDB

class ProductService:
    def __init__(self, db):
        self.collection = db["products"]
    
    async def create_product(self, product: ProductCreate) -> str:
        product_dict = product.dict()
        product_dict["created_at"] = datetime.utcnow()
        product_dict["is_deleted"] = False
        result = await self.collection.insert_one(product_dict)
        return str(result.inserted_id)
    
    async def get_product(self, product_id: str) -> Optional[ProductInDB]:
        if not ObjectId.is_valid(product_id):
            return None
        product = await self.collection.find_one({
            "_id": ObjectId(product_id),
            "is_deleted": False
        })
        return ProductInDB(**product) if product else None
    
    async def list_products(
        self, 
        skip: int = 0, 
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductInDB]:
        query = {"is_deleted": False}
        
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)
        return [ProductInDB(**p) for p in products]
```

### 4.3 訂單管理模組 (含事務處理)

```python
# app/services/order_service.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession

class OrderService:
    def __init__(self, db):
        self.orders_collection = db["orders"]
        self.products_collection = db["products"]
        self.client = db.client
    
    async def create_order(self, user_id: str, order_data: OrderCreate):
        # 使用 MongoDB 事務確保原子性
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                try:
                    # 1. 檢查並扣減庫存
                    order_items = []
                    total_amount = 0
                    
                    for item in order_data.items:
                        product = await self.products_collection.find_one(
                            {"_id": ObjectId(item.product_id)},
                            session=session
                        )
                        
                        if not product:
                            raise ValueError(f"Product {item.product_id} not found")
                        
                        if product["stock"] < item.quantity:
                            raise ValueError(
                                f"Insufficient stock for {product['name']}"
                            )
                        
                        # 扣減庫存
                        await self.products_collection.update_one(
                            {"_id": ObjectId(item.product_id)},
                            {"$inc": {"stock": -item.quantity}},
                            session=session
                        )
                        
                        # 計算訂單明細
                        subtotal = product["price"] * item.quantity
                        order_items.append({
                            "product_id": item.product_id,
                            "product_name": product["name"],
                            "quantity": item.quantity,
                            "price": product["price"],
                            "subtotal": subtotal
                        })
                        total_amount += subtotal
                    
                    # 2. 建立訂單
                    order = {
                        "order_number": self._generate_order_number(),
                        "user_id": ObjectId(user_id),
                        "items": order_items,
                        "total_amount": total_amount,
                        "status": "pending",
                        "created_at": datetime.utcnow(),
                        "status_history": [{
                            "status": "pending",
                            "timestamp": datetime.utcnow()
                        }]
                    }
                    
                    result = await self.orders_collection.insert_one(
                        order, session=session
                    )
                    
                    return str(result.inserted_id)
                
                except Exception as e:
                    await session.abort_transaction()
                    raise e
    
    def _generate_order_number(self) -> str:
        # 生成唯一訂單編號
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.digits, k=6))
        return f"ORD{timestamp}{random_suffix}"
```

### 4.4 數據分析模組

```python
# app/services/analytics_service.py
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, db):
        self.orders_collection = db["orders"]
        self.users_collection = db["users"]
    
    async def get_sales_summary(
        self, 
        start_date: datetime, 
        end_date: datetime
    ):
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    },
                    "status": {"$in": ["completed", "shipped", "delivered"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_orders": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "average_order_value": {"$avg": "$total_amount"}
                }
            }
        ]
        
        result = await self.orders_collection.aggregate(pipeline).to_list(1)
        return result[0] if result else None
    
    async def get_top_selling_products(self, limit: int = 10):
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": "$items.subtotal"}
                }
            },
            {"$sort": {"total_quantity": -1}},
            {"$limit": limit}
        ]
        
        return await self.orders_collection.aggregate(pipeline).to_list(limit)
    
    async def get_top_customers(self, limit: int = 10):
        pipeline = [
            {
                "$group": {
                    "_id": "$user_id",
                    "order_count": {"$sum": 1},
                    "total_spent": {"$sum": "$total_amount"}
                }
            },
            {"$sort": {"order_count": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "_id": 0,
                    "user_id": "$_id",
                    "user_name": "$user_info.name",
                    "user_email": "$user_info.email",
                    "order_count": 1,
                    "total_spent": 1
                }
            }
        ]
        
        return await self.orders_collection.aggregate(pipeline).to_list(limit)
```

---

## 5. 資料庫設計

### 5.1 索引策略

```python
# scripts/create_indexes.py
async def create_indexes(db):
    # Users Collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    
    # Products Collection
    await db.products.create_index("name")
    await db.products.create_index("category")
    await db.products.create_index("status")
    await db.products.create_index([("name", "text"), ("description", "text")])
    
    # Orders Collection
    await db.orders.create_index("order_number", unique=True)
    await db.orders.create_index("user_id")
    await db.orders.create_index("status")
    await db.orders.create_index("created_at")
    await db.orders.create_index([("user_id", 1), ("created_at", -1)])
```

### 5.2 資料驗證 (Schema Validation)

```javascript
// MongoDB Schema Validation (在 MongoDB Shell 中執行)
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "password_hash", "name", "role"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        role: {
          enum: ["admin", "customer", "vendor"]
        },
        is_active: {
          bsonType: "bool"
        }
      }
    }
  }
});
```

---

## 6. API 設計規範

### 6.1 RESTful API 設計原則

| HTTP Method | 用途 | 示例 |
|------------|------|------|
| GET | 獲取資源 | `GET /api/v1/products` |
| POST | 建立資源 | `POST /api/v1/products` |
| PUT | 完整更新資源 | `PUT /api/v1/products/123` |
| PATCH | 部分更新資源 | `PATCH /api/v1/products/123` |
| DELETE | 刪除資源 | `DELETE /api/v1/products/123` |

### 6.2 回應格式標準化

```python
# 成功回應
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}

# 錯誤回應
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product with ID 123 not found",
    "details": null
  }
}

# 分頁回應
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 6.3 錯誤處理

```python
# app/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse

class ErrorResponse(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except ErrorResponse as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred"
                }
            }
        )
```

---

## 7. 安全性設計

### 7.1 密碼安全
- 使用 bcrypt 加密 (cost factor: 12)
- 密碼長度至少 8 字元
- 包含大小寫字母、數字、特殊字元

### 7.2 JWT Token 安全
- Token 有效期: 1 小時
- Refresh Token: 7 天
- 使用 HTTPS 傳輸
- Token 存放在 HTTP-Only Cookie 或 Authorization Header

### 7.3 輸入驗證
- Pydantic 自動驗證資料型別
- 自定義驗證器處理業務規則
- MongoDB Query Injection 防護

### 7.4 CORS 設定
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 生產環境改為實際域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 8. 效能優化

### 8.1 資料庫層面
- 合理建立索引
- 使用投影減少資料傳輸
- 聚合管道優化
- 連線池設定

### 8.2 應用層面
- 異步操作 (async/await)
- 快取機制 (Redis)
- 分頁查詢
- 批量操作

### 8.3 監控與日誌
```python
# app/middleware/logging.py
import logging
from fastapi import Request
import time

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.2f}s "
        f"with status {response.status_code}"
    )
    
    return response
```

---

## 9. 測試策略

### 9.1 單元測試
```python
# tests/test_product_service.py
import pytest
from app.services.product_service import ProductService

@pytest.mark.asyncio
async def test_create_product(test_db):
    service = ProductService(test_db)
    product_data = {
        "name": "Test Product",
        "price": 100,
        "stock": 10
    }
    product_id = await service.create_product(product_data)
    assert product_id is not None
```

### 9.2 整合測試
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 10. 部署方案

### 10.1 Docker 容器化

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://admin:password@mongodb:27017
    depends_on:
      - mongodb

volumes:
  mongodb_data:
```

### 10.2 環境變數管理

```python
# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ecommerce_db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "E-Commerce API"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 總結

本技術架構設計提供了一個**可擴展、高效能、安全**的電商訂單管理系統基礎。主要特點：

✅ **分層架構**: API → Service → Repository → Database  
✅ **異步處理**: 使用 FastAPI + Motor 提升效能  
✅ **事務支援**: MongoDB 事務確保資料一致性  
✅ **安全設計**: JWT 認證、密碼加密、輸入驗證  
✅ **可測試性**: 單元測試與整合測試  
✅ **容器化**: Docker 支援快速部署  

**文件版本**: 1.0  
**最後更新**: 2025-10-22

