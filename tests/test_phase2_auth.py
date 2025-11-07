"""
Phase 2 認證與用戶管理 - 單元測試

測試用戶註冊、登入、認證和用戶管理功能
"""

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from app.main import app
from app.database import connect_to_mongo, close_mongo_connection, db
from app.models.user import UserRole


@pytest_asyncio.fixture
async def test_client():
    """創建測試客戶端"""
    # 確保數據庫連接已建立
    await connect_to_mongo()
    
    # 創建測試客戶端
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # 測試結束後關閉連接
    await close_mongo_connection()


@pytest_asyncio.fixture
async def clean_database():
    """清理測試數據庫"""
    # 確保數據庫連接已建立
    await connect_to_mongo()
    
    # 在測試前清理 users 集合
    if db.db is not None:
        await db.db.users.delete_many({})
    
    yield
    
    # 在測試後清理 users 集合
    if db.db is not None:
        await db.db.users.delete_many({})


class TestUserAuthentication:
    """測試用戶認證功能"""
    
    @pytest.mark.asyncio
    async def test_user_registration_success(self, test_client, clean_database):
        """測試用戶註冊成功"""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "測試用戶",
                "phone": "0912345678"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["user"]["email"] == "newuser@example.com"
        assert data["data"]["user"]["full_name"] == "測試用戶"
        assert data["data"]["user"]["role"] == "customer"
    
    @pytest.mark.asyncio
    async def test_user_registration_duplicate_email(self, test_client, clean_database):
        """測試重複 email 註冊失敗"""
        # 先註冊一個用戶
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "SecurePass123!",
                "full_name": "現有用戶"
            }
        )
        
        # 嘗試用相同 email 再次註冊
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "AnotherPass123!",
                "full_name": "另一個用戶"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.asyncio
    async def test_user_registration_weak_password(self, test_client, clean_database):
        """測試弱密碼註冊失敗"""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "weakpass@example.com",
                "password": "weak",  # 密碼太弱
                "full_name": "弱密碼用戶"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_user_login_success(self, test_client, clean_database):
        """測試用戶登入成功"""
        # 先註冊用戶
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "loginuser@example.com",
                "password": "LoginPass123!",
                "full_name": "登入用戶"
            }
        )
        
        # 嘗試登入
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "loginuser@example.com",
                "password": "LoginPass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == "loginuser@example.com"
    
    @pytest.mark.asyncio
    async def test_user_login_wrong_password(self, test_client, clean_database):
        """測試錯誤密碼登入失敗"""
        # 先註冊用戶
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "CorrectPass123!",
                "full_name": "測試用戶"
            }
        )
        
        # 嘗試用錯誤密碼登入
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPass123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_user_login_nonexistent_email(self, test_client, clean_database):
        """測試不存在的 email 登入失敗"""
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    """測試受保護的端點"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_info(self, test_client, clean_database):
        """測試獲取當前用戶信息"""
        # 註冊並登入
        register_response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "protecteduser@example.com",
                "password": "ProtectedPass123!",
                "full_name": "受保護用戶"
            }
        )
        
        token = register_response.json()["data"]["access_token"]
        
        # 使用 token 獲取用戶信息
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "protecteduser@example.com"
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, test_client, clean_database):
        """測試無 token 訪問受保護端點失敗"""
        response = await test_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, test_client, clean_database):
        """測試無效 token 訪問失敗"""
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_update_current_user(self, test_client, clean_database):
        """測試更新當前用戶信息"""
        # 註冊並登入
        register_response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "updateuser@example.com",
                "password": "UpdatePass123!",
                "full_name": "原始名稱"
            }
        )
        
        token = register_response.json()["data"]["access_token"]
        
        # 更新用戶信息
        response = await test_client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "full_name": "更新後的名稱",
                "phone": "0987654321"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["full_name"] == "更新後的名稱"
        assert data["data"]["phone"] == "0987654321"
    
    @pytest.mark.asyncio
    async def test_change_password(self, test_client, clean_database):
        """測試修改密碼"""
        # 註冊並登入
        register_response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "changepass@example.com",
                "password": "OldPass123!",
                "full_name": "修改密碼用戶"
            }
        )
        
        token = register_response.json()["data"]["access_token"]
        
        # 修改密碼
        response = await test_client.put(
            "/api/v1/auth/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "OldPass123!",
                "new_password": "NewPass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # 用新密碼登入驗證
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "changepass@example.com",
                "password": "NewPass123!"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK


class TestAdminEndpoints:
    """測試管理員端點"""
    
    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, test_client, clean_database):
        """測試管理員查看用戶列表"""
        # 創建管理員
        from app.utils.security import hash_password
        from app.database import db
        
        await db.db.users.insert_one({
            "email": "admin@example.com",
            "hashed_password": hash_password("AdminPass123!"),
            "full_name": "管理員",
            "role": "admin",
            "is_active": True,
            "addresses": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # 管理員登入
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        
        admin_token = login_response.json()["data"]["access_token"]
        
        # 查看用戶列表
        response = await test_client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
    
    @pytest.mark.asyncio
    async def test_list_users_as_customer_forbidden(self, test_client, clean_database):
        """測試普通用戶無法查看用戶列表"""
        # 註冊普通用戶
        register_response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "customer@example.com",
                "password": "CustomerPass123!",
                "full_name": "普通用戶"
            }
        )
        
        customer_token = register_response.json()["data"]["access_token"]
        
        # 嘗試查看用戶列表
        response = await test_client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_imports():
    """測試所有模組可以正確導入"""
    from app.models import user
    from app.services import user_service
    from app.utils import security, dependencies
    from app.api.v1 import auth, users
    
    assert user is not None
    assert user_service is not None
    assert security is not None
    assert dependencies is not None
    assert auth is not None
    assert users is not None


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v"])

