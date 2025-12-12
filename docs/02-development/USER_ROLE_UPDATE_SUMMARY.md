# 用戶角色註冊功能更新總結

**更新日期**: 2025-11-13  
**相關階段**: Phase 3  
**問題來源**: 用戶需求 - 支持 Vendor 註冊以測試商品上傳功能

---

## 🎯 更新目標

1. ✅ 允許用戶註冊為 **Customer** 或 **Vendor**
2. ✅ 禁止通過註冊獲得 **Admin** 角色
3. ✅ 創建初始化腳本來設置默認 Admin 賬戶
4. ✅ 更新前端 Demo 支持角色選擇

---

## 📦 修改的文件

### 1. 後端核心文件

#### `app/models/user.py`
**修改內容**:
- 在 `UserCreate` 模型中添加 `role` 字段（可選）
- 添加 `validate_role` 驗證器，禁止註冊為 admin

```python
class UserCreate(UserBase):
    password: str = Field(...)
    role: Optional[UserRole] = Field(default=None, description="...")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[UserRole]) -> Optional[UserRole]:
        if v is not None and v == UserRole.ADMIN:
            raise ValueError('Cannot register as admin...')
        return v
```

#### `app/services/user_service.py`
**修改內容**:
- 修改 `create_user` 方法，支持用戶指定角色
- 如果未指定角色，使用默認的 `customer` 角色

```python
user_role = user_data.role.value if user_data.role else settings.DEFAULT_USER_ROLE
```

### 2. 前端文件

#### `frontend_demo.html`
**修改內容**:
- 在註冊表單中添加角色選擇下拉菜單
- 支持選擇 Customer 或 Vendor
- 更新表單提交邏輯，包含角色數據

```html
<select id="registerRole">
    <option value="customer">👤 顧客 (Customer)</option>
    <option value="vendor">🏪 商家 (Vendor)</option>
</select>
```

### 3. 新增文件

#### `scripts/init_admin.py`
**功能**: Python 腳本，用於初始化管理員賬戶和可選的測試用戶

**特性**:
- 創建默認 admin 賬戶 (`admin@ecommerce.com`)
- 可選創建測試的 vendor 和 customer 賬戶
- 檢查重複，避免重複創建
- 友好的終端輸出和安全提示

#### `init_users.ps1`
**功能**: PowerShell 快速啟動腳本

**特性**:
- 自動檢測並使用虛擬環境的 Python
- 運行 `scripts/init_admin.py`
- 簡化用戶操作流程

#### `docs/02-development/USER_ROLE_REGISTRATION.md`
**功能**: 完整的角色註冊機制說明文檔

**內容**:
- 三種角色的詳細說明
- 安全設計原理
- API 使用示例
- 代碼實現細節
- 測試場景
- 常見問題解答

#### `docs/01-getting-started/USER_ROLE_QUICK_START.md`
**功能**: 快速開始指南

**內容**:
- 3 步驟快速開始
- 角色對比表
- 實用測試場景
- 常見問題

---

## 🎭 角色系統設計

| 角色 | 獲取方式 | 權限 | 安全等級 |
|------|----------|------|----------|
| **Customer** 👤 | 公開註冊（默認） | 瀏覽/購買商品 | 低 |
| **Vendor** 🏪 | 公開註冊（需選擇） | Customer 權限 + 管理商品 | 中 |
| **Admin** 🔐 | 系統初始化腳本 | 所有權限 | 高 |

### 安全機制

1. **Pydantic 驗證**: 在數據模型層面阻止 admin 註冊
2. **服務層邏輯**: 確保角色正確分配
3. **初始化隔離**: Admin 只能通過專用腳本創建
4. **密碼強度**: 所有賬戶都要求強密碼

---

## 🧪 測試場景

### ✅ 測試 1: 默認註冊為 Customer
```bash
POST /api/v1/auth/register
{
  "email": "user1@example.com",
  "password": "User123!",
  "full_name": "測試用戶",
  "phone": "0911111111"
  # role 未指定，默認為 customer
}
```
**結果**: 成功，角色為 `customer`

### ✅ 測試 2: 註冊為 Vendor
```bash
POST /api/v1/auth/register
{
  "email": "vendor1@example.com",
  "password": "Vendor123!",
  "full_name": "測試商家",
  "phone": "0922222222",
  "role": "vendor"  # 明確指定
}
```
**結果**: 成功，角色為 `vendor`

### ❌ 測試 3: 嘗試註冊為 Admin
```bash
POST /api/v1/auth/register
{
  "email": "hacker@example.com",
  "password": "Hacker123!",
  "full_name": "黑客",
  "phone": "0933333333",
  "role": "admin"  # 嘗試註冊為 admin
}
```
**結果**: 失敗，返回錯誤
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Cannot register as admin. Admin accounts must be created by system administrators."
  }
}
```

---

## 🚀 使用流程

### 首次部署

```powershell
# 1. 初始化用戶（創建 admin 和測試賬戶）
.\init_users.ps1

# 2. 啟動後端
.\start_backend.ps1

# 3. 啟動前端（另一個終端）
.\start_frontend.ps1

# 4. 訪問前端測試
# http://localhost:8080/frontend_demo.html
```

### 日常使用

#### 註冊新商家
1. 訪問前端 Demo
2. 選擇「註冊」標籤
3. 填寫資料，選擇「🏪 商家 (Vendor)」
4. 註冊成功後即可上傳商品

#### 註冊新顧客
1. 訪問前端 Demo
2. 選擇「註冊」標籤
3. 填寫資料，保持默認「👤 顧客 (Customer)」
4. 註冊成功後可瀏覽購買商品

#### 管理員登錄
1. 使用 `admin@ecommerce.com` / `Admin123!` 登錄
2. **立即修改密碼**（重要！）
3. 管理所有用戶和商品

---

## 📋 默認賬戶

運行 `init_users.ps1` 後創建的賬戶：

### 🔐 管理員
```
Email:    admin@ecommerce.com
Password: Admin123!
角色:     admin
```
⚠️ **重要**: 首次登錄後請立即修改密碼！

### 🏪 測試商家
```
Email:    vendor@test.com
Password: Vendor123!
角色:     vendor
```

### 👤 測試顧客
```
Email:    customer@test.com
Password: Customer123!
角色:     customer
```

---

## 🔧 技術實現細節

### Pydantic V2 驗證器

使用 `@field_validator` 裝飾器（Pydantic V2 語法）：

```python
@field_validator('role')
@classmethod
def validate_role(cls, v: Optional[UserRole]) -> Optional[UserRole]:
    """驗證角色：不允許註冊為 admin"""
    if v is not None and v == UserRole.ADMIN:
        raise ValueError('Cannot register as admin...')
    return v
```

### 服務層邏輯

```python
async def create_user(self, user_data: UserCreate) -> UserInDB:
    # 如果用戶指定了角色且不是 admin，則使用指定的角色
    # 否則使用默認角色 (customer)
    user_role = user_data.role.value if user_data.role else settings.DEFAULT_USER_ROLE
    
    user_dict = {
        # ...
        "role": user_role,
        # ...
    }
```

### 前端角色選擇

```javascript
const role = document.getElementById('registerRole').value;

body: JSON.stringify({
    email,
    password,
    full_name,
    phone,
    role: role  // 傳送角色給後端
})
```

---

## 📊 影響分析

### ✅ 已測試
- [x] Customer 默認註冊
- [x] Vendor 註冊
- [x] Admin 註冊阻止（驗證錯誤）
- [x] 前端角色選擇
- [x] 初始化腳本
- [x] 無 Linter 錯誤

### 🔄 向後兼容性
- ✅ **完全兼容**: 現有的註冊邏輯不受影響
- ✅ **默認行為**: 未指定角色時仍為 customer
- ✅ **API 兼容**: 舊的註冊請求仍然有效

### 🎯 後續優化建議
- [ ] 添加郵箱驗證
- [ ] Vendor 申請審核流程
- [ ] 更細粒度的權限控制
- [ ] 用戶活動日誌

---

## 📚 相關文檔

1. **完整說明**: [`docs/02-development/USER_ROLE_REGISTRATION.md`](docs/02-development/USER_ROLE_REGISTRATION.md)
2. **快速開始**: [`docs/01-getting-started/USER_ROLE_QUICK_START.md`](docs/01-getting-started/USER_ROLE_QUICK_START.md)
3. **前端 Demo**: [`frontend_demo.html`](frontend_demo.html)
4. **初始化腳本**: [`scripts/init_admin.py`](scripts/init_admin.py)

---

## ✅ 完成狀態

| 任務 | 狀態 |
|------|------|
| 後端角色驗證 | ✅ 完成 |
| 服務層邏輯 | ✅ 完成 |
| 前端角色選擇 | ✅ 完成 |
| Admin 初始化腳本 | ✅ 完成 |
| 文檔編寫 | ✅ 完成 |
| 測試驗證 | ✅ 完成 |

---

## 🎉 成果

現在系統支持：
1. ✅ 用戶可以選擇註冊為 **Customer** 或 **Vendor**
2. ✅ **Admin** 角色受到保護，不能通過註冊獲得
3. ✅ 提供便捷的初始化腳本創建管理員賬戶
4. ✅ 前端提供友好的角色選擇界面
5. ✅ 完整的文檔和使用指南

**現在你可以**:
- 註冊 Vendor 賬戶來測試商品上傳功能 🏪
- 使用默認 Admin 賬戶進行系統管理 🔐
- 安全地部署到生產環境 ✅

---

**更新完成！開始測試商品管理功能吧！** 🚀


