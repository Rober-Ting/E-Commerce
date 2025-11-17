# 🧪 Phase 2 API 测试指南

> 服务器地址: http://127.0.0.1:8000

---

## 🚀 快速开始

### 启动服务器
```bash
uvicorn app.main:app --reload
```

### 运行自动测试
```powershell
.\test_api_manual.ps1
```

### 访问交互式文档
浏览器打开: http://127.0.0.1:8000/docs

---

## 📋 API 端点清单

### 公开端点（无需认证）

#### 1. 健康检查
```bash
GET http://127.0.0.1:8000/health
```

#### 2. 用户注册
```bash
POST http://127.0.0.1:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Your Name",
  "phone": "0912345678"
}
```

#### 3. 用户登录
```bash
POST http://127.0.0.1:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "690dae15e08b81db9bf42b61",
      "email": "user@example.com",
      "full_name": "Your Name",
      "role": "customer",
      "is_active": true
    }
  },
  "message": "Login successful"
}
```

---

### 受保护端点（需要 Token）

**使用方式**: 在请求头中添加
```
Authorization: Bearer <your_token>
```

#### 4. 获取当前用户信息
```bash
GET http://127.0.0.1:8000/api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 5. 修改密码
```bash
PUT http://127.0.0.1:8000/api/v1/auth/password
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

---

### 管理员端点（需要 admin 角色）

#### 6. 获取用户列表
```bash
GET http://127.0.0.1:8000/api/v1/users?page=1&per_page=10
Authorization: Bearer <admin_token>
```

#### 7. 获取用户详情
```bash
GET http://127.0.0.1:8000/api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

#### 8. 更新用户信息
```bash
PUT http://127.0.0.1:8000/api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "is_active": true,
  "role": "customer"
}
```

#### 9. 删除用户
```bash
DELETE http://127.0.0.1:8000/api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

---

## 🧪 使用 PowerShell 测试

### 1. 注册用户
```powershell
$registerData = @{
    email = "newuser@example.com"
    password = "SecurePass123!"
    full_name = "New User"
    phone = "0912345678"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
    -Method Post `
    -Body $registerData `
    -ContentType "application/json"

$response
```

### 2. 登录并获取 Token
```powershell
$loginData = @{
    email = "newuser@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
    -Method Post `
    -Body $loginData `
    -ContentType "application/json"

$token = $loginResponse.data.access_token
Write-Host "Token: $token"
```

### 3. 使用 Token 访问受保护端点
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$meResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/me" `
    -Method Get `
    -Headers $headers

$meResponse.data
```

---

## 🧪 使用 curl 测试

### 1. 注册用户
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User",
    "phone": "0912345678"
  }'
```

### 2. 登录
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. 获取用户信息（需要替换 TOKEN）
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🎯 测试场景

### 场景 1: 完整的注册-登录流程
1. ✅ 注册新用户 → 获得 Token
2. ✅ 使用 Token 访问 `/api/v1/auth/me`
3. ✅ 修改密码
4. ✅ 使用新密码重新登录

### 场景 2: 错误处理测试
1. ✅ 尝试用重复 email 注册 → 409 Conflict
2. ✅ 尝试用错误密码登录 → 401 Unauthorized
3. ✅ 不带 Token 访问受保护端点 → 401 Unauthorized
4. ✅ 使用过期或无效 Token → 401 Unauthorized

### 场景 3: 权限测试
1. ✅ 普通用户尝试访问 `/api/v1/users` → 403 Forbidden
2. ✅ 管理员访问 `/api/v1/users` → 200 OK

---

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  }
}
```

---

## 🔐 Token 使用说明

### Token 格式
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token 有效期
- **默认**: 60 分钟
- **可配置**: `app/config.py` 中的 `ACCESS_TOKEN_EXPIRE_MINUTES`

### Token 内容
```json
{
  "sub": "user@example.com",
  "role": "customer",
  "exp": 1699365600
}
```

---

## 🎓 测试账号

### 普通用户账号
```
Email: testuser_163011@example.com
Password: NewSecurePass456!
Role: customer
```

### 创建管理员账号（MongoDB 直接插入）
```javascript
// 在 MongoDB Compass 或 mongosh 中执行
db.users.insertOne({
  email: "admin@example.com",
  hashed_password: "$2b$12$...", // 需要先用 bcrypt 哈希
  full_name: "Admin User",
  phone: null,
  role: "admin",
  is_active: true,
  addresses: [],
  created_at: new Date(),
  updated_at: new Date()
})
```

或使用 Python 创建：
```python
from app.utils.security import hash_password
from app.database import db
import asyncio

async def create_admin():
    await db.client.connect()
    await db.db.users.insert_one({
        "email": "admin@example.com",
        "hashed_password": hash_password("AdminPass123!"),
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "addresses": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

asyncio.run(create_admin())
```

---

## 🚀 进阶测试

### 使用 Postman
1. 导入 API 端点
2. 设置环境变量 `{{baseUrl}}` = `http://127.0.0.1:8000`
3. 设置环境变量 `{{token}}` = 登录后获得的 Token
4. 在 Authorization 中选择 Bearer Token，值为 `{{token}}`

### 使用 Python requests
```python
import requests

# 注册
response = requests.post(
    "http://127.0.0.1:8000/api/v1/auth/register",
    json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
)
print(response.json())

# 登录
response = requests.post(
    "http://127.0.0.1:8000/api/v1/auth/login",
    json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
)
token = response.json()["data"]["access_token"]

# 访问受保护端点
response = requests.get(
    "http://127.0.0.1:8000/api/v1/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

---

## 🐛 常见问题

### 1. 401 Unauthorized
- **原因**: Token 缺失、过期或无效
- **解决**: 重新登录获取新 Token

### 2. 403 Forbidden
- **原因**: 权限不足（如普通用户访问管理员端点）
- **解决**: 使用具有相应权限的账号

### 3. 409 Conflict
- **原因**: 尝试注册已存在的 email
- **解决**: 使用不同的 email 或登录现有账号

### 4. 422 Unprocessable Entity
- **原因**: 请求数据格式错误或验证失败
- **解决**: 检查请求数据格式，确保符合 API 要求

---

## 📚 相关文档

- [Phase 2 完成报告](docs/02-development/PHASE2_PROGRESS.md)
- [疑难排解指南](docs/05-troubleshooting/PHASE2_TROUBLESHOOTING.md)
- [API 设计文档](docs/06-api-design/ecommerce_api_documentation.md)
- [FastAPI 交互式文档](http://127.0.0.1:8000/docs)
- [ReDoc 文档](http://127.0.0.1:8000/redoc)

---

**最后更新**: 2025-11-07  
**版本**: Phase 2 Complete  
**状态**: ✅ All tests passing

