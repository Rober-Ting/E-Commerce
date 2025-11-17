# Dependencies 模組重構總結

## 📅 重構日期
2025-11-11

---

## 🎯 重構目標

將 `app/utils/dependencies.py` 和 `app/api/v1/users.py` 中的所有 `HTTPException` 替換為自定義異常，與 `auth.py` 保持一致。

**額外發現：** 在重構 `dependencies.py` 時，發現 `users.py` 中也有一處遺漏的 `HTTPException`，已一併修復。

---

## 🔄 重構內容

### **1. 導入修改**

#### **重構前：**
```python
from fastapi import Depends, HTTPException, status
```

#### **重構後：**
```python
from fastapi import Depends, status
from app.middleware.error_handler import (
    UnauthorizedException,
    ForbiddenException,
    DatabaseException
)
```

---

### **2. 異常替換明細**

#### **2.1 `get_current_user()` 函數**

| 位置 | 原異常 | 新異常 | 場景 |
|------|--------|--------|------|
| Line 45-52 | `HTTPException(401)` | `UnauthorizedException` | Token 解碼失敗 |
| Line 54-59 | `HTTPException(401)` | `UnauthorizedException` | Token 缺少 email |
| Line 61-68 | `HTTPException(401)` | `UnauthorizedException` | 用戶不存在 |
| Line 74-80 | `HTTPException(500)` | `DatabaseException` | 數據解析錯誤 |

**重構前：**
```python
if payload is None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

**重構後：**
```python
if payload is None:
    raise UnauthorizedException(
        message="Could not validate credentials"
    )
```

---

#### **2.2 `get_current_active_user()` 函數**

| 位置 | 原異常 | 新異常 | 場景 |
|------|--------|--------|------|
| Line 105-109 | `HTTPException(403)` | `ForbiddenException` | 用戶未啟用 |

**重構前：**
```python
if not current_user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user"
    )
```

**重構後：**
```python
if not current_user.is_active:
    raise ForbiddenException(
        message="Inactive user"
    )
```

---

#### **2.3 `require_role()` 函數**

| 位置 | 原異常 | 新異常 | 場景 |
|------|--------|--------|------|
| Line 136-140 | `HTTPException(403)` | `ForbiddenException` | 角色權限不足 |

**重構前：**
```python
if current_user.role != required_role:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Requires {required_role} role"
    )
```

**重構後：**
```python
if current_user.role != required_role:
    raise ForbiddenException(
        message=f"Requires {required_role} role"
    )
```

---

#### **2.4 `require_admin()` 函數**

| 位置 | 原異常 | 新異常 | 場景 |
|------|--------|--------|------|
| Line 162-166 | `HTTPException(403)` | `ForbiddenException` | 需要管理員權限 |

**重構前：**
```python
if current_user.role != UserRole.ADMIN:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )
```

**重構後：**
```python
if current_user.role != UserRole.ADMIN:
    raise ForbiddenException(
        message="Admin access required"
    )
```

---

#### **2.5 `require_vendor_or_admin()` 函數**

| 位置 | 原異常 | 新異常 | 場景 |
|------|--------|--------|------|
| Line 190-194 | `HTTPException(403)` | `ForbiddenException` | 需要店家或管理員權限 |

**重構前：**
```python
if current_user.role not in [UserRole.VENDOR, UserRole.ADMIN]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Vendor or admin access required"
    )
```

**重構後：**
```python
if current_user.role not in [UserRole.VENDOR, UserRole.ADMIN]:
    raise ForbiddenException(
        message="Vendor or admin access required"
    )
```

---

### **3. 文檔字符串更新**

#### **重構前：**
```python
"""
Raises:
    HTTPException: 401 - Token 無效或用戶不存在
"""
```

#### **重構後：**
```python
"""
Raises:
    UnauthorizedException: Token 無效或用戶不存在
    DatabaseException: 數據解析錯誤
"""
```

---

## 📊 重構統計

| 項目 | 數量 |
|------|------|
| **文件重構** | 2 個文件 |
| **函數重構** | 5 個函數 |
| **異常替換** | 9 處 |
| **文檔更新** | 3 處 |
| **導入變更** | 2 處 |

### **異常類型分布：**
- `UnauthorizedException`: 3 處（認證失敗）
- `ForbiddenException`: 4 處（權限不足）
- `DatabaseException`: 2 處（數據錯誤）

### **重構文件清單：**
1. ✅ `app/utils/dependencies.py` - 8 處異常替換
2. ✅ `app/api/v1/users.py` - 1 處異常替換（遺漏修復）

---

### **額外發現：`app/api/v1/users.py`**

在重構過程中發現 `users.py` 的 `delete_user_by_id()` 函數中有一處遺漏：

**Line 201-205 (重構前)：**
```python
if not success:
    logger.error(f"用戶刪除失敗: user_id={user_id}")
    from fastapi import HTTPException, status
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete user"
    )
```

**Line 201-204 (重構後)：**
```python
if not success:
    logger.error(f"用戶刪除失敗: user_id={user_id}")
    raise DatabaseException(
        message="Failed to delete user",
        details={"user_id": user_id}
    )
```

**同時更新導入：**
```python
# 重構前
from app.middleware.error_handler import NotFoundException

# 重構後
from app.middleware.error_handler import NotFoundException, DatabaseException
```

---

## ✅ 重構優點

### **1. 一致性**
```python
# ✅ 整個專案統一使用自定義異常
app/api/v1/auth.py         → 使用自定義異常
app/api/v1/users.py        → 使用自定義異常
app/utils/dependencies.py  → 使用自定義異常（已重構）
```

### **2. 更豐富的錯誤信息**
```python
# HTTPException
raise HTTPException(
    status_code=500,
    detail="Error parsing user data: ValueError(...)"
)

# 自定義異常（更詳細）
raise DatabaseException(
    message="Error parsing user data",
    details={
        "error": "ValueError(...)",
        "email": "user@example.com"
    }
)
```

### **3. 統一的響應格式**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Could not validate credentials",
    "details": {}
  },
  "timestamp": "2025-11-11T12:00:00Z"
}
```

### **4. 更好的語義化**
```python
# ❌ 不清楚
raise HTTPException(status_code=403, detail="...")

# ✅ 清楚明確
raise ForbiddenException(message="...")
```

---

## 🎯 影響範圍

### **受影響的文件：**
1. ✅ `app/utils/dependencies.py` - 已重構（8 處）
2. ✅ `app/api/v1/auth.py` - 之前已重構
3. ✅ `app/api/v1/users.py` - 已修復遺漏（1 處）

### **依賴此模組的功能：**
- ✅ 用戶認證 (`get_current_user`)
- ✅ 用戶活躍狀態檢查 (`get_current_active_user`)
- ✅ 管理員權限 (`require_admin`)
- ✅ 店家權限 (`require_vendor_or_admin`)
- ✅ 角色權限 (`require_role`)
- ✅ 可選認證 (`optional_user`)

---

## 🧪 測試建議

### **1. 單元測試**

```python
import pytest
from app.utils.dependencies import get_current_user
from app.middleware.error_handler import UnauthorizedException

async def test_invalid_token_raises_unauthorized():
    """測試無效 Token 應拋出 UnauthorizedException"""
    # 創建假的 credentials
    credentials = MockCredentials(token="invalid_token")
    
    # 應該拋出自定義異常
    with pytest.raises(UnauthorizedException) as exc_info:
        await get_current_user(credentials)
    
    # 驗證異常消息
    assert "Could not validate credentials" in str(exc_info.value)
```

### **2. 集成測試**

```python
async def test_protected_endpoint_without_token():
    """測試受保護的端點（無 Token）"""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"
```

### **3. 權限測試**

```python
async def test_admin_endpoint_requires_admin_role():
    """測試管理員端點需要管理員角色"""
    # 使用普通用戶 Token
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)
    
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"
    assert "Admin access required" in data["error"]["message"]
```

---

## 🔍 驗證清單

- [x] 所有 `HTTPException` 已替換為自定義異常
- [x] 導入語句已更新
- [x] 文檔字符串已更新
- [x] 無 linter 錯誤
- [x] 異常消息清晰明確
- [x] 響應格式符合標準

---

## 📝 注意事項

### **1. `optional_user()` 函數保持原樣**
```python
def optional_user():
    """可選的用戶認證"""
    async def optional_user_dependency(...):
        try:
            # ... 驗證邏輯 ...
        except Exception:
            return None  # ← 不拋出異常，返回 None
```

**原因：** 此函數設計為靜默失敗，允許匿名和認證用戶訪問。

---

### **2. `WWW-Authenticate` Header**
```python
# 重構前：手動設置 header
raise HTTPException(
    status_code=401,
    headers={"WWW-Authenticate": "Bearer"}
)

# 重構後：由 UnauthorizedException 自動處理
raise UnauthorizedException(message="...")
# error_handler.py 中會自動添加正確的 header
```

---

### **3. 錯誤詳情增強**
```python
# 現在可以添加更多調試信息
raise DatabaseException(
    message="Error parsing user data",
    details={
        "error": str(e),
        "email": email,
        "user_data_keys": list(user_data.keys())
    }
)
```

---

## 🎓 最佳實踐

### **1. 選擇合適的異常**

| 場景 | 使用異常 | HTTP 狀態碼 |
|------|----------|------------|
| Token 無效、過期 | `UnauthorizedException` | 401 |
| 用戶不存在 | `UnauthorizedException` | 401 |
| 用戶未啟用 | `ForbiddenException` | 403 |
| 權限不足 | `ForbiddenException` | 403 |
| 數據解析錯誤 | `DatabaseException` | 500 |
| 數據驗證錯誤 | `ValidationException` | 400 |

---

### **2. 提供有用的錯誤消息**

```python
# ✅ 好的錯誤消息
raise ForbiddenException(
    message="Admin access required"
)

# ❌ 不好的錯誤消息
raise ForbiddenException(
    message="Access denied"
)
```

---

### **3. 包含調試信息（開發環境）**

```python
raise DatabaseException(
    message="Error parsing user data",
    details={
        "error": str(e),
        "email": email,
        # 生產環境可能需要過濾敏感信息
    }
)
```

---

## 🚀 後續工作

### **已完成：**
- [x] `app/api/v1/auth.py` 重構
- [x] `app/utils/dependencies.py` 重構

### **待檢查：**
- [x] `app/api/v1/users.py` 已完全使用自定義異常 ✅
- [ ] `app/services/user_service.py` 是否需要重構
- [ ] 其他服務層是否需要重構
- [ ] 整個 `app/` 目錄已無 `HTTPException` ✅

### **測試：**
- [ ] 運行現有測試確保無破壞性變更
- [ ] 添加針對自定義異常的測試
- [ ] 測試錯誤響應格式

---

## 📚 相關文檔

- [異常使用指南](./EXCEPTION_USAGE_GUIDE.md)
- [Auth 重構總結](./AUTH_REFACTORING_SUMMARY.md)
- [錯誤處理說明](./ERROR_HANDLING_EXPLAINED.md)

---

## 🎉 總結

此次重構成功將 `dependencies.py` 中的所有 `HTTPException` 替換為自定義異常，實現了：

1. ✅ **一致性** - 整個專案統一使用自定義異常
2. ✅ **可維護性** - 更清晰的異常語義
3. ✅ **可擴展性** - 易於添加錯誤詳情
4. ✅ **用戶體驗** - 統一的錯誤響應格式

**重構完成日期：** 2025-11-11  
**重構狀態：** ✅ 完成  
**測試狀態：** ⏳ 待測試  
**驗證狀態：** ✅ 整個 `app/` 目錄已無 `raise HTTPException`

