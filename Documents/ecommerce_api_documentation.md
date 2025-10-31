# 電商訂單管理系統 - API 設計文檔

## 📋 文件概述

本文件詳細定義電商訂單管理系統的 RESTful API 規範，包括所有端點、請求/回應格式、認證機制、錯誤處理等。

---

## 🌐 API 基礎資訊

### Base URL
```
Development: http://localhost:8000
Production: https://api.ecommerce.example.com
```

### API 版本
```
Current Version: v1
Prefix: /api/v1
```

### 認證機制
- **類型**: JWT (JSON Web Token)
- **Header**: `Authorization: Bearer <token>`
- **Token 有效期**: 60 分鐘
- **Refresh Token**: 7 天（可選）

### 通用 HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 請求成功 |
| 201 | 資源建立成功 |
| 204 | 請求成功，無返回內容 |
| 400 | 請求參數錯誤 |
| 401 | 未認證或 Token 無效 |
| 403 | 權限不足 |
| 404 | 資源不存在 |
| 409 | 資源衝突（如 Email 已存在）|
| 422 | 資料驗證失敗 |
| 500 | 伺服器內部錯誤 |

---

## 📐 回應格式標準

### 成功回應

```json
{
  "success": true,
  "data": {
    // 實際資料
  },
  "message": "Operation successful"
}
```

### 錯誤回應

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // 額外錯誤細節（可選）
    }
  }
}
```

### 分頁回應

```json
{
  "success": true,
  "data": {
    "items": [
      // 資料陣列
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## 🔐 1. 認證 API (Authentication)

### 1.1 用戶註冊

**端點**: `POST /api/v1/auth/register`

**說明**: 註冊新用戶帳號

**請求標頭**: 無需認證

**請求體**:
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123!",
  "name": "Alice Wang",
  "phone": "+886912345678"
}
```

**回應** (201 Created):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "email": "alice@example.com",
      "name": "Alice Wang",
      "phone": "+886912345678",
      "role": "customer",
      "is_active": true
    }
  },
  "message": "User registered successfully"
}
```

**錯誤回應** (400):
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered"
  }
}
```

**驗證規則**:
- Email: 必須是有效的 Email 格式
- Password: 最少 8 字元
- Name: 2-50 字元
- Phone: 可選

---

### 1.2 用戶登入

**端點**: `POST /api/v1/auth/login`

**說明**: 用戶登入並獲取 JWT Token

**請求標頭**: 無需認證

**請求體**:
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123!"
}
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "email": "alice@example.com",
      "name": "Alice Wang",
      "phone": "+886912345678",
      "role": "customer",
      "is_active": true
    }
  },
  "message": "Login successful"
}
```

**錯誤回應** (401):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect email or password"
  }
}
```

---

### 1.3 獲取當前用戶資訊

**端點**: `GET /api/v1/auth/me`

**說明**: 獲取當前登入用戶的詳細資訊

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "email": "alice@example.com",
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
      }
    ],
    "is_active": true,
    "created_at": "2025-01-15T08:30:00Z"
  }
}
```

**錯誤回應** (401):
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

---

### 1.4 登出

**端點**: `POST /api/v1/auth/logout`

**說明**: 用戶登出（前端刪除 Token，後端可選實作黑名單）

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## 👤 2. 用戶管理 API (Users)

### 2.1 獲取用戶列表

**端點**: `GET /api/v1/users`

**說明**: 獲取所有用戶列表（僅管理員）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `page` (int, optional): 頁碼，預設 1
- `per_page` (int, optional): 每頁數量，預設 20，最大 100
- `role` (string, optional): 角色篩選 (admin, customer, vendor)
- `is_active` (boolean, optional): 帳號狀態篩選
- `search` (string, optional): 搜尋關鍵字（名稱或 Email）

**範例**: `GET /api/v1/users?page=1&per_page=20&role=customer`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "507f1f77bcf86cd799439011",
        "email": "alice@example.com",
        "name": "Alice Wang",
        "phone": "+886912345678",
        "role": "customer",
        "is_active": true,
        "created_at": "2025-01-15T08:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 2.2 獲取用戶詳情

**端點**: `GET /api/v1/users/{user_id}`

**說明**: 獲取指定用戶的詳細資訊

**權限**: `admin` 或自己

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "email": "alice@example.com",
    "name": "Alice Wang",
    "phone": "+886912345678",
    "role": "customer",
    "addresses": [...],
    "is_active": true,
    "created_at": "2025-01-15T08:30:00Z",
    "updated_at": "2025-10-20T12:45:00Z"
  }
}
```

**錯誤回應** (404):
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found"
  }
}
```

---

### 2.3 更新用戶資訊

**端點**: `PUT /api/v1/users/{user_id}`

**說明**: 更新用戶資訊

**權限**: `admin` 或自己

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體**:
```json
{
  "name": "Alice Wang Updated",
  "phone": "+886987654321"
}
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "email": "alice@example.com",
    "name": "Alice Wang Updated",
    "phone": "+886987654321",
    "role": "customer",
    "is_active": true
  },
  "message": "User updated successfully"
}
```

---

### 2.4 新增用戶地址

**端點**: `POST /api/v1/users/{user_id}/addresses`

**說明**: 為用戶新增收貨地址

**權限**: `admin` 或自己

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體**:
```json
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
```

**回應** (201 Created):
```json
{
  "success": true,
  "message": "Address added successfully"
}
```

---

### 2.5 刪除用戶（軟刪除）

**端點**: `DELETE /api/v1/users/{user_id}`

**說明**: 停用用戶帳號（軟刪除）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 🛍️ 3. 商品管理 API (Products)

### 3.1 獲取商品列表

**端點**: `GET /api/v1/products`

**說明**: 獲取商品列表（支援搜尋、篩選、排序、分頁）

**請求標頭**: 無需認證（公開）

**查詢參數**:
- `page` (int, optional): 頁碼，預設 1
- `per_page` (int, optional): 每頁數量，預設 20
- `category` (string, optional): 分類篩選
- `search` (string, optional): 搜尋關鍵字（名稱、描述）
- `min_price` (float, optional): 最低價格
- `max_price` (float, optional): 最高價格
- `status` (string, optional): 狀態篩選 (active, inactive, out_of_stock)
- `sort_by` (string, optional): 排序欄位 (price, created_at, name)
- `order` (string, optional): 排序方向 (asc, desc)，預設 desc

**範例**: `GET /api/v1/products?category=筆記型電腦&min_price=20000&max_price=80000&sort_by=price&order=asc`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "507f191e810c19729de860ea",
        "name": "MacBook Pro 14 吋 M3",
        "description": "全新 Apple M3 晶片...",
        "price": 59900.00,
        "stock": 15,
        "category": "筆記型電腦",
        "tags": ["Apple", "MacBook", "M3"],
        "images": [
          "https://example.com/images/macbook-pro-14-m3-1.jpg"
        ],
        "status": "active",
        "created_at": "2025-01-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 3.2 獲取商品詳情

**端點**: `GET /api/v1/products/{product_id}`

**說明**: 獲取指定商品的詳細資訊

**請求標頭**: 無需認證（公開）

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "507f191e810c19729de860ea",
    "name": "MacBook Pro 14 吋 M3",
    "description": "全新 Apple M3 晶片，14 吋 Liquid Retina XDR 顯示器，16GB 記憶體，512GB SSD 儲存空間。",
    "price": 59900.00,
    "stock": 15,
    "category": "筆記型電腦",
    "tags": ["Apple", "MacBook", "M3", "筆電"],
    "images": [
      "https://example.com/images/macbook-pro-14-m3-1.jpg",
      "https://example.com/images/macbook-pro-14-m3-2.jpg"
    ],
    "attributes": {
      "color": "太空灰",
      "screen_size": "14 吋",
      "processor": "Apple M3",
      "ram": "16GB",
      "storage": "512GB SSD"
    },
    "status": "active",
    "views": 1250,
    "sales_count": 48,
    "rating": 4.8,
    "created_at": "2025-01-10T10:00:00Z",
    "updated_at": "2025-10-22T15:30:00Z"
  }
}
```

**錯誤回應** (404):
```json
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product not found"
  }
}
```

---

### 3.3 新增商品

**端點**: `POST /api/v1/products`

**說明**: 新增商品（僅管理員）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體**:
```json
{
  "name": "iPad Pro 12.9 吋",
  "description": "全新 M2 晶片，12.9 吋 Liquid Retina XDR 顯示器",
  "price": 35900.00,
  "stock": 20,
  "category": "平板電腦",
  "tags": ["Apple", "iPad", "M2"],
  "images": [
    "https://example.com/images/ipad-pro-12.9-1.jpg"
  ],
  "attributes": {
    "color": "太空灰",
    "storage": "256GB"
  },
  "status": "active"
}
```

**回應** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "507f191e810c19729de860eb",
    "name": "iPad Pro 12.9 吋",
    "price": 35900.00,
    "stock": 20,
    "status": "active",
    "created_at": "2025-10-22T16:00:00Z"
  },
  "message": "Product created successfully"
}
```

**驗證規則**:
- name: 1-200 字元
- price: 必須 > 0
- stock: 必須 >= 0
- status: active, inactive, out_of_stock

---

### 3.4 更新商品

**端點**: `PUT /api/v1/products/{product_id}`

**說明**: 更新商品資訊（僅管理員）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體** (部分更新):
```json
{
  "price": 34900.00,
  "stock": 25
}
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "507f191e810c19729de860eb",
    "name": "iPad Pro 12.9 吋",
    "price": 34900.00,
    "stock": 25,
    "updated_at": "2025-10-22T16:30:00Z"
  },
  "message": "Product updated successfully"
}
```

---

### 3.5 刪除商品（軟刪除）

**端點**: `DELETE /api/v1/products/{product_id}`

**說明**: 刪除商品（軟刪除，僅管理員）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

---

## 📦 4. 訂單管理 API (Orders)

### 4.1 建立訂單

**端點**: `POST /api/v1/orders`

**說明**: 用戶建立新訂單

**權限**: 需認證

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體**:
```json
{
  "items": [
    {
      "product_id": "507f191e810c19729de860ea",
      "quantity": 1
    },
    {
      "product_id": "507f191e810c19729de860eb",
      "quantity": 2
    }
  ],
  "shipping_address_index": 0,
  "customer_notes": "請在工作日 9:00-18:00 送達"
}
```

**回應** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "6540a1b2c3d4e5f678901234",
    "order_number": "ORD20251022143055123456",
    "user_id": "507f1f77bcf86cd799439011",
    "items": [
      {
        "product_id": "507f191e810c19729de860ea",
        "product_name": "MacBook Pro 14 吋 M3",
        "quantity": 1,
        "price": 59900.00,
        "subtotal": 59900.00
      }
    ],
    "total_amount": 64780.00,
    "status": "pending",
    "shipping_address": {
      "recipient": "Alice Wang",
      "phone": "+886912345678",
      "address_line1": "台北市信義區信義路五段 7 號",
      "city": "台北市",
      "postal_code": "110"
    },
    "created_at": "2025-10-22T14:30:55Z"
  },
  "message": "Order created successfully"
}
```

**錯誤回應** (400):
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Insufficient stock for product: MacBook Pro 14 吋 M3",
    "details": {
      "product_id": "507f191e810c19729de860ea",
      "available_stock": 5,
      "requested_quantity": 10
    }
  }
}
```

---

### 4.2 獲取訂單列表

**端點**: `GET /api/v1/orders`

**說明**: 獲取訂單列表（用戶查看自己的訂單，管理員查看所有訂單）

**權限**: 需認證

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `page` (int, optional): 頁碼，預設 1
- `per_page` (int, optional): 每頁數量，預設 20
- `status` (string, optional): 狀態篩選
- `start_date` (date, optional): 開始日期 (YYYY-MM-DD)
- `end_date` (date, optional): 結束日期 (YYYY-MM-DD)
- `user_id` (string, optional): 用戶 ID（僅管理員）

**範例**: `GET /api/v1/orders?status=pending&page=1`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "6540a1b2c3d4e5f678901234",
        "order_number": "ORD20251022143055123456",
        "user_id": "507f1f77bcf86cd799439011",
        "total_amount": 64780.00,
        "status": "pending",
        "items_count": 2,
        "created_at": "2025-10-22T14:30:55Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

---

### 4.3 獲取訂單詳情

**端點**: `GET /api/v1/orders/{order_id}`

**說明**: 獲取指定訂單的詳細資訊

**權限**: `admin` 或訂單所有者

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "6540a1b2c3d4e5f678901234",
    "order_number": "ORD20251022143055123456",
    "user_id": "507f1f77bcf86cd799439011",
    "items": [
      {
        "product_id": "507f191e810c19729de860ea",
        "product_name": "MacBook Pro 14 吋 M3",
        "product_image": "https://example.com/images/macbook-pro-14-m3-1.jpg",
        "quantity": 1,
        "price": 59900.00,
        "subtotal": 59900.00
      }
    ],
    "subtotal": 64680.00,
    "shipping_fee": 100.00,
    "discount": 0.00,
    "total_amount": 64780.00,
    "status": "pending",
    "shipping_address": {
      "recipient": "Alice Wang",
      "phone": "+886912345678",
      "address_line1": "台北市信義區信義路五段 7 號",
      "address_line2": "10 樓 A 室",
      "city": "台北市",
      "postal_code": "110"
    },
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2025-10-22T14:30:55Z",
        "note": "訂單已建立"
      }
    ],
    "payment": {
      "method": "credit_card",
      "status": "pending"
    },
    "customer_notes": "請在工作日 9:00-18:00 送達",
    "created_at": "2025-10-22T14:30:55Z",
    "updated_at": "2025-10-22T14:30:55Z"
  }
}
```

---

### 4.4 更新訂單狀態

**端點**: `PATCH /api/v1/orders/{order_id}/status`

**說明**: 更新訂單狀態（僅管理員）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**請求體**:
```json
{
  "status": "confirmed",
  "note": "訂單已確認，準備出貨"
}
```

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "6540a1b2c3d4e5f678901234",
    "status": "confirmed",
    "updated_at": "2025-10-22T15:00:00Z"
  },
  "message": "Order status updated successfully"
}
```

**有效狀態流程**:
```
pending → confirmed → processing → shipped → delivered
         ↓
      cancelled
         ↓
      returned (from delivered)
```

---

### 4.5 取消訂單

**端點**: `DELETE /api/v1/orders/{order_id}`

**說明**: 取消訂單（僅 pending 狀態可取消）

**權限**: `admin` 或訂單所有者

**請求標頭**: 
```
Authorization: Bearer <token>
```

**回應** (200 OK):
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

**錯誤回應** (400):
```json
{
  "success": false,
  "error": {
    "code": "CANNOT_CANCEL_ORDER",
    "message": "Order cannot be cancelled in current status",
    "details": {
      "current_status": "shipped"
    }
  }
}
```

---

## 📊 5. 數據分析 API (Analytics)

### 5.1 銷售總覽

**端點**: `GET /api/v1/analytics/sales/summary`

**說明**: 獲取銷售總覽統計

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `start_date` (date, required): 開始日期 (YYYY-MM-DD)
- `end_date` (date, required): 結束日期 (YYYY-MM-DD)

**範例**: `GET /api/v1/analytics/sales/summary?start_date=2025-10-01&end_date=2025-10-31`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-31"
    },
    "summary": {
      "total_orders": 450,
      "total_revenue": 15680000.00,
      "average_order_value": 34844.44,
      "completed_orders": 420,
      "cancelled_orders": 15,
      "pending_orders": 15
    }
  }
}
```

---

### 5.2 銷售趨勢

**端點**: `GET /api/v1/analytics/sales/trends`

**說明**: 獲取銷售趨勢（按日/月統計）

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `start_date` (date, required): 開始日期
- `end_date` (date, required): 結束日期
- `granularity` (string, optional): 統計粒度 (daily, weekly, monthly)，預設 daily

**範例**: `GET /api/v1/analytics/sales/trends?start_date=2025-10-01&end_date=2025-10-31&granularity=daily`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "date": "2025-10-01",
        "total_orders": 15,
        "total_revenue": 520000.00
      },
      {
        "date": "2025-10-02",
        "total_orders": 18,
        "total_revenue": 650000.00
      }
    ]
  }
}
```

---

### 5.3 最暢銷商品

**端點**: `GET /api/v1/analytics/products/top-selling`

**說明**: 獲取最暢銷商品排行

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `limit` (int, optional): 返回數量，預設 10，最大 50
- `start_date` (date, optional): 開始日期
- `end_date` (date, optional): 結束日期

**範例**: `GET /api/v1/analytics/products/top-selling?limit=10`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "product_id": "507f191e810c19729de860ea",
        "product_name": "MacBook Pro 14 吋 M3",
        "total_quantity": 48,
        "total_revenue": 2875200.00,
        "order_count": 48
      },
      {
        "product_id": "507f191e810c19729de860eb",
        "product_name": "iPad Pro 12.9 吋",
        "total_quantity": 65,
        "total_revenue": 2268500.00,
        "order_count": 62
      }
    ]
  }
}
```

---

### 5.4 最佳客戶排行

**端點**: `GET /api/v1/analytics/customers/top-buyers`

**說明**: 獲取購買次數/金額最多的客戶排行

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `limit` (int, optional): 返回數量，預設 10
- `sort_by` (string, optional): 排序依據 (order_count, total_spent)，預設 order_count

**範例**: `GET /api/v1/analytics/customers/top-buyers?limit=10&sort_by=total_spent`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "user_id": "507f1f77bcf86cd799439011",
        "user_name": "Alice Wang",
        "user_email": "alice@example.com",
        "order_count": 25,
        "total_spent": 1580000.00,
        "average_order_value": 63200.00
      }
    ]
  }
}
```

---

### 5.5 每月銷售統計

**端點**: `GET /api/v1/analytics/sales/monthly`

**說明**: 獲取每月銷售統計

**權限**: `admin`

**請求標頭**: 
```
Authorization: Bearer <token>
```

**查詢參數**:
- `year` (int, optional): 年份，預設當前年份

**範例**: `GET /api/v1/analytics/sales/monthly?year=2025`

**回應** (200 OK):
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "monthly_sales": [
      {
        "month": "2025-01",
        "total_orders": 320,
        "total_revenue": 12500000.00
      },
      {
        "month": "2025-02",
        "total_orders": 280,
        "total_revenue": 10800000.00
      }
    ]
  }
}
```

---

## 🔍 6. 商品分類 API (Categories) [可選]

### 6.1 獲取分類列表

**端點**: `GET /api/v1/categories`

**說明**: 獲取所有商品分類（樹狀結構）

**請求標頭**: 無需認證（公開）

**回應** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "6540a1b2c3d4e5f678901235",
      "name": "電腦周邊",
      "slug": "computer-accessories",
      "level": 0,
      "children": [
        {
          "id": "6540a1b2c3d4e5f678901236",
          "name": "筆記型電腦",
          "slug": "laptops",
          "level": 1,
          "children": []
        }
      ]
    }
  ]
}
```

---

## 🛡️ 錯誤代碼總覽

### 認證相關
- `EMAIL_EXISTS`: Email 已被註冊
- `INVALID_CREDENTIALS`: Email 或密碼錯誤
- `UNAUTHORIZED`: 未認證或 Token 無效
- `TOKEN_EXPIRED`: Token 已過期
- `FORBIDDEN`: 權限不足

### 用戶相關
- `USER_NOT_FOUND`: 用戶不存在
- `INVALID_USER_ID`: 用戶 ID 格式錯誤

### 商品相關
- `PRODUCT_NOT_FOUND`: 商品不存在
- `INVALID_PRODUCT_ID`: 商品 ID 格式錯誤
- `INSUFFICIENT_STOCK`: 庫存不足

### 訂單相關
- `ORDER_NOT_FOUND`: 訂單不存在
- `INVALID_ORDER_ID`: 訂單 ID 格式錯誤
- `CANNOT_CANCEL_ORDER`: 訂單無法取消（狀態不允許）
- `INVALID_ORDER_STATUS`: 無效的訂單狀態

### 通用錯誤
- `VALIDATION_ERROR`: 資料驗證失敗
- `INTERNAL_SERVER_ERROR`: 伺服器內部錯誤
- `NOT_FOUND`: 資源不存在
- `BAD_REQUEST`: 請求參數錯誤

---

## 🧪 測試範例

### 使用 cURL 測試

#### 1. 用戶註冊
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "name": "Test User",
    "phone": "+886912345678"
  }'
```

#### 2. 用戶登入
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }'
```

#### 3. 獲取商品列表
```bash
curl -X GET "http://localhost:8000/api/v1/products?page=1&per_page=10"
```

#### 4. 建立訂單（需要 Token）
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "items": [
      {"product_id": "507f191e810c19729de860ea", "quantity": 1}
    ],
    "shipping_address_index": 0
  }'
```

---

## 📝 Postman Collection

建議匯出完整的 Postman Collection，包含：
- 所有 API 端點
- 範例請求與回應
- 環境變數設定（Base URL, Token）
- 自動化測試腳本

---

## 🔄 版本更新記錄

### v1.0 (2025-10-22)
- ✅ 初始版本發布
- ✅ 完整的 CRUD 操作
- ✅ JWT 認證機制
- ✅ 訂單管理流程
- ✅ 數據分析端點

### 未來規劃 (v2.0)
- 🔜 購物車 API
- 🔜 優惠券系統 API
- 🔜 商品評論 API
- 🔜 圖片上傳 API
- 🔜 Webhook 通知
- 🔜 GraphQL 支援

---

## 🌐 Swagger UI

**存取位置**: 
- Development: http://localhost:8000/docs
- Alternative: http://localhost:8000/redoc

FastAPI 自動生成互動式 API 文檔，支援：
- 線上測試所有端點
- 自動驗證請求參數
- 查看完整的 Schema 定義

---

**文件版本**: 1.0  
**最後更新**: 2025-10-22  
**API 版本**: v1  
**維護團隊**: Development Team

**備註**: 本文件與實際 API 實作同步更新。如有任何問題或建議，請聯繫開發團隊。

