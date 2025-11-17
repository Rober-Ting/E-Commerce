# 🔍 错误处理机制详解

## 📌 问题：为什么 `detail` 变成了 `error.message`？

### 简短答案
**错误处理中间件自动转换了格式！**

---

## 🔄 完整流程

### 步骤 1：后端抛出异常

**文件：`app/api/v1/auth.py`**

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",  # ← 原始错误消息
    headers={"WWW-Authenticate": "Bearer"}
)
```

**FastAPI 原生格式：**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### 步骤 2：注册错误处理器

**文件：`app/main.py` 第 47 行**

```python
register_exception_handlers(app)
```

这会注册所有自定义的错误处理器。

---

### 步骤 3：错误处理器拦截并转换

**文件：`app/middleware/error_handler.py` 第 180-224 行**

```python
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    # 状态码映射
    code_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",      # ← 401 映射到这里
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR"
    }
    
    error_code = code_mapping.get(exc.status_code, "HTTP_ERROR")
    
    # 转换为统一格式
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,           # ← 从状态码映射
                "message": exc.detail,        # ← detail 变成 message
                "details": {}
            }
        }
    )
```

---

### 步骤 4：返回给前端

**最终的 JSON 响应：**

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Incorrect email or password",
    "details": {}
  }
}
```

---

## 📊 数据转换对比表

| 阶段 | 格式 | 字段 |
|------|------|------|
| **FastAPI 原生** | `HTTPException` | `detail`, `status_code` |
| **我们的统一格式** | `error` 对象 | `code`, `message`, `details` |

### 字段映射

| FastAPI | 我们的格式 | 示例 |
|---------|-----------|------|
| `status_code: 401` | `error.code: "UNAUTHORIZED"` | 通过 `code_mapping` 映射 |
| `detail: "Incorrect email..."` | `error.message: "Incorrect email..."` | 直接复制 |
| - | `error.details: {}` | 额外的错误详情 |
| - | `success: false` | 标识请求失败 |

---

## 🎯 为什么要这样转换？

### 优点

1. **统一的响应格式**
   - 所有 API 错误都使用相同的结构
   - 前端只需要一种错误处理逻辑

2. **更清晰的错误分类**
   ```python
   # 不同类型的错误都有明确的 code
   "UNAUTHORIZED"         # 认证失败
   "FORBIDDEN"            # 权限不足
   "VALIDATION_ERROR"     # 数据验证失败
   "NOT_FOUND"            # 资源不存在
   ```

3. **更丰富的错误信息**
   ```json
   {
     "code": "VALIDATION_ERROR",      // 错误类型（程序可判断）
     "message": "Email already exists", // 用户可读消息
     "details": {                       // 详细信息
       "field": "email",
       "value": "test@example.com"
     }
   }
   ```

4. **符合 REST API 最佳实践**
   - `success` 字段明确指示请求状态
   - `error` 对象包含完整的错误信息
   - 便于前端统一处理

---

## 🔐 WWW-Authenticate 头部详解

### 什么是 WWW-Authenticate？

**定义：** HTTP 401 响应的标准头部，告诉客户端需要认证。

**标准：** [RFC 7235 - HTTP Authentication](https://tools.ietf.org/html/rfc7235)

---

### Bearer 认证方式

**Bearer** 是 OAuth 2.0 定义的 Token 认证方式。

**标准：** [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://tools.ietf.org/html/rfc6750)

**格式：**
```http
Authorization: Bearer <token>
```

**示例：**
```http
GET /api/v1/auth/me HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6ImN1c3RvbWVyIiwiZXhwIjoxNzMxNDE1MjAwfQ.signature
Content-Type: application/json
```

---

### 为什么需要这个头部？

#### 1. HTTP 标准要求

> **RFC 7235, Section 3.1:**  
> A server generating a 401 (Unauthorized) response MUST send a WWW-Authenticate header field containing at least one challenge.

**翻译：** 服务器返回 401 响应时，**必须**包含 `WWW-Authenticate` 头部。

#### 2. 告知客户端认证方式

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
                  ^^^^^^
                  告诉客户端：使用 Bearer Token 认证
```

#### 3. 自动化工具支持

- **Swagger UI** 会显示 "Authorize" 按钮
- **Postman** 会自动识别 Bearer Token
- **浏览器** 知道这是 API 认证（不是基本认证）

---

### 实际的 HTTP 响应示例

#### 登录失败（401）

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: application/json
Content-Length: 145

{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Incorrect email or password",
    "details": {}
  }
}
```

#### Token 无效（401）

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_token"
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": {}
  }
}
```

#### 权限不足（403）

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "details": {}
  }
}
```

注意：403 不需要 `WWW-Authenticate`，因为不是认证问题，而是权限问题。

---

### 不同认证方式对比

| 认证方式 | WWW-Authenticate 示例 | Authorization 格式 | 使用场景 |
|---------|----------------------|-------------------|---------|
| **Bearer** | `Bearer` | `Bearer <token>` | JWT、OAuth 2.0、现代 API |
| **Basic** | `Basic realm="API"` | `Basic <base64(user:pass)>` | 简单 HTTP 认证 |
| **Digest** | `Digest realm="API", nonce="..."` | `Digest username="...", response="..."` | 更安全的密码认证 |
| **API Key** | 无标准 | `X-API-Key: <key>` | 自定义 API Key |

---

### Bearer Token 的使用流程

```
┌──────────────────────────────────────────────────────────┐
│ 1. 用户登录                                               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ POST /api/v1/auth/login                                  │
│ {                                                         │
│   "email": "user@example.com",                           │
│   "password": "password123"                              │
│ }                                                         │
│                                                           │
│ ↓ 成功响应                                                │
│                                                           │
│ {                                                         │
│   "access_token": "eyJhbGci...",                         │
│   "token_type": "bearer"                                 │
│ }                                                         │
│                                                           │
└──────────────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│ 2. 保存 Token                                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ localStorage.setItem('token', access_token)              │
│                                                           │
└──────────────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│ 3. 后续请求携带 Token                                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ GET /api/v1/auth/me                                      │
│ Headers:                                                  │
│   Authorization: Bearer eyJhbGci...                      │
│                                                           │
│ ↓ 成功响应                                                │
│                                                           │
│ {                                                         │
│   "success": true,                                       │
│   "data": {                                              │
│     "email": "user@example.com",                         │
│     "role": "customer"                                   │
│   }                                                       │
│ }                                                         │
│                                                           │
└──────────────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│ 4. Token 无效或过期                                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ GET /api/v1/auth/me                                      │
│ Headers:                                                  │
│   Authorization: Bearer <invalid_token>                  │
│                                                           │
│ ↓ 401 响应                                                │
│                                                           │
│ HTTP/1.1 401 Unauthorized                                │
│ WWW-Authenticate: Bearer  ← 提示需要认证                 │
│                                                           │
│ {                                                         │
│   "success": false,                                      │
│   "error": {                                             │
│     "code": "UNAUTHORIZED",                              │
│     "message": "Invalid or expired token"                │
│   }                                                       │
│ }                                                         │
│                                                           │
│ ↓ 前端处理：重定向到登录页                                │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 💡 前端如何处理

### 1. 保存 Token

```javascript
// 登录成功后
const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});

const data = await response.json();

if (data.success) {
    // 保存 Token
    localStorage.setItem('token', data.data.access_token);
    console.log('Token 类型:', data.data.token_type); // "bearer"
}
```

### 2. 携带 Token 发送请求

```javascript
// 从 localStorage 获取 Token
const token = localStorage.getItem('token');

// 发送认证请求
const response = await fetch('/api/v1/auth/me', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,  // ← 关键！
        'Content-Type': 'application/json'
    }
});
```

### 3. 统一错误处理

```javascript
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('token');
    
    // 添加 Authorization 头部
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    const data = await response.json();
    
    // 统一处理错误
    if (!data.success) {
        // 401: 重定向到登录页
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        
        // 其他错误：显示消息
        alert(`错误: ${data.error.message}`);
        throw new Error(data.error.message);
    }
    
    return data.data;
}

// 使用示例
try {
    const user = await apiRequest('/api/v1/auth/me');
    console.log('当前用户:', user);
} catch (error) {
    console.error('请求失败:', error);
}
```

---

## 🔍 调试技巧

### 1. 在浏览器开发者工具查看头部

**Network 面板 → 选择请求 → Headers 标签**

**Request Headers:**
```
Authorization: Bearer eyJhbGci...
Content-Type: application/json
```

**Response Headers:**
```
WWW-Authenticate: Bearer
Content-Type: application/json
```

### 2. 使用 curl 测试

```bash
# 登录
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -v

# 查看响应头部（-v 显示详细信息）
# 会看到 WWW-Authenticate: Bearer

# 使用 Token 访问受保护资源
curl -X GET http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_token>" \
  -v
```

### 3. 在 Swagger UI 测试

1. 访问 `http://127.0.0.1:8000/docs`
2. 点击右上角 **"Authorize"** 按钮
3. 输入 Token（不需要加 "Bearer " 前缀）
4. 点击 **"Authorize"**
5. 测试受保护的端点

---

## 📚 相关标准和文档

- [RFC 7235 - HTTP Authentication](https://tools.ietf.org/html/rfc7235)
- [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://tools.ietf.org/html/rfc6750)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

---

## 🎓 总结

### 问题 1：detail → message

**原因：** 错误处理中间件统一转换格式

**位置：** `app/middleware/error_handler.py:220`

**好处：**
- ✅ 统一的响应格式
- ✅ 更清晰的错误分类
- ✅ 更丰富的错误信息

### 问题 2：WWW-Authenticate: Bearer

**原因：** HTTP 401 标准要求

**作用：**
- ✅ 告知客户端需要认证
- ✅ 指明使用 Bearer Token
- ✅ 工具自动识别

**使用：** 
```javascript
headers: {
    'Authorization': `Bearer ${token}`
}
```

---

**有问题随时问我！** 🚀

