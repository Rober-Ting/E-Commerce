# 用戶角色與註冊機制說明

## 📋 概述

本文檔說明 E-Commerce API 的用戶角色系統和註冊機制。

---

## 🎭 用戶角色

系統支援三種用戶角色：

### 1. **Customer (顧客)** 👤
- **獲取方式**: 可以通過註冊獲得（默認角色）
- **權限**:
  - 瀏覽商品
  - 購買商品
  - 管理個人訂單
  - 管理收貨地址
  - 修改個人資料

### 2. **Vendor (商家)** 🏪
- **獲取方式**: 可以通過註冊獲得（需在註冊時選擇）
- **權限**:
  - Customer 的所有權限
  - 創建商品
  - 管理自己的商品
  - 查看商品銷售統計
  - 處理商品庫存

### 3. **Admin (管理員)** 🔐
- **獲取方式**: ⚠️ **不能通過註冊獲得**
- **創建方式**: 只能通過系統初始化腳本創建
- **權限**:
  - 所有用戶的權限
  - 管理所有用戶
  - 管理所有商品
  - 修改用戶角色
  - 系統配置管理

---

## 🔐 安全設計

### 為什麼 Admin 不能註冊？

1. **安全性**: Admin 擁有最高權限，不應該開放給公眾註冊
2. **可控性**: Admin 賬戶應該由系統管理員嚴格控制
3. **審計**: 所有 Admin 賬戶應該有明確的創建記錄

### 角色驗證機制

在 `app/models/user.py` 中，我們添加了角色驗證器：

```python
@field_validator('role')
@classmethod
def validate_role(cls, v: Optional[UserRole]) -> Optional[UserRole]:
    """驗證角色：不允許註冊為 admin"""
    if v is not None and v == UserRole.ADMIN:
        raise ValueError('Cannot register as admin. Admin accounts must be created by system administrators.')
    return v
```

**如果有人嘗試註冊為 admin，會收到錯誤提示。**

---

## 🚀 使用指南

### 1. 初始化 Admin 賬戶

在首次部署系統時，必須先創建管理員賬戶：

#### Windows PowerShell:
```powershell
.\init_users.ps1
```

#### Linux/Mac:
```bash
source venv/bin/activate
python scripts/init_admin.py
```

#### 默認管理員賬戶:
```
📧 Email:    admin@ecommerce.com
🔒 Password: Admin123!
🎭 角色:     admin
```

⚠️ **重要**: 創建後請立即登錄並修改密碼！

---

### 2. 註冊 Customer (顧客)

#### API 請求:
```json
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "customer@example.com",
    "password": "Customer123!",
    "full_name": "張三",
    "phone": "0912345678",
    "role": "customer"  // 可選，默認為 customer
}
```

#### 前端 Demo:
1. 訪問 `http://localhost:8080/frontend_demo.html`
2. 點擊「註冊」標籤
3. 填寫資料，選擇「顧客 (Customer)」
4. 點擊「註冊」

---

### 3. 註冊 Vendor (商家)

#### API 請求:
```json
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "vendor@example.com",
    "password": "Vendor123!",
    "full_name": "小店鋪",
    "phone": "0923456789",
    "role": "vendor"  // 指定為 vendor
}
```

#### 前端 Demo:
1. 訪問 `http://localhost:8080/frontend_demo.html`
2. 點擊「註冊」標籤
3. 填寫資料，選擇「商家 (Vendor)」
4. 點擊「註冊」

---

## 💻 代碼實現

### 1. 數據模型 (`app/models/user.py`)

```python
class UserCreate(UserBase):
    """用戶創建（註冊）請求模型"""
    password: str = Field(...)
    role: Optional[UserRole] = Field(
        default=None, 
        description="用戶角色（可選：customer 或 vendor，默認為 customer）"
    )
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[UserRole]) -> Optional[UserRole]:
        """驗證角色：不允許註冊為 admin"""
        if v is not None and v == UserRole.ADMIN:
            raise ValueError('Cannot register as admin.')
        return v
```

### 2. 服務層 (`app/services/user_service.py`)

```python
async def create_user(self, user_data: UserCreate) -> UserInDB:
    """創建新用戶"""
    # 如果用戶指定了角色且不是 admin，則使用指定的角色
    # 否則使用默認角色 (customer)
    user_role = user_data.role.value if user_data.role else settings.DEFAULT_USER_ROLE
    
    user_dict = {
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": user_role,  # 使用確定的角色
        # ...
    }
    # ...
```

---

## 🧪 測試場景

### 測試 1: 註冊為 Customer (默認)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "password": "Test123!",
    "full_name": "測試用戶1",
    "phone": "0911111111"
  }'
```
✅ **預期結果**: 成功創建，角色為 `customer`

---

### 測試 2: 註冊為 Vendor
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "Test123!",
    "full_name": "測試商家",
    "phone": "0922222222",
    "role": "vendor"
  }'
```
✅ **預期結果**: 成功創建，角色為 `vendor`

---

### 測試 3: 嘗試註冊為 Admin (應該失敗)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test3@example.com",
    "password": "Test123!",
    "full_name": "測試管理員",
    "phone": "0933333333",
    "role": "admin"
  }'
```
❌ **預期結果**: 
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Cannot register as admin. Admin accounts must be created by system administrators.",
    "details": {}
  }
}
```

---

## 📊 角色權限對比表

| 功能 | Customer | Vendor | Admin |
|------|----------|--------|-------|
| 瀏覽商品 | ✅ | ✅ | ✅ |
| 購買商品 | ✅ | ✅ | ✅ |
| 管理個人訂單 | ✅ | ✅ | ✅ |
| 創建商品 | ❌ | ✅ | ✅ |
| 管理自己的商品 | ❌ | ✅ | ✅ |
| 管理所有商品 | ❌ | ❌ | ✅ |
| 查看所有用戶 | ❌ | ❌ | ✅ |
| 修改用戶角色 | ❌ | ❌ | ✅ |
| 系統配置 | ❌ | ❌ | ✅ |

---

## 🔧 相關文件

### 後端文件
- `app/models/user.py` - 用戶數據模型
- `app/services/user_service.py` - 用戶服務層
- `app/api/v1/auth.py` - 認證 API
- `app/utils/dependencies.py` - 權限依賴注入

### 腳本文件
- `scripts/init_admin.py` - Admin 初始化腳本
- `init_users.ps1` - Windows 快速啟動腳本

### 前端文件
- `frontend_demo.html` - 前端 Demo（包含角色選擇）

---

## ❓ 常見問題

### Q1: 忘記了 Admin 密碼怎麼辦？
**A**: 可以手動在 MongoDB 中重置：
```bash
# 連接到 MongoDB
mongo

# 切換到數據庫
use ecommerce_db

# 更新密碼（使用預先計算的哈希值）
db.users.updateOne(
  { email: "admin@ecommerce.com" },
  { $set: { hashed_password: "新的哈希密碼" } }
)
```

或者刪除 admin 用戶後重新運行初始化腳本。

### Q2: 可以將 Customer 升級為 Vendor 嗎？
**A**: 可以，管理員可以通過 API 修改用戶角色：
```bash
PATCH /api/v1/users/{user_id}/role
Authorization: Bearer {admin_token}

{
  "role": "vendor"
}
```

### Q3: Vendor 可以看到其他 Vendor 的商品嗎？
**A**: 可以瀏覽，但只能編輯/刪除自己的商品。

### Q4: 如何創建多個 Admin？
**A**: 使用現有 Admin 賬戶，通過 API 將其他用戶升級為 Admin：
```bash
PATCH /api/v1/users/{user_id}/role
Authorization: Bearer {admin_token}

{
  "role": "admin"
}
```

---

## 🔄 未來改進

- [ ] 添加郵箱驗證
- [ ] 實現 Vendor 申請審核流程
- [ ] 添加角色權限的細粒度控制 (RBAC)
- [ ] 實現用戶禁用/啟用功能
- [ ] 添加用戶活動日誌

---

**最後更新**: 2025-11-13
**版本**: Phase 3

