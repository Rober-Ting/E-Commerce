# 🎯 异常使用指南

## 📌 问题：为什么混用两种异常？

### 当前状态

**`app/api/v1/auth.py` 第 7 行：**
```python
from fastapi import APIRouter, Depends, HTTPException, status
```

**第 20 行：**
```python
from app.middleware.error_handler import ValidationException, NotFoundException
```

**使用情况：**
- ✅ 第 20 行导入了自定义异常
- ❌ 但实际使用的是 FastAPI 的 `HTTPException`（第 98、106、215 行）

---

## 🔍 两种异常的对比

### 1. FastAPI 的 HTTPException

**来源：** `from fastapi import HTTPException`

**特点：**
- ✅ FastAPI 内置
- ✅ 简单直接
- ⚠️ 格式不统一（会被我们的错误处理器转换）
- ⚠️ 无法携带详细的 `details` 信息
- ⚠️ 错误代码需要从状态码映射

**使用示例：**
```python
raise HTTPException(
    status_code=401,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"}
)
```

**返回格式（经过我们的错误处理器转换后）：**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",        // ← 从 status_code 映射
    "message": "Incorrect email or password",
    "details": {}                  // ← 空的
  }
}
```

---

### 2. 我们的自定义异常

**来源：** `from app.middleware.error_handler import UnauthorizedException`

**特点：**
- ✅ 语义更明确
- ✅ 统一的错误格式
- ✅ 可以携带详细的 `details` 信息
- ✅ 错误代码更明确
- ✅ 更容易维护和扩展

**使用示例：**
```python
raise UnauthorizedException(
    message="Incorrect email or password"
)
```

**返回格式：**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",        // ← 异常类自带
    "message": "Incorrect email or password",
    "details": {}
  }
}
```

---

## 📊 详细对比表

| 特性 | FastAPI `HTTPException` | 自定义异常 |
|------|------------------------|-----------|
| **来源** | FastAPI 内置 | 我们创建的 `error_handler.py` |
| **语义明确性** | ⚠️ 需要看状态码 | ✅ 类名即语义（`UnauthorizedException`） |
| **错误代码** | ⚠️ 从状态码映射 | ✅ 类自带明确的 `code` |
| **详细信息** | ❌ 无法携带 `details` | ✅ 支持 `details` 字典 |
| **统一格式** | ⚠️ 需要错误处理器转换 | ✅ 原生统一格式 |
| **代码可读性** | ⚠️ 普通 | ✅ 更好 |
| **维护性** | ⚠️ 普通 | ✅ 更好 |

---

## 🎯 推荐使用：自定义异常

### 可用的自定义异常类

**文件：`app/middleware/error_handler.py`**

```python
# 基础异常类
class APIException(Exception)           # 基类

# 具体的异常类
class NotFoundException(APIException)    # 404 - 资源不存在
class AlreadyExistsException(APIException) # 409 - 资源已存在
class UnauthorizedException(APIException)  # 401 - 未授权
class ForbiddenException(APIException)     # 403 - 权限不足
class ValidationException(APIException)    # 422 - 验证失败
class BadRequestException(APIException)    # 400 - 错误请求
class DatabaseException(APIException)      # 500 - 数据库错误
```

---

## ✨ 改进建议

### 改进前（当前代码）

```python
# app/api/v1/auth.py
from fastapi import HTTPException, status

# 登录失败
if user is None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

# 用户未激活
if not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is not active"
    )

# 密码修改失败
if not success:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to change password"
    )
```

---

### 改进后（推荐）

```python
# app/api/v1/auth.py
from app.middleware.error_handler import (
    UnauthorizedException,
    ForbiddenException,
    DatabaseException
)

# 登录失败
if user is None:
    raise UnauthorizedException(
        message="Incorrect email or password"
    )

# 用户未激活
if not user.is_active:
    raise ForbiddenException(
        message="User account is not active"
    )

# 密码修改失败
if not success:
    raise DatabaseException(
        message="Failed to change password",
        details={"user_id": current_user.id}
    )
```

---

## 🎨 改进的好处

### 1. 代码更清晰

**改进前：**
```python
raise HTTPException(status_code=401, detail="...")
# 😕 需要看状态码才知道是什么错误
```

**改进后：**
```python
raise UnauthorizedException(message="...")
# 😊 一看就知道是"未授权"错误
```

---

### 2. 可以携带详细信息

**改进前：**
```python
raise HTTPException(
    status_code=422,
    detail="Validation failed"
)
# ❌ 无法携带详细的验证错误信息
```

**改进后：**
```python
raise ValidationException(
    message="Validation failed",
    details={
        "field": "email",
        "error": "Email format is invalid",
        "value": "invalid-email"
    }
)
# ✅ 可以携带详细信息
```

前端收到：
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "field": "email",
      "error": "Email format is invalid",
      "value": "invalid-email"
    }
  }
}
```

---

### 3. 统一的错误处理

所有自定义异常都遵循相同的格式：

```python
class APIException(Exception):
    def __init__(
        self,
        status_code: int = 500,
        code: str = "INTERNAL_ERROR",
        message: str = "An error occurred",
        details: dict = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
```

---

## 🔧 完整的改进代码

### 步骤 1：修改导入

**改进前：**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.error_handler import ValidationException, NotFoundException
```

**改进后：**
```python
from fastapi import APIRouter, Depends, status
from app.middleware.error_handler import (
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    NotFoundException,
    DatabaseException
)
```

---

### 步骤 2：修改异常抛出

#### **位置 1：登录失败（第 98 行）**

**改进前：**
```python
if user is None:
    logger.warning(f"登入失敗: 無效的憑證 email={credentials.email}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
```

**改进后：**
```python
if user is None:
    logger.warning(f"登入失敗: 無效的憑證 email={credentials.email}")
    raise UnauthorizedException(
        message="Incorrect email or password"
    )
```

**注意：** `WWW-Authenticate` 头部会在错误处理器中自动添加（如果需要的话）。

---

#### **位置 2：用户未激活（第 106 行）**

**改进前：**
```python
if not user.is_active:
    logger.warning(f"登入失敗: 用戶未啟用 user_id={user.id}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is not active"
    )
```

**改进后：**
```python
if not user.is_active:
    logger.warning(f"登入失敗: 用戶未啟用 user_id={user.id}")
    raise ForbiddenException(
        message="User account is not active"
    )
```

---

#### **位置 3：密码修改失败（第 215 行）**

**改进前：**
```python
if not success:
    logger.error(f"密碼修改失敗: user_id={current_user.id}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to change password"
    )
```

**改进后：**
```python
if not success:
    logger.error(f"密碼修改失敗: user_id={current_user.id}")
    raise DatabaseException(
        message="Failed to change password",
        details={"user_id": current_user.id}
    )
```

---

## 🎓 最佳实践

### 1. 根据业务逻辑选择异常

| 场景 | 推荐异常 | 状态码 |
|------|---------|--------|
| 用户未登录/Token 无效 | `UnauthorizedException` | 401 |
| 权限不足 | `ForbiddenException` | 403 |
| 资源不存在 | `NotFoundException` | 404 |
| 资源已存在 | `AlreadyExistsException` | 409 |
| 数据验证失败 | `ValidationException` | 422 |
| 请求参数错误 | `BadRequestException` | 400 |
| 数据库操作失败 | `DatabaseException` | 500 |

---

### 2. 提供详细的错误信息

**好的做法：**
```python
raise ValidationException(
    message="Email already registered",
    details={
        "field": "email",
        "value": user_data.email,
        "suggestion": "Try logging in or use forgot password"
    }
)
```

**不好的做法：**
```python
raise ValidationException(message="Error")  # 😕 太模糊
```

---

### 3. 记录日志

```python
if user is None:
    logger.warning(
        f"登入失敗: 無效的憑證 email={credentials.email}"
    )
    raise UnauthorizedException(
        message="Incorrect email or password"
    )
```

---

## 📝 完整示例

### 用户注册端点

```python
@router.post("/register", response_model=ResponseModel[TokenResponse])
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """用户注册"""
    logger.info(f"註冊請求: email={user_data.email}")
    
    user_service = UserService(db)
    
    try:
        # 创建用户
        user = await user_service.create_user(user_data)
        
    except ValidationException as e:
        # 已经是我们的自定义异常，直接抛出
        logger.warning(f"註冊失敗: {e.message}")
        raise
        
    except Exception as e:
        # 未预料的错误
        logger.error(f"註冊失敗: {str(e)}", exc_info=True)
        raise DatabaseException(
            message="Failed to create user",
            details={"error": str(e)}
        )
    
    # 创建 Token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    
    user_response = await user_service.user_to_response(user)
    token_data = create_token_response(access_token, user_response.model_dump())
    
    logger.info(f"註冊成功: user_id={user.id}")
    return success_response(
        data=token_data,
        message="User registered successfully"
    )
```

---

## 🚫 特殊情况：何时使用 HTTPException

在极少数情况下，你可能仍然需要使用 `HTTPException`：

### 1. 需要自定义响应头部

```python
# 如果自定义异常不支持添加 headers
raise HTTPException(
    status_code=401,
    detail="Token expired",
    headers={
        "WWW-Authenticate": 'Bearer error="invalid_token"',
        "X-Custom-Header": "value"
    }
)
```

**解决方案：** 可以扩展自定义异常类添加 `headers` 参数。

---

### 2. 非常规的状态码

```python
# 如果需要 418 I'm a teapot（开玩笑）
raise HTTPException(status_code=418, detail="I'm a teapot")
```

**解决方案：** 为常见的状态码创建自定义异常类。

---

## 🎯 总结

### 当前状态
```python
from fastapi import HTTPException  # ← 使用 FastAPI 内置
raise HTTPException(status_code=401, detail="...")
```

### 推荐改进
```python
from app.middleware.error_handler import UnauthorizedException  # ← 使用自定义
raise UnauthorizedException(message="...")
```

### 改进好处
- ✅ 代码更清晰（类名即语义）
- ✅ 格式更统一（原生支持我们的格式）
- ✅ 功能更强大（支持 `details`）
- ✅ 更易维护（集中管理）

---

## 📚 相关文件

- `app/middleware/error_handler.py` - 异常定义
- `app/api/v1/auth.py` - 当前使用 HTTPException 的地方
- `app/services/user_service.py` - 已经使用自定义异常的示例

---

**需要我帮你重构 `auth.py` 吗？** 🚀

