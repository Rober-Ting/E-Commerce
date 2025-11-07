"""
安全工具函數模組

提供密碼加密、JWT Token 生成和驗證等安全相關功能
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密碼
    
    Args:
        password: 明文密碼
        
    Returns:
        str: 哈希後的密碼
        
    Note:
        bcrypt 限制密碼最多 72 字節，如果超過會自動截斷
        
    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> print(hashed)
        $2b$12$...
    """
    # bcrypt 限制：最多 72 字節
    # 如果密碼超過 72 字節，截斷它
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼是否匹配
    
    Args:
        plain_password: 明文密碼
        hashed_password: 哈希後的密碼
        
    Returns:
        bool: 密碼是否匹配
        
    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPass", hashed)
        False
    """
    # bcrypt 限制：最多 72 字節，需要與 hash_password 保持一致
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    創建 JWT Access Token
    
    Args:
        data: 要編碼到 token 中的數據（通常包含 sub, role 等）
        expires_delta: token 過期時間，默認使用配置中的時間
        
    Returns:
        str: JWT token 字符串
        
    Example:
        >>> token = create_access_token({"sub": "user@example.com", "role": "customer"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()
    
    # 設置過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # 添加過期時間到 payload
    to_encode.update({"exp": expire})
    
    # 編碼 JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解碼並驗證 JWT Token
    
    Args:
        token: JWT token 字符串
        
    Returns:
        Optional[Dict[str, Any]]: 解碼後的 payload，如果 token 無效則返回 None
        
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> print(payload['sub'])
        user@example.com
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    驗證密碼強度
    
    Args:
        password: 要驗證的密碼
        
    Returns:
        tuple[bool, str]: (是否有效, 錯誤消息)
        
    密碼要求:
    - 最少 8 個字符
    - 包含至少一個大寫字母
    - 包含至少一個小寫字母
    - 包含至少一個數字
    
    Example:
        >>> validate_password_strength("Pass123!")
        (True, "")
        >>> validate_password_strength("weak")
        (False, "Password must be at least 8 characters long")
    """
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, ""


def create_token_response(access_token: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    創建標準的 token 響應格式
    
    Args:
        access_token: JWT token
        user_data: 用戶數據
        
    Returns:
        Dict[str, Any]: 標準的 token 響應
        
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> user_data = {"id": "123", "email": "user@example.com"}
        >>> response = create_token_response(token, user_data)
        >>> print(response['token_type'])
        bearer
    """
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 轉換為秒
        "user": user_data
    }

