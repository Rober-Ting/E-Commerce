"""
認證 API 端點

處理用戶註冊、登入、獲取用戶信息等認證相關操作
"""

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    PasswordChange, TokenResponse
)
from app.models.common import ResponseModel, success_response
from app.services.user_service import UserService, get_user_service
from app.utils.dependencies import get_current_active_user, get_current_user
from app.utils.security import create_access_token, create_token_response
from app.models.user import UserInDB
from app.database import get_database
from app.middleware.error_handler import (
    ValidationException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    DatabaseException
)
from app.utils.logging_config import get_logger

# 創建路由器
router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=ResponseModel[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    用戶註冊
    
    創建新用戶賬戶並返回 JWT Token
    
    - **email**: 唯一的電子郵件地址
    - **password**: 密碼（至少8個字符，包含大小寫字母和數字）
    - **full_name**: 完整姓名
    - **phone**: 聯絡電話（可選）
    
    **Returns**: 新用戶信息和 JWT Token
    """
    logger.info(f"註冊請求: email={user_data.email}")
    
    user_service = UserService(db)
    
    # 創建用戶
    user = await user_service.create_user(user_data)
    logger.info(f"用戶創建成功: user_id={user.id}, email={user.email}")
    
    # 創建 Token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(user)
    
    # 創建 Token 響應
    token_data = create_token_response(access_token, user_response.model_dump())
    
    logger.info(f"註冊成功: user_id={user.id}")
    return success_response(
        data=token_data,
        message="User registered successfully"
    )


@router.post("/login", response_model=ResponseModel[TokenResponse])
async def login(
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    用戶登入
    
    使用 email 和密碼進行認證，返回 JWT Token
    
    - **email**: 電子郵件地址
    - **password**: 密碼
    
    **Returns**: 用戶信息和 JWT Token
    """
    logger.info(f"登入請求: email={credentials.email}")
    
    user_service = UserService(db)
    
    # 認證用戶
    user = await user_service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if user is None:
        logger.warning(f"登入失敗: 無效的憑證 email={credentials.email}")
        raise UnauthorizedException(
            message="Incorrect email or password"
        )
    
    if not user.is_active:
        logger.warning(f"登入失敗: 用戶未啟用 user_id={user.id}")
        raise ForbiddenException(
            message="User account is not active"
        )
    
    # 創建 Token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(user)
    
    # 創建 Token 響應
    token_data = create_token_response(access_token, user_response.model_dump())
    
    logger.info(f"登入成功: user_id={user.id}, email={user.email}")
    return success_response(
        data=token_data,
        message="Login successful"
    )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    獲取當前用戶信息
    
    需要 JWT Token 認證
    
    **Returns**: 當前用戶的詳細信息
    """
    logger.debug(f"獲取當前用戶信息: user_id={current_user.id}")
    
    user_service = UserService(db)
    user_response = await user_service.user_to_response(current_user)
    
    return success_response(
        data=user_response,
        message="User information retrieved successfully"
    )


@router.put("/me", response_model=ResponseModel[UserResponse])
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    更新當前用戶信息
    
    需要 JWT Token 認證
    
    - **full_name**: 完整姓名（可選）
    - **phone**: 聯絡電話（可選）
    - **addresses**: 收貨地址列表（可選）
    
    **Returns**: 更新後的用戶信息
    """
    logger.info(f"更新用戶信息請求: user_id={current_user.id}")
    
    user_service = UserService(db)
    
    # 更新用戶
    updated_user = await user_service.update_user(current_user.id, user_update)
    
    if updated_user is None:
        logger.error(f"更新失敗: 用戶不存在 user_id={current_user.id}")
        raise NotFoundException(resource="User", resource_id=current_user.id)
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(updated_user)
    
    logger.info(f"用戶信息更新成功: user_id={current_user.id}")
    return success_response(
        data=user_response,
        message="User information updated successfully"
    )


@router.put("/password", response_model=ResponseModel[dict])
async def change_password(
    password_change: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    修改當前用戶密碼
    
    需要 JWT Token 認證
    
    - **current_password**: 當前密碼
    - **new_password**: 新密碼（至少8個字符，包含大小寫字母和數字）
    
    **Returns**: 成功消息
    """
    logger.info(f"修改密碼請求: user_id={current_user.id}")
    
    user_service = UserService(db)
    
    # 修改密碼
    success = await user_service.change_password(current_user.id, password_change)
    
    if not success:
        logger.error(f"密碼修改失敗: user_id={current_user.id}")
        raise DatabaseException(
            message="Failed to change password",
            details={"user_id": current_user.id}
        )
    
    logger.info(f"密碼修改成功: user_id={current_user.id}")
    return success_response(
        data={"changed": True},
        message="Password changed successfully"
    )


@router.post("/refresh", response_model=ResponseModel[TokenResponse])
async def refresh_token(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    刷新 JWT Token
    
    使用當前的 JWT Token 獲取新的 Token
    
    **Returns**: 新的 JWT Token
    """
    logger.info(f"刷新 Token 請求: user_id={current_user.id}")
    
    # 創建新 Token
    access_token = create_access_token(
        data={"sub": current_user.email, "role": current_user.role.value}
    )
    
    user_service = UserService(db)
    user_response = await user_service.user_to_response(current_user)
    
    # 創建 Token 響應
    token_data = create_token_response(access_token, user_response.model_dump())
    
    logger.info(f"Token 刷新成功: user_id={current_user.id}")
    return success_response(
        data=token_data,
        message="Token refreshed successfully"
    )

