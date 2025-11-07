"""
用戶服務層

處理用戶相關的業務邏輯
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import (
    UserCreate, UserUpdate, UserInDB, UserResponse,
    UserRole, PasswordChange, UserRoleUpdate
)
from app.models.common import PaginationParams, PaginationMeta
from app.utils.security import hash_password, verify_password
from app.utils.helpers import str_to_objectid
from app.config import settings
from app.middleware.error_handler import (
    NotFoundException, ValidationException, DatabaseException
)


class UserService:
    """用戶服務類"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化用戶服務
        
        Args:
            db: MongoDB 數據庫實例
        """
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """
        創建新用戶
        
        Args:
            user_data: 用戶創建數據
            
        Returns:
            UserInDB: 創建的用戶
            
        Raises:
            ValidationException: Email 已存在
            DatabaseException: 數據庫錯誤
        """
        # 檢查 email 是否已存在
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValidationException(
                message="Email already registered",
                details={"email": user_data.email}
            )
        
        # 創建用戶文檔
        user_dict = {
            "email": user_data.email,
            "hashed_password": hash_password(user_data.password),
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "role": settings.DEFAULT_USER_ROLE,
            "is_active": True,
            "is_email_verified": False,
            "addresses": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        try:
            result = await self.collection.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
        except Exception as e:
            raise DatabaseException(
                message="Failed to create user",
                details={"error": str(e)}
            )
        
        # 轉換並返回
        user_dict["id"] = str(user_dict.pop("_id"))
        return UserInDB(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        通過 Email 獲取用戶
        
        Args:
            email: 用戶 email
            
        Returns:
            Optional[UserInDB]: 用戶或 None
        """
        user_data = await self.collection.find_one({"email": email})
        if user_data is None:
            return None
        
        user_data["id"] = str(user_data.pop("_id"))
        return UserInDB(**user_data)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        通過 ID 獲取用戶
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Optional[UserInDB]: 用戶或 None
            
        Raises:
            ValidationException: 無效的用戶 ID
        """
        obj_id = str_to_objectid(user_id)
        if obj_id is None:
            raise ValidationException(
                message="Invalid user ID format",
                details={"user_id": user_id}
            )
        
        user_data = await self.collection.find_one({"_id": obj_id})
        if user_data is None:
            return None
        
        user_data["id"] = str(user_data.pop("_id"))
        return UserInDB(**user_data)
    
    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate
    ) -> Optional[UserInDB]:
        """
        更新用戶信息
        
        Args:
            user_id: 用戶 ID
            user_update: 更新數據
            
        Returns:
            Optional[UserInDB]: 更新後的用戶或 None
            
        Raises:
            ValidationException: 無效的用戶 ID
            DatabaseException: 數據庫錯誤
        """
        obj_id = str_to_objectid(user_id)
        if obj_id is None:
            raise ValidationException(
                message="Invalid user ID format",
                details={"user_id": user_id}
            )
        
        # 只更新提供的字段
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            # 沒有要更新的數據
            return await self.get_user_by_id(user_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": update_data},
                return_document=True
            )
        except Exception as e:
            raise DatabaseException(
                message="Failed to update user",
                details={"error": str(e)}
            )
        
        if result is None:
            return None
        
        result["id"] = str(result.pop("_id"))
        return UserInDB(**result)
    
    async def delete_user(self, user_id: str) -> bool:
        """
        刪除用戶（軟刪除，設置 is_active=False）
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            bool: 是否成功刪除
            
        Raises:
            ValidationException: 無效的用戶 ID
            DatabaseException: 數據庫錯誤
        """
        obj_id = str_to_objectid(user_id)
        if obj_id is None:
            raise ValidationException(
                message="Invalid user ID format",
                details={"user_id": user_id}
            )
        
        try:
            result = await self.collection.update_one(
                {"_id": obj_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseException(
                message="Failed to delete user",
                details={"error": str(e)}
            )
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[UserInDB]:
        """
        認證用戶（驗證 email 和密碼）
        
        Args:
            email: 用戶 email
            password: 明文密碼
            
        Returns:
            Optional[UserInDB]: 認證成功返回用戶，失敗返回 None
        """
        user = await self.get_user_by_email(email)
        if user is None:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def change_password(
        self,
        user_id: str,
        password_change: PasswordChange
    ) -> bool:
        """
        修改用戶密碼
        
        Args:
            user_id: 用戶 ID
            password_change: 密碼修改數據
            
        Returns:
            bool: 是否成功修改
            
        Raises:
            ValidationException: 當前密碼錯誤或無效的用戶 ID
            DatabaseException: 數據庫錯誤
        """
        # 獲取用戶
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(resource="User", resource_id=user_id)
        
        # 驗證當前密碼
        if not verify_password(password_change.current_password, user.hashed_password):
            raise ValidationException(
                message="Current password is incorrect",
                details={}
            )
        
        # 更新密碼
        obj_id = str_to_objectid(user_id)
        try:
            result = await self.collection.update_one(
                {"_id": obj_id},
                {
                    "$set": {
                        "hashed_password": hash_password(password_change.new_password),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseException(
                message="Failed to change password",
                details={"error": str(e)}
            )
    
    async def update_user_role(
        self,
        user_id: str,
        role_update: UserRoleUpdate
    ) -> Optional[UserInDB]:
        """
        更新用戶角色（僅管理員可用）
        
        Args:
            user_id: 用戶 ID
            role_update: 角色更新數據
            
        Returns:
            Optional[UserInDB]: 更新後的用戶或 None
            
        Raises:
            ValidationException: 無效的用戶 ID
            DatabaseException: 數據庫錯誤
        """
        obj_id = str_to_objectid(user_id)
        if obj_id is None:
            raise ValidationException(
                message="Invalid user ID format",
                details={"user_id": user_id}
            )
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": obj_id},
                {
                    "$set": {
                        "role": role_update.role.value,
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
        except Exception as e:
            raise DatabaseException(
                message="Failed to update user role",
                details={"error": str(e)}
            )
        
        if result is None:
            return None
        
        result["id"] = str(result.pop("_id"))
        return UserInDB(**result)
    
    async def get_users(
        self,
        pagination: PaginationParams,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[UserInDB], PaginationMeta]:
        """
        獲取用戶列表（分頁）
        
        Args:
            pagination: 分頁參數
            role: 過濾角色（可選）
            is_active: 過濾活躍狀態（可選）
            
        Returns:
            tuple[List[UserInDB], PaginationMeta]: 用戶列表和分頁信息
        """
        # 構建查詢條件
        query = {}
        if role is not None:
            query["role"] = role.value
        if is_active is not None:
            query["is_active"] = is_active
        
        # 獲取總數
        total = await self.collection.count_documents(query)
        
        # 獲取用戶列表
        cursor = self.collection.find(query).skip(pagination.skip).limit(pagination.per_page)
        users_data = await cursor.to_list(length=pagination.per_page)
        
        # 轉換為模型
        users = []
        for user_data in users_data:
            user_data["id"] = str(user_data.pop("_id"))
            users.append(UserInDB(**user_data))
        
        # 創建分頁信息
        pagination_meta = PaginationMeta.create(
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        return users, pagination_meta
    
    async def user_to_response(self, user: UserInDB) -> UserResponse:
        """
        將 UserInDB 轉換為 UserResponse（移除敏感信息）
        
        Args:
            user: 數據庫用戶模型
            
        Returns:
            UserResponse: API 響應用戶模型
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            addresses=user.addresses,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


async def get_user_service(db: AsyncIOMotorDatabase) -> UserService:
    """
    獲取用戶服務實例（依賴注入）
    
    Args:
        db: MongoDB 數據庫實例
        
    Returns:
        UserService: 用戶服務實例
    """
    return UserService(db)

