"""
FastAPI 依賴注入函數

提供認證、權限驗證等依賴
"""

from typing import Optional
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

from app.utils.security import decode_access_token
from app.models.user import UserInDB, UserRole
from app.database import get_database
from app.middleware.error_handler import (
    UnauthorizedException,
    ForbiddenException,
    DatabaseException
)

# HTTP Bearer 認證方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    從 JWT Token 獲取當前用戶
    
    Args:
        credentials: HTTP Authorization Bearer Token
        
    Returns:
        UserInDB: 當前用戶信息
        
    Raises:
        UnauthorizedException: Token 無效或用戶不存在
        DatabaseException: 數據解析錯誤
        
    Example:
        @app.get("/protected")
        async def protected_route(current_user: UserInDB = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    token = credentials.credentials
    
    # 解碼 Token
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException(
            message="Could not validate credentials"
        )
    
    # 獲取用戶 email（sub 是 JWT 標準字段，用於存儲用戶標識）
    email: str = payload.get("sub")
    if email is None:
        raise UnauthorizedException(
            message="Could not validate credentials"
        )
    
    # 從數據庫獲取用戶
    database = get_database()  # 不需要 await，這是普通函數
    user_data = await database.users.find_one({"email": email})
    
    if user_data is None:
        raise UnauthorizedException(
            message="User not found"
        )
    
    # 將 _id 轉換為 id
    user_data["id"] = str(user_data.pop("_id"))
    
    # 轉換為 UserInDB 模型
    try:
        user = UserInDB(**user_data)
    except Exception as e:
        raise DatabaseException(
            message="Error parsing user data",
            details={"error": str(e), "email": email}
        )
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    獲取當前活躍用戶（必須 is_active=True）
    
    Args:
        current_user: 當前用戶
        
    Returns:
        UserInDB: 當前活躍用戶
        
    Raises:
        ForbiddenException: 用戶未啟用
        
    Example:
        @app.get("/protected")
        async def protected_route(current_user: UserInDB = Depends(get_current_active_user)):
            return {"user_id": current_user.id}
    """
    if not current_user.is_active:
        raise ForbiddenException(
            message="Inactive user"
        )
    return current_user


async def require_role(
    required_role: UserRole,
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    要求特定角色權限
    
    Args:
        required_role: 需要的角色
        current_user: 當前用戶
        
    Returns:
        UserInDB: 當前用戶（如果有權限）
        
    Raises:
        ForbiddenException: 權限不足
        
    Example:
        @app.get("/admin")
        async def admin_route(
            current_user: UserInDB = Depends(lambda: require_role(UserRole.ADMIN))
        ):
            return {"admin_user": current_user.email}
    """
    if current_user.role != required_role:
        raise ForbiddenException(
            message=f"Requires {required_role} role"
        )
    return current_user


def require_admin():
    """
    要求管理員權限的依賴
    
    Returns:
        Depends: FastAPI 依賴函數
        
    Example:
        @app.delete("/users/{user_id}")
        async def delete_user(
            user_id: str,
            current_user: UserInDB = Depends(require_admin())
        ):
            # 只有管理員可以訪問
            pass
    """
    async def admin_dependency(
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenException(
                message="Admin access required"
            )
        return current_user
    
    return admin_dependency


def require_vendor_or_admin():
    """
    要求店家或管理員權限的依賴
    
    Returns:
        Depends: FastAPI 依賴函數
        
    Example:
        @app.post("/products")
        async def create_product(
            product_data: dict,
            current_user: UserInDB = Depends(require_vendor_or_admin())
        ):
            # 店家或管理員可以創建商品
            pass
    """
    async def vendor_or_admin_dependency(
        current_user: UserInDB = Depends(get_current_active_user)
    ) -> UserInDB:
        if current_user.role not in [UserRole.VENDOR, UserRole.ADMIN]:
            raise ForbiddenException(
                message="Vendor or admin access required"
            )
        return current_user
    
    return vendor_or_admin_dependency


def optional_user() -> Optional[UserInDB]:
    """
    可選的用戶認證（用於既可以匿名也可以認證訪問的端點）
    
    Returns:
        Optional[UserInDB]: 當前用戶或 None
        
    Example:
        @app.get("/products")
        async def list_products(
            current_user: Optional[UserInDB] = Depends(optional_user())
        ):
            # 匿名和認證用戶都可以訪問
            if current_user:
                # 返回個性化的商品列表
                pass
            else:
                # 返回通用商品列表
                pass
    """
    async def optional_user_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        )
    ) -> Optional[UserInDB]:
        if credentials is None:
            return None
        
        try:
            token = credentials.credentials
            payload = decode_access_token(token)
            if payload is None:
                return None
            
            email = payload.get("sub")
            if email is None:
                return None
            
            database = get_database()  # 不需要 await
            user_data = await database.users.find_one({"email": email})
            
            if user_data is None:
                return None
            
            user_data["id"] = str(user_data.pop("_id"))
            user = UserInDB(**user_data)
            
            return user if user.is_active else None
        except Exception:
            return None
    
    return optional_user_dependency

