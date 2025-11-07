"""
用戶數據模型

定義用戶相關的 Pydantic 模型，用於請求驗證和響應序列化
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """用戶角色枚舉"""
    ADMIN = "admin"
    CUSTOMER = "customer"
    VENDOR = "vendor"


class Address(BaseModel):
    """地址模型"""
    recipient_name: str = Field(..., min_length=1, max_length=100, description="收件人姓名")
    phone: str = Field(..., pattern=r"^09\d{8}$", description="聯絡電話（台灣手機格式）")
    city: str = Field(..., min_length=1, max_length=50, description="城市")
    district: str = Field(..., min_length=1, max_length=50, description="區域")
    street: str = Field(..., min_length=1, max_length=200, description="街道地址")
    postal_code: str = Field(..., pattern=r"^\d{3,5}$", description="郵遞區號")
    is_default: bool = Field(default=False, description="是否為預設地址")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient_name": "張三",
                "phone": "0912345678",
                "city": "台北市",
                "district": "信義區",
                "street": "信義路五段7號",
                "postal_code": "110",
                "is_default": True
            }
        }


class UserBase(BaseModel):
    """用戶基礎模型"""
    email: EmailStr = Field(..., description="電子郵件地址")
    full_name: str = Field(..., min_length=1, max_length=100, description="完整姓名")
    phone: Optional[str] = Field(None, pattern=r"^09\d{8}$", description="聯絡電話")


class UserCreate(UserBase):
    """用戶創建（註冊）請求模型"""
    password: str = Field(..., min_length=8, max_length=100, description="密碼（至少8個字符）")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """驗證密碼強度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "張三",
                "phone": "0912345678",
                "password": "SecurePass123!"
            }
        }


class UserLogin(BaseModel):
    """用戶登入請求模型"""
    email: EmailStr = Field(..., description="電子郵件地址")
    password: str = Field(..., description="密碼")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserUpdate(BaseModel):
    """用戶更新請求模型"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^09\d{8}$")
    addresses: Optional[List[Address]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "張三豐",
                "phone": "0987654321"
            }
        }


class PasswordChange(BaseModel):
    """密碼修改請求模型"""
    current_password: str = Field(..., description="當前密碼")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密碼")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """驗證新密碼強度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewPass123!"
            }
        }


class UserResponse(UserBase):
    """用戶響應模型（不包含敏感信息）"""
    id: str = Field(..., description="用戶 ID")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="用戶角色")
    is_active: bool = Field(default=True, description="是否啟用")
    addresses: List[Address] = Field(default_factory=list, description="收貨地址列表")
    created_at: datetime = Field(..., description="創建時間")
    updated_at: datetime = Field(..., description="更新時間")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "6543210abcdef123456789",
                "email": "user@example.com",
                "full_name": "張三",
                "phone": "0912345678",
                "role": "customer",
                "is_active": True,
                "addresses": [],
                "created_at": "2025-11-07T10:00:00Z",
                "updated_at": "2025-11-07T10:00:00Z"
            }
        }


class UserInDB(UserBase):
    """用戶數據庫模型（包含所有字段）"""
    id: Optional[str] = None
    hashed_password: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    is_email_verified: bool = False
    addresses: List[Address] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # 允許從 MongoDB 文檔創建模型
        arbitrary_types_allowed = True


class TokenResponse(BaseModel):
    """Token 響應模型"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    expires_in: int = Field(..., description="Token 過期時間（秒）")
    user: UserResponse = Field(..., description="用戶信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "6543210abcdef123456789",
                    "email": "user@example.com",
                    "full_name": "張三",
                    "role": "customer"
                }
            }
        }


class UserRoleUpdate(BaseModel):
    """用戶角色更新模型（僅管理員可用）"""
    role: UserRole = Field(..., description="新的用戶角色")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "vendor"
            }
        }

