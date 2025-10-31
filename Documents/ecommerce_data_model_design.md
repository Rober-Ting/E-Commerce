# 電商訂單管理系統 - 資料模型設計

## 📋 文件概述

本文件詳細定義電商訂單管理系統的 MongoDB 資料模型設計，包括集合結構、欄位定義、索引策略、關聯設計和 Schema Validation。

---

## 🗂️ 資料庫設計概覽

### 資料庫名稱
`ecommerce_db`

### 集合列表
1. **users** - 用戶資訊
2. **products** - 商品資訊
3. **orders** - 訂單資訊
4. **categories** - 商品分類（可選）
5. **sessions** - 用戶會話（可選）

### 關聯策略
- **用戶 ↔ 訂單**: 引用關聯 (Referencing)
- **訂單 ↔ 商品**: 內嵌部分資訊 + 引用 (Hybrid)
- **商品 ↔ 分類**: 引用關聯 (Referencing)

---

## 1️⃣ Users Collection (用戶集合)

### 設計考量
- 用戶基本資訊集中管理
- 支援多個收貨地址（內嵌文件）
- 角色權限管理
- 密碼安全儲存

### Collection Schema

```javascript
{
  _id: ObjectId,                    // MongoDB 自動生成的唯一 ID
  email: String,                    // 用戶 Email（唯一，索引）
  password_hash: String,            // 加密後的密碼（bcrypt）
  name: String,                     // 用戶姓名
  phone: String,                    // 聯絡電話
  role: String,                     // 角色: "admin", "customer", "vendor"
  
  // 內嵌文件：收貨地址列表
  addresses: [
    {
      label: String,                // 地址標籤（如：家、公司）
      recipient: String,            // 收件人姓名
      phone: String,                // 收件人電話
      address_line1: String,        // 地址第一行
      address_line2: String,        // 地址第二行（可選）
      city: String,                 // 城市
      postal_code: String,          // 郵遞區號
      is_default: Boolean           // 是否為預設地址
    }
  ],
  
  // 元數據
  is_active: Boolean,               // 帳號是否啟用
  created_at: ISODate,              // 建立時間
  updated_at: ISODate,              // 最後更新時間
  last_login_at: ISODate            // 最後登入時間（可選）
}
```

### 範例文件

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "email": "alice@example.com",
  "password_hash": "$2b$12$KIXxLVKZ5waLN1Jz...",
  "name": "Alice Wang",
  "phone": "+886912345678",
  "role": "customer",
  "addresses": [
    {
      "label": "家",
      "recipient": "Alice Wang",
      "phone": "+886912345678",
      "address_line1": "台北市信義區信義路五段 7 號",
      "address_line2": "10 樓 A 室",
      "city": "台北市",
      "postal_code": "110",
      "is_default": true
    },
    {
      "label": "公司",
      "recipient": "Alice Wang",
      "phone": "+886912345678",
      "address_line1": "台北市中正區羅斯福路四段 1 號",
      "address_line2": null,
      "city": "台北市",
      "postal_code": "100",
      "is_default": false
    }
  ],
  "is_active": true,
  "created_at": ISODate("2025-01-15T08:30:00Z"),
  "updated_at": ISODate("2025-10-20T12:45:00Z"),
  "last_login_at": ISODate("2025-10-22T09:15:00Z")
}
```

### 索引設計

```javascript
// 唯一索引：確保 Email 唯一性
db.users.createIndex({ "email": 1 }, { unique: true })

// 單欄位索引：角色查詢
db.users.createIndex({ "role": 1 })

// 單欄位索引：帳號狀態
db.users.createIndex({ "is_active": 1 })

// 複合索引：角色 + 狀態
db.users.createIndex({ "role": 1, "is_active": 1 })
```

### Schema Validation

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "password_hash", "name", "role", "is_active"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "必須是有效的 Email 格式"
        },
        password_hash: {
          bsonType: "string",
          minLength: 50,
          description: "必須是加密後的密碼"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 50,
          description: "姓名長度必須在 2-50 字元之間"
        },
        role: {
          enum: ["admin", "customer", "vendor"],
          description: "必須是預定義的角色之一"
        },
        is_active: {
          bsonType: "bool"
        }
      }
    }
  }
})
```

### Pydantic 模型 (Python)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

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

class UserInDB(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str]
    role: str
    addresses: List[Address] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

---

## 2️⃣ Products Collection (商品集合)

### 設計考量
- 支援多圖片
- 標籤系統（陣列）
- 庫存即時管理
- 軟刪除機制

### Collection Schema

```javascript
{
  _id: ObjectId,                    // MongoDB 自動生成的唯一 ID
  name: String,                     // 商品名稱（索引）
  description: String,              // 商品描述
  price: Decimal128,                // 商品價格（使用 Decimal128 避免浮點誤差）
  stock: Number,                    // 庫存數量
  category: String,                 // 商品分類（索引）
  tags: [String],                   // 標籤陣列
  images: [String],                 // 圖片 URL 陣列
  
  // 商品屬性（可選，彈性設計）
  attributes: {
    color: String,
    size: String,
    weight: String,
    brand: String
    // ... 其他屬性
  },
  
  // 商品狀態
  status: String,                   // "active", "inactive", "out_of_stock"
  
  // SEO（可選）
  slug: String,                     // URL 友善的商品標識
  meta_title: String,
  meta_description: String,
  
  // 統計資料（可選）
  views: Number,                    // 瀏覽次數
  sales_count: Number,              // 銷售數量
  rating: Number,                   // 平均評分
  
  // 元數據
  is_deleted: Boolean,              // 軟刪除標記
  created_at: ISODate,
  updated_at: ISODate,
  created_by: ObjectId              // 建立者 User ID（可選）
}
```

### 範例文件

```json
{
  "_id": ObjectId("507f191e810c19729de860ea"),
  "name": "MacBook Pro 14 吋 M3",
  "description": "全新 Apple M3 晶片，14 吋 Liquid Retina XDR 顯示器，16GB 記憶體，512GB SSD 儲存空間。",
  "price": NumberDecimal("59900.00"),
  "stock": 15,
  "category": "筆記型電腦",
  "tags": ["Apple", "MacBook", "M3", "筆電", "專業"],
  "images": [
    "https://example.com/images/macbook-pro-14-m3-1.jpg",
    "https://example.com/images/macbook-pro-14-m3-2.jpg",
    "https://example.com/images/macbook-pro-14-m3-3.jpg"
  ],
  "attributes": {
    "color": "太空灰",
    "screen_size": "14 吋",
    "processor": "Apple M3",
    "ram": "16GB",
    "storage": "512GB SSD",
    "brand": "Apple",
    "weight": "1.55 kg"
  },
  "status": "active",
  "slug": "macbook-pro-14-m3-space-gray",
  "meta_title": "MacBook Pro 14 吋 M3 - 專業筆記型電腦",
  "meta_description": "全新 Apple M3 晶片效能強大，適合專業創作者使用。",
  "views": 1250,
  "sales_count": 48,
  "rating": 4.8,
  "is_deleted": false,
  "created_at": ISODate("2025-01-10T10:00:00Z"),
  "updated_at": ISODate("2025-10-22T15:30:00Z"),
  "created_by": ObjectId("507f1f77bcf86cd799439011")
}
```

### 索引設計

```javascript
// 單欄位索引：商品名稱
db.products.createIndex({ "name": 1 })

// 單欄位索引：分類
db.products.createIndex({ "category": 1 })

// 單欄位索引：狀態
db.products.createIndex({ "status": 1 })

// 單欄位索引：標籤
db.products.createIndex({ "tags": 1 })

// 單欄位索引：價格（範圍查詢）
db.products.createIndex({ "price": 1 })

// 文字索引：支援全文搜尋
db.products.createIndex(
  { "name": "text", "description": "text", "tags": "text" },
  { default_language: "chinese" }
)

// 複合索引：分類 + 狀態 + 價格
db.products.createIndex({ "category": 1, "status": 1, "price": 1 })

// 複合索引：軟刪除 + 狀態（常用查詢）
db.products.createIndex({ "is_deleted": 1, "status": 1 })

// 唯一索引：URL slug
db.products.createIndex({ "slug": 1 }, { unique: true, sparse: true })
```

### Schema Validation

```javascript
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "stock", "status", "is_deleted"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 200,
          description: "商品名稱必須為 1-200 字元"
        },
        price: {
          bsonType: ["decimal", "double"],
          minimum: 0,
          description: "價格必須大於等於 0"
        },
        stock: {
          bsonType: "int",
          minimum: 0,
          description: "庫存必須大於等於 0"
        },
        status: {
          enum: ["active", "inactive", "out_of_stock"],
          description: "必須是預定義的狀態之一"
        },
        is_deleted: {
          bsonType: "bool"
        }
      }
    }
  }
})
```

### Pydantic 模型 (Python)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
    attributes: Dict[str, Any] = {}
    status: str = "active"

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
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
```

---

## 3️⃣ Orders Collection (訂單集合)

### 設計考量
- **混合設計**: 內嵌訂單商品明細（快照） + 引用用戶 ID
- 訂單狀態歷史記錄（內嵌陣列）
- 訂單編號唯一性
- 支援事務處理

### Collection Schema

```javascript
{
  _id: ObjectId,                    // MongoDB 自動生成的唯一 ID
  order_number: String,             // 訂單編號（唯一，索引）
  user_id: ObjectId,                // 用戶 ID（引用 users 集合，索引）
  
  // 內嵌文件：訂單商品明細（快照設計）
  items: [
    {
      product_id: ObjectId,         // 商品 ID（引用 products 集合）
      product_name: String,         // 商品名稱（快照）
      product_image: String,        // 商品圖片（快照）
      quantity: Number,             // 購買數量
      price: Decimal128,            // 購買時的價格（快照）
      subtotal: Decimal128          // 小計 (quantity * price)
    }
  ],
  
  // 訂單金額
  subtotal: Decimal128,             // 商品小計
  shipping_fee: Decimal128,         // 運費
  discount: Decimal128,             // 折扣金額
  total_amount: Decimal128,         // 訂單總金額
  
  // 收貨地址（快照）
  shipping_address: {
    recipient: String,
    phone: String,
    address_line1: String,
    address_line2: String,
    city: String,
    postal_code: String
  },
  
  // 訂單狀態
  status: String,                   // "pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "returned"
  
  // 狀態歷史記錄
  status_history: [
    {
      status: String,
      timestamp: ISODate,
      note: String,
      updated_by: ObjectId          // 操作者 User ID
    }
  ],
  
  // 支付資訊（可選）
  payment: {
    method: String,                 // "credit_card", "debit_card", "paypal", "cash_on_delivery"
    status: String,                 // "pending", "paid", "failed", "refunded"
    transaction_id: String,
    paid_at: ISODate
  },
  
  // 物流資訊（可選）
  shipping: {
    tracking_number: String,
    carrier: String,
    shipped_at: ISODate,
    estimated_delivery: ISODate,
    delivered_at: ISODate
  },
  
  // 備註
  notes: String,                    // 訂單備註
  customer_notes: String,           // 客戶備註
  
  // 元數據
  created_at: ISODate,              // 訂單建立時間（索引）
  updated_at: ISODate               // 最後更新時間
}
```

### 範例文件

```json
{
  "_id": ObjectId("6540a1b2c3d4e5f678901234"),
  "order_number": "ORD20251022143055123456",
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "items": [
    {
      "product_id": ObjectId("507f191e810c19729de860ea"),
      "product_name": "MacBook Pro 14 吋 M3",
      "product_image": "https://example.com/images/macbook-pro-14-m3-1.jpg",
      "quantity": 1,
      "price": NumberDecimal("59900.00"),
      "subtotal": NumberDecimal("59900.00")
    },
    {
      "product_id": ObjectId("507f191e810c19729de860eb"),
      "product_name": "Magic Mouse",
      "product_image": "https://example.com/images/magic-mouse.jpg",
      "quantity": 2,
      "price": NumberDecimal("2390.00"),
      "subtotal": NumberDecimal("4780.00")
    }
  ],
  "subtotal": NumberDecimal("64680.00"),
  "shipping_fee": NumberDecimal("100.00"),
  "discount": NumberDecimal("0.00"),
  "total_amount": NumberDecimal("64780.00"),
  "shipping_address": {
    "recipient": "Alice Wang",
    "phone": "+886912345678",
    "address_line1": "台北市信義區信義路五段 7 號",
    "address_line2": "10 樓 A 室",
    "city": "台北市",
    "postal_code": "110"
  },
  "status": "confirmed",
  "status_history": [
    {
      "status": "pending",
      "timestamp": ISODate("2025-10-22T14:30:55Z"),
      "note": "訂單已建立",
      "updated_by": ObjectId("507f1f77bcf86cd799439011")
    },
    {
      "status": "confirmed",
      "timestamp": ISODate("2025-10-22T14:35:20Z"),
      "note": "訂單已確認",
      "updated_by": ObjectId("507f1f77bcf86cd799439012")
    }
  ],
  "payment": {
    "method": "credit_card",
    "status": "paid",
    "transaction_id": "TXN20251022143120",
    "paid_at": ISODate("2025-10-22T14:31:20Z")
  },
  "shipping": {
    "tracking_number": null,
    "carrier": null,
    "shipped_at": null,
    "estimated_delivery": ISODate("2025-10-25T12:00:00Z"),
    "delivered_at": null
  },
  "notes": "",
  "customer_notes": "請在工作日 9:00-18:00 送達",
  "created_at": ISODate("2025-10-22T14:30:55Z"),
  "updated_at": ISODate("2025-10-22T14:35:20Z")
}
```

### 索引設計

```javascript
// 唯一索引：訂單編號
db.orders.createIndex({ "order_number": 1 }, { unique: true })

// 單欄位索引：用戶 ID（查詢用戶訂單）
db.orders.createIndex({ "user_id": 1 })

// 單欄位索引：訂單狀態
db.orders.createIndex({ "status": 1 })

// 單欄位索引：建立時間（降序，最新訂單優先）
db.orders.createIndex({ "created_at": -1 })

// 複合索引：用戶 ID + 建立時間（用戶訂單歷史）
db.orders.createIndex({ "user_id": 1, "created_at": -1 })

// 複合索引：狀態 + 建立時間（管理員訂單列表）
db.orders.createIndex({ "status": 1, "created_at": -1 })

// 單欄位索引：商品 ID（查詢商品銷售記錄）
db.orders.createIndex({ "items.product_id": 1 })

// 複合索引：支付狀態 + 訂單狀態
db.orders.createIndex({ "payment.status": 1, "status": 1 })
```

### Schema Validation

```javascript
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["order_number", "user_id", "items", "total_amount", "status"],
      properties: {
        order_number: {
          bsonType: "string",
          pattern: "^ORD[0-9]{20}$",
          description: "訂單編號格式必須為 ORD + 20 位數字"
        },
        user_id: {
          bsonType: "objectId"
        },
        items: {
          bsonType: "array",
          minItems: 1,
          description: "訂單必須至少包含一個商品"
        },
        total_amount: {
          bsonType: ["decimal", "double"],
          minimum: 0
        },
        status: {
          enum: ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "returned"],
          description: "必須是預定義的訂單狀態之一"
        }
      }
    }
  }
})
```

### Pydantic 模型 (Python)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from bson import ObjectId

class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItem] = Field(..., min_items=1)
    shipping_address_index: int = 0  # 用戶地址列表的索引
    customer_notes: Optional[str] = None

class OrderItemDetail(BaseModel):
    product_id: str
    product_name: str
    product_image: str
    quantity: int
    price: float
    subtotal: float

class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: str
    items: List[OrderItemDetail]
    total_amount: float
    status: str
    shipping_address: dict
    created_at: datetime
```

---

## 4️⃣ Categories Collection (商品分類集合) [可選]

### 設計考量
- 支援多層級分類（父子關係）
- 分類排序

### Collection Schema

```javascript
{
  _id: ObjectId,
  name: String,                     // 分類名稱（索引）
  slug: String,                     // URL 友善標識（唯一）
  description: String,
  parent_id: ObjectId,              // 父分類 ID（null 表示頂層分類）
  level: Number,                    // 分類層級（0 = 頂層）
  sort_order: Number,               // 排序順序
  is_active: Boolean,
  created_at: ISODate,
  updated_at: ISODate
}
```

### 範例文件

```json
{
  "_id": ObjectId("6540a1b2c3d4e5f678901235"),
  "name": "電腦周邊",
  "slug": "computer-accessories",
  "description": "各類電腦周邊產品",
  "parent_id": null,
  "level": 0,
  "sort_order": 1,
  "is_active": true,
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z")
}
```

### 索引設計

```javascript
db.categories.createIndex({ "name": 1 })
db.categories.createIndex({ "slug": 1 }, { unique: true })
db.categories.createIndex({ "parent_id": 1 })
db.categories.createIndex({ "level": 1, "sort_order": 1 })
```

---

## 📊 關聯設計總結

### 1. 用戶與訂單 (One-to-Many)
- **策略**: 引用關聯 (Referencing)
- **原因**: 訂單數量會持續增長，不適合內嵌
- **實作**: `orders.user_id` 引用 `users._id`

### 2. 訂單與商品 (Many-to-Many)
- **策略**: 混合設計（Hybrid）
- **原因**: 
  - 需要保存購買時的商品資訊快照（價格、名稱）
  - 避免商品資訊更新後影響歷史訂單
- **實作**: 
  - `orders.items.product_id` 引用 `products._id`
  - 同時內嵌商品快照資訊

### 3. 用戶地址
- **策略**: 內嵌文件 (Embedded Documents)
- **原因**: 
  - 用戶地址數量有限（通常 < 10 個）
  - 查詢用戶時經常需要地址資訊
  - 地址變更不頻繁
- **實作**: `users.addresses` 陣列

---

## 🔐 資料安全與驗證

### 密碼安全
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密密碼
hashed_password = pwd_context.hash("user_password")

# 驗證密碼
is_valid = pwd_context.verify("user_password", hashed_password)
```

### 敏感資料處理
- **密碼**: 使用 bcrypt 加密，cost factor = 12
- **支付資訊**: 不儲存完整信用卡號
- **個資**: 符合 GDPR 要求（刪除用戶時完全移除資料）

---

## 📈 效能優化策略

### 1. 索引優化
- 根據查詢頻率建立索引
- 避免過多索引（影響寫入效能）
- 使用 `explain()` 分析查詢效能

### 2. 投影 (Projection)
```javascript
// 只獲取需要的欄位
db.users.find(
  { email: "alice@example.com" },
  { name: 1, email: 1, role: 1, _id: 0 }
)
```

### 3. 分頁查詢
```javascript
// 使用 skip 和 limit
db.products.find({ status: "active" })
  .skip(20)
  .limit(20)
  .sort({ created_at: -1 })
```

### 4. 聚合管道優化
- `$match` 階段儘早執行（過濾資料）
- 使用 `$project` 減少資料傳輸
- 避免 `$lookup` 的過度使用

---

## 🔄 資料遷移與版本管理

### 版本號管理（可選）
```javascript
{
  _id: ObjectId,
  // ... 其他欄位
  schema_version: 1  // 資料模型版本
}
```

### 遷移策略
- **漸進式遷移**: 新舊版本並存
- **懶遷移**: 資料讀取時轉換
- **批量遷移**: 使用腳本批量更新

---

## 📝 資料初始化腳本

### 建立索引腳本

```python
# scripts/create_indexes.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def create_indexes():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["ecommerce_db"]
    
    # Users Collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    await db.users.create_index([("role", 1), ("is_active", 1)])
    
    # Products Collection
    await db.products.create_index("name")
    await db.products.create_index("category")
    await db.products.create_index("status")
    await db.products.create_index([("name", "text"), ("description", "text")])
    await db.products.create_index([("is_deleted", 1), ("status", 1)])
    
    # Orders Collection
    await db.orders.create_index("order_number", unique=True)
    await db.orders.create_index("user_id")
    await db.orders.create_index("status")
    await db.orders.create_index([("user_id", 1), ("created_at", -1)])
    await db.orders.create_index([("status", 1), ("created_at", -1)])
    
    print("All indexes created successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())
```

### 測試資料生成腳本

```python
# scripts/seed_data.py
# 生成測試用戶、商品、訂單
# (詳細程式碼見開發階段實作)
```

---

## 總結

本資料模型設計提供了：

✅ **清晰的結構**: 每個集合職責明確  
✅ **彈性擴展**: 使用 MongoDB 彈性 Schema  
✅ **效能優化**: 合理的索引與查詢策略  
✅ **資料完整性**: Schema Validation 確保資料品質  
✅ **安全設計**: 密碼加密、敏感資料保護  

**文件版本**: 1.0  
**最後更新**: 2025-10-22

