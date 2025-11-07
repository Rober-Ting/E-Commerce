# 電商訂單管理系統 - 開發路線圖與執行步驟

## 📋 專案總覽

### 專案資訊
- **專案名稱**: MongoDB 電商訂單管理系統
- **預估開發時間**: 6-8 週
- **開發模式**: 敏捷開發 (Agile)，每週一個迭代
- **版本策略**: v1.0 MVP (最小可行產品) → v2.0 完整功能

---

## 🎯 階段劃分

```
Phase 0: 環境準備 (Week 0)        [已完成部分]
    ↓
Phase 1: 專案初始化 (Week 1)      [接下來執行]
    ↓
Phase 2: 認證與用戶管理 (Week 2)
    ↓
Phase 3: 商品管理 (Week 3)
    ↓
Phase 4: 訂單管理 (Week 4)
    ↓
Phase 5: 數據統計 (Week 5)
    ↓
Phase 6: 測試與優化 (Week 6)
    ↓
Phase 7: 部署與文檔 (Week 7)
    ↓
Phase 8: 進階功能 (Week 8+)      [可選]
```

---

## 📅 詳細開發計劃

## Phase 0: 環境準備 ✅

### 目標
確保開發環境與工具就緒

### 檢查清單
- [x] MongoDB 安裝與運行
- [x] Python 3.10+ 安裝
- [x] Git 版本控制工具
- [x] IDE/編輯器 (VS Code / PyCharm)
- [x] 基礎 MongoDB 學習
- [x] 專案需求文件完成
- [x] 技術架構文件完成

### 產出物
- ✅ `mongodb_learning_guide.md`
- ✅ `ecommerce_project_requirements.md`
- ✅ `ecommerce_technical_architecture.md`
- ✅ `ecommerce_development_roadmap.md` (本文件)

---

## Phase 1: 專案初始化與基礎架構 (Week 1)

### 🎯 目標
建立專案骨架，配置開發環境，實現基礎功能

### 📝 任務清單

#### 1.1 專案建立與環境設定 (Day 1-2)

**步驟**:
1. 建立專案目錄結構
```bash
mkdir ecommerce-api
cd ecommerce-api
```

2. 初始化 Git 倉庫
```bash
git init
echo "__pycache__/
*.pyc
.env
venv/
.vscode/
.pytest_cache/" > .gitignore
```

3. 建立 Python 虛擬環境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. 安裝核心依賴
```bash
pip install fastapi uvicorn motor pydantic python-jose[cryptography] passlib[bcrypt] python-multipart
pip freeze > requirements.txt
```

5. 建立目錄結構（參考技術架構文件）

**產出物**:
- ✅ 專案目錄結構
- ✅ `requirements.txt`
- ✅ `.gitignore`
- ✅ `README.md`

#### 1.2 資料庫連線與配置 (Day 2-3)

**建立檔案**: `app/database.py`
```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

async def close_mongo_connection():
    db.client.close()
    print("Closed MongoDB connection")

def get_database():
    return db.db
```

**建立檔案**: `app/config.py`
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ecommerce_db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**建立檔案**: `.env.example`
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ecommerce_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**產出物**:
- ✅ `app/database.py`
- ✅ `app/config.py`
- ✅ `.env.example`

#### 1.3 FastAPI 應用初始化 (Day 3-4)

**建立檔案**: `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.config import settings

app = FastAPI(
    title="E-Commerce API",
    description="MongoDB 電商訂單管理系統 API",
    version="1.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境需改為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {
        "message": "Welcome to E-Commerce API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**測試運行**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**產出物**:
- ✅ `app/main.py`
- ✅ 可運行的 FastAPI 應用
- ✅ 訪問 http://localhost:8000/docs 查看 Swagger UI

#### 1.4 通用模型與工具函數 (Day 4-5)

**建立檔案**: `app/models/common.py`
```python
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation successful"

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20
    
    @property
    def skip(self):
        return (self.page - 1) * self.per_page

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int
```

**建立檔案**: `app/utils/helpers.py`
```python
from bson import ObjectId
from datetime import datetime
import random
import string

def object_id_to_str(obj_id: ObjectId) -> str:
    return str(obj_id)

def is_valid_object_id(id_str: str) -> bool:
    return ObjectId.is_valid(id_str)

def generate_order_number() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_suffix}"

def parse_object_id(id_str: str) -> Optional[ObjectId]:
    return ObjectId(id_str) if is_valid_object_id(id_str) else None
```

**產出物**:
- ✅ `app/models/common.py`
- ✅ `app/utils/helpers.py`

#### 1.5 錯誤處理中介軟體 (Day 5)

**建立檔案**: `app/middleware/error_handler.py`
```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except APIException as e:
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
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
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

**更新**: `app/main.py` (加入中介軟體)
```python
from app.middleware.error_handler import error_handling_middleware

app.middleware("http")(error_handling_middleware)
```

**產出物**:
- ✅ `app/middleware/error_handler.py`

#### 1.6 日誌配置 (Day 5)

**建立檔案**: `app/utils/logging_config.py`
```python
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
```

**產出物**:
- ✅ `app/utils/logging_config.py`

### 🧪 Phase 1 驗收標準
- [ ] FastAPI 應用成功啟動
- [ ] 能夠連接到 MongoDB
- [ ] `/health` 端點返回正常
- [ ] Swagger UI 文檔可訪問
- [ ] 專案結構清晰完整

---

## Phase 2: 認證與用戶管理 (Week 2)

### 🎯 目標
實現用戶註冊、登入、JWT 認證、用戶資訊管理

### 📝 任務清單

#### 2.1 安全工具函數 (Day 1)

**建立檔案**: `app/utils/security.py`
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

#### 2.2 用戶資料模型 (Day 1-2)

**建立檔案**: `app/models/user.py`
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Address(BaseModel):
    label: str = Field(..., example="家")
    recipient: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    postal_code: str
    is_default: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class UserInDB(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str]
    role: str
    addresses: List[Address] = []
    is_active: bool
    created_at: datetime
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str]
    role: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

#### 2.3 用戶服務層 (Day 2-3)

**建立檔案**: `app/services/user_service.py`
```python
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import Optional
from app.models.user import UserCreate, UserInDB
from app.utils.security import hash_password
from app.middleware.error_handler import APIException

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]
    
    async def create_user(self, user_data: UserCreate) -> str:
        # 檢查 email 是否已存在
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise APIException(
                code="EMAIL_EXISTS",
                message="Email already registered",
                status_code=400
            )
        
        user_dict = {
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "name": user_data.name,
            "phone": user_data.phone,
            "role": "customer",  # 預設角色
            "addresses": [],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(user_dict)
        return str(result.inserted_id)
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(user_id)})
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})
```

#### 2.4 認證 API 端點 (Day 3-4)

**建立檔案**: `app/api/deps.py`
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from app.database import get_database

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    from bson import ObjectId
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def require_role(allowed_roles: list):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    return role_checker
```

**建立檔案**: `app/api/v1/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services.user_service import UserService
from app.utils.security import verify_password, create_access_token
from app.database import get_database
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db = Depends(get_database)):
    service = UserService(db)
    user_id = await service.create_user(user_data)
    
    # 獲取完整用戶資訊
    user = await service.get_user_by_id(user_id)
    
    # 生成 Token
    access_token = create_access_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            phone=user.get("phone"),
            role=user["role"],
            is_active=user["is_active"]
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db = Depends(get_database)):
    service = UserService(db)
    user = await service.get_user_by_email(credentials.email)
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            phone=user.get("phone"),
            role=user["role"],
            is_active=user["is_active"]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        phone=current_user.get("phone"),
        role=current_user["role"],
        is_active=current_user["is_active"]
    )
```

**更新**: `app/main.py` (註冊路由)
```python
from app.api.v1 import auth

app.include_router(auth.router, prefix="/api/v1")
```

### 🧪 Phase 2 驗收標準
- [ ] 用戶可以成功註冊
- [ ] 用戶可以使用 email 和密碼登入
- [ ] 登入後獲得 JWT Token
- [ ] 使用 Token 可以訪問 `/api/v1/auth/me`
- [ ] 密碼已加密儲存在資料庫
- [ ] 重複 email 註冊會返回錯誤

---

## Phase 3: 商品管理 (Week 3)

### 🎯 目標
實現商品的 CRUD 操作、搜尋、分類、庫存管理

### 📝 任務清單

#### 3.1 商品資料模型 (Day 1)

**建立檔案**: `app/models/product.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    tags: List[str] = []
    images: List[str] = []
    status: str = "active"  # active, inactive, out_of_stock

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str
    tags: List[str]
    images: List[str]
    status: str
    created_at: datetime
    updated_at: datetime

class ProductListFilter(BaseModel):
    category: Optional[str] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    status: Optional[str] = None
```

#### 3.2 商品服務層 (Day 1-2)
**建立檔案**: `app/services/product_service.py` (參考技術架構文件)

#### 3.3 商品 API 端點 (Day 2-3)
**建立檔案**: `app/api/v1/products.py`
- `GET /api/v1/products` - 列表（分頁、篩選、搜尋）
- `GET /api/v1/products/{id}` - 詳情
- `POST /api/v1/products` - 新增（管理員）
- `PUT /api/v1/products/{id}` - 更新（管理員）
- `DELETE /api/v1/products/{id}` - 刪除（管理員）

#### 3.4 建立索引 (Day 3)
**建立檔案**: `scripts/create_indexes.py`

### 🧪 Phase 3 驗收標準
- [ ] 管理員可以新增、編輯、刪除商品
- [ ] 所有用戶可以瀏覽商品列表
- [ ] 支援商品搜尋（名稱、描述）
- [ ] 支援商品篩選（分類、價格區間）
- [ ] 支援分頁查詢
- [ ] 商品列表查詢效能良好（< 200ms）

---

## Phase 4: 訂單管理 (Week 4)

### 🎯 目標
實現訂單建立、查詢、狀態管理，含事務處理

### 📝 任務清單

#### 4.1 訂單資料模型 (Day 1)
**建立檔案**: `app/models/order.py`

#### 4.2 訂單服務層 (Day 1-3)
**建立檔案**: `app/services/order_service.py`
- 訂單建立（事務處理）
- 庫存檢查與扣減
- 訂單狀態更新
- 訂單查詢

#### 4.3 訂單 API 端點 (Day 3-4)
**建立檔案**: `app/api/v1/orders.py`
- `POST /api/v1/orders` - 建立訂單
- `GET /api/v1/orders` - 我的訂單列表
- `GET /api/v1/orders/{id}` - 訂單詳情
- `PUT /api/v1/orders/{id}/status` - 更新訂單狀態（管理員）
- `DELETE /api/v1/orders/{id}` - 取消訂單

#### 4.4 MongoDB 複製集設定 (Day 4-5)
為了支援事務，需要設定 MongoDB 複製集（本地開發環境）

### 🧪 Phase 4 驗收標準
- [ ] 用戶可以成功下訂單
- [ ] 訂單建立時自動扣減庫存
- [ ] 庫存不足時無法下訂單
- [ ] 訂單狀態流程正確
- [ ] 管理員可以更新訂單狀態
- [ ] 事務處理正確（原子性）

---

## Phase 5: 數據統計與分析 (Week 5)

### 🎯 目標
實現銷售統計、商品分析、用戶分析

### 📝 任務清單

#### 5.1 分析服務層 (Day 1-3)
**建立檔案**: `app/services/analytics_service.py`
- 銷售總覽
- 銷售趨勢
- 最暢銷商品
- 最佳客戶

#### 5.2 分析 API 端點 (Day 3-4)
**建立檔案**: `app/api/v1/analytics.py`

#### 5.3 聚合管道優化 (Day 4-5)

### 🧪 Phase 5 驗收標準
- [ ] 可以查詢指定期間的銷售總額
- [ ] 可以查看最暢銷商品 Top 10
- [ ] 可以查看最佳客戶排行
- [ ] 聚合查詢效能良好

---

## Phase 6: 測試與優化 (Week 6)

### 🎯 目標
單元測試、整合測試、效能優化

### 📝 任務清單

#### 6.1 單元測試 (Day 1-3)
- 測試所有 Service 層函數
- 測試工具函數

#### 6.2 整合測試 (Day 3-4)
- 測試所有 API 端點
- 測試認證流程
- 測試事務處理

#### 6.3 效能優化 (Day 4-5)
- 查詢效能分析
- 索引優化
- 程式碼優化

### 🧪 Phase 6 驗收標準
- [ ] 測試覆蓋率 > 70%
- [ ] 所有測試通過
- [ ] API 回應時間 < 500ms

---

## Phase 7: 部署與文檔 (Week 7)

### 🎯 目標
Docker 容器化、API 文檔、部署指南

### 📝 任務清單

#### 7.1 Docker 容器化 (Day 1-2)
- 撰寫 Dockerfile
- 撰寫 docker-compose.yml
- 測試容器化部署

#### 7.2 API 文檔完善 (Day 3-4)
- Swagger UI 描述完整
- 撰寫 API 使用文檔
- 撰寫部署指南

#### 7.3 生產環境準備 (Day 4-5)
- 環境變數管理
- 安全性檢查
- 日誌配置

### 🧪 Phase 7 驗收標準
- [ ] Docker 容器成功運行
- [ ] API 文檔完整
- [ ] 部署指南清晰

---

## Phase 8: 進階功能 (Week 8+) [可選]

### 可選功能清單
- [ ] 購物車功能
- [ ] 優惠券系統
- [ ] 商品評論與評分
- [ ] 圖片上傳功能
- [ ] Email 通知
- [ ] 訂單追蹤
- [ ] 前端界面（React/Vue）
- [ ] Redis 快取
- [ ] 支付整合

---

## 📊 進度追蹤

### 當前狀態
- ✅ Phase 0: 環境準備 (已完成)
- ⏳ Phase 1: 專案初始化 (進行中)
- ⬜ Phase 2: 認證與用戶管理
- ⬜ Phase 3: 商品管理
- ⬜ Phase 4: 訂單管理
- ⬜ Phase 5: 數據統計
- ⬜ Phase 6: 測試與優化
- ⬜ Phase 7: 部署與文檔

### 下一步行動
🎯 **立即開始 Phase 1**
1. 建立專案目錄結構
2. 安裝依賴套件
3. 建立 FastAPI 應用
4. 測試 MongoDB 連線

---

## 📚 學習資源

### 官方文檔
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Pydantic 文檔](https://docs.pydantic.dev/)

### 參考教程
- FastAPI 完整教程
- MongoDB 聚合管道教程
- JWT 認證最佳實踐

---

**文件版本**: 1.0  
**最後更新**: 2025-10-22  
**專案負責人**: Development Team

**備註**: 本路線圖為參考指南，實際開發可根據進度調整。建議採用敏捷開發方式，每週檢視進度並調整計劃。

