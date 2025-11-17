"""
用戶管理 API 端點

提供用戶管理功能（僅管理員可訪問）
"""

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.models.user import (
    UserResponse, UserInDB, UserRole,
    UserRoleUpdate, UserUpdate
)
from app.models.common import (
    ResponseModel, PaginatedResponse, PaginatedData,
    PaginationParams, success_response, paginated_response
)
from app.services.user_service import UserService
from app.utils.dependencies import require_admin, get_current_active_user
from app.database import get_database
from app.middleware.error_handler import NotFoundException, DatabaseException
from app.utils.logging_config import get_logger

# 創建路由器
router = APIRouter(prefix="/users", tags=["User Management"])
logger = get_logger(__name__)


@router.get("", response_model=ResponseModel[PaginatedData[UserResponse]])
async def list_users(
    page: int = Query(1, ge=1, description="頁碼"),
    per_page: int = Query(20, ge=1, le=100, description="每頁數量"),
    role: Optional[UserRole] = Query(None, description="過濾角色"),
    is_active: Optional[bool] = Query(None, description="過濾活躍狀態"),
    current_user: UserInDB = Depends(require_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    獲取用戶列表（分頁）
    
    **需要管理員權限**
    
    - **page**: 頁碼（從1開始）
    - **per_page**: 每頁數量（1-100）
    - **role**: 過濾角色（可選）: admin, customer, vendor
    - **is_active**: 過濾活躍狀態（可選）: true/false
    
    **Returns**: 用戶列表和分頁信息
    """
    logger.info(
        f"管理員查詢用戶列表: admin_id={current_user.id}, "
        f"page={page}, per_page={per_page}, role={role}, is_active={is_active}"
    )
    
    user_service = UserService(db)
    pagination = PaginationParams(page=page, per_page=per_page)
    
    # 獲取用戶列表
    users, pagination_meta = await user_service.get_users(
        pagination=pagination,
        role=role,
        is_active=is_active
    )
    
    # 轉換為響應模型
    user_responses = [
        await user_service.user_to_response(user) for user in users
    ]
    
    logger.info(f"返回 {len(user_responses)} 個用戶，總共 {pagination_meta.total} 個")
    
    return paginated_response(
        items=user_responses,
        page=pagination.page,
        per_page=pagination.per_page,
        total=pagination_meta.total,
        message="Users retrieved successfully"
    )


@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
async def get_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    獲取特定用戶信息
    
    **權限**:
    - 用戶可以查看自己的信息
    - 管理員可以查看任何用戶的信息
    
    **Returns**: 用戶詳細信息
    """
    logger.info(f"查詢用戶信息: target_user_id={user_id}, requester_id={current_user.id}")
    
    # 檢查權限：用戶只能查看自己的信息，除非是管理員
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        logger.warning(
            f"權限不足: user_id={current_user.id} 嘗試查看 target_user_id={user_id}"
        )
        raise NotFoundException(resource="User", resource_id=user_id)
    
    user_service = UserService(db)
    
    # 獲取用戶
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        logger.warning(f"用戶不存在: user_id={user_id}")
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(user)
    
    logger.info(f"用戶信息查詢成功: user_id={user_id}")
    return success_response(
        data=user_response,
        message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=ResponseModel[UserResponse])
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(require_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    更新用戶信息
    
    **需要管理員權限**
    
    - **full_name**: 完整姓名（可選）
    - **phone**: 聯絡電話（可選）
    - **addresses**: 收貨地址列表（可選）
    
    **Returns**: 更新後的用戶信息
    """
    logger.info(f"管理員更新用戶: admin_id={current_user.id}, target_user_id={user_id}")
    
    user_service = UserService(db)
    
    # 更新用戶
    updated_user = await user_service.update_user(user_id, user_update)
    if updated_user is None:
        logger.warning(f"用戶不存在: user_id={user_id}")
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(updated_user)
    
    logger.info(f"用戶更新成功: user_id={user_id}")
    return success_response(
        data=user_response,
        message="User updated successfully"
    )


@router.delete("/{user_id}", response_model=ResponseModel[dict])
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(require_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    刪除用戶（軟刪除）
    
    **需要管理員權限**
    
    將用戶的 is_active 設置為 False，不會真正從數據庫中刪除
    
    **Returns**: 刪除結果
    """
    logger.info(f"管理員刪除用戶: admin_id={current_user.id}, target_user_id={user_id}")
    
    # 防止管理員刪除自己
    if current_user.id == user_id:
        logger.warning(f"管理員嘗試刪除自己: admin_id={current_user.id}")
        from app.middleware.error_handler import ValidationException
        raise ValidationException(
            message="Cannot delete your own account",
            details={"user_id": user_id}
        )
    
    user_service = UserService(db)
    
    # 檢查用戶是否存在
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        logger.warning(f"用戶不存在: user_id={user_id}")
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # 刪除用戶（軟刪除）
    success = await user_service.delete_user(user_id)
    
    if not success:
        logger.error(f"用戶刪除失敗: user_id={user_id}")
        raise DatabaseException(
            message="Failed to delete user",
            details={"user_id": user_id}
        )
    
    logger.info(f"用戶刪除成功: user_id={user_id}")
    return success_response(
        data={"deleted": True, "user_id": user_id},
        message="User deleted successfully"
    )


@router.put("/{user_id}/role", response_model=ResponseModel[UserResponse])
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: UserInDB = Depends(require_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    更新用戶角色
    
    **需要管理員權限**
    
    - **role**: 新的角色（admin, customer, vendor）
    
    **Returns**: 更新後的用戶信息
    """
    logger.info(
        f"管理員更新用戶角色: admin_id={current_user.id}, "
        f"target_user_id={user_id}, new_role={role_update.role}"
    )
    
    # 防止管理員修改自己的角色
    if current_user.id == user_id:
        logger.warning(f"管理員嘗試修改自己的角色: admin_id={current_user.id}")
        from app.middleware.error_handler import ValidationException
        raise ValidationException(
            message="Cannot change your own role",
            details={"user_id": user_id}
        )
    
    user_service = UserService(db)
    
    # 更新角色
    updated_user = await user_service.update_user_role(user_id, role_update)
    if updated_user is None:
        logger.warning(f"用戶不存在: user_id={user_id}")
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(updated_user)
    
    logger.info(f"用戶角色更新成功: user_id={user_id}, new_role={role_update.role}")
    return success_response(
        data=user_response,
        message="User role updated successfully"
    )


@router.post("/{user_id}/activate", response_model=ResponseModel[UserResponse])
async def activate_user(
    user_id: str,
    current_user: UserInDB = Depends(require_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    啟用用戶
    
    **需要管理員權限**
    
    將被刪除（is_active=False）的用戶重新啟用
    
    **Returns**: 啟用後的用戶信息
    """
    logger.info(f"管理員啟用用戶: admin_id={current_user.id}, target_user_id={user_id}")
    
    user_service = UserService(db)
    
    # 更新用戶狀態
    from app.models.user import UserUpdate
    user_update = UserUpdate()
    user_update.full_name = None  # 不修改其他字段
    
    # 直接更新 is_active 狀態
    from bson import ObjectId
    obj_id = ObjectId(user_id)
    await db.users.update_one(
        {"_id": obj_id},
        {"$set": {"is_active": True}}
    )
    
    # 獲取更新後的用戶
    updated_user = await user_service.get_user_by_id(user_id)
    if updated_user is None:
        logger.warning(f"用戶不存在: user_id={user_id}")
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # 轉換為響應模型
    user_response = await user_service.user_to_response(updated_user)
    
    logger.info(f"用戶啟用成功: user_id={user_id}")
    return success_response(
        data=user_response,
        message="User activated successfully"
    )

