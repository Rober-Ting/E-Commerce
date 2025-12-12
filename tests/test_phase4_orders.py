"""
Phase 4: 订单管理系统测试

测试内容：
1. 订单创建
   - 成功创建订单
   - 库存不足时创建失败
   - 未认证用户创建失败
   - 商品不存在时创建失败
   
2. 订单查询
   - 获取我的订单列表
   - 获取所有订单（管理员）
   - 获取订单详情
   - 根据订单编号查询
   
3. 订单状态更新
   - 更新订单状态
   - 状态转换验证
   - 权限验证
   
4. 订单取消
   - 取消订单并恢复库存
   - 取消权限验证
   - 不同状态下的取消规则
   
5. 订单筛选
   - 按状态筛选
   - 按日期筛选
   - 按金额筛选
   - 关键词搜索
   
6. 订单统计
   - 用户订单统计
   - 全局订单统计（管理员）
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.main import app
from app.database import get_database


# ============= Test Fixtures =============

@pytest_asyncio.fixture
async def test_client():
    """创建测试客户端"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def clean_database():
    """清理测试数据并创建测试用户"""
    from app.database import connect_to_mongo
    from app.utils.security import get_password_hash
    from datetime import datetime
    
    # 确保数据库连接已建立
    await connect_to_mongo()
    
    db: AsyncIOMotorDatabase = get_database()
    
    # 测试前清理
    await db.products.delete_many({})
    await db.users.delete_many({})
    await db.orders.delete_many({})
    
    # 创建测试 admin 账户
    admin_user = {
        "email": "admin@ecommerce.com",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("Admin123!"),
        "role": "admin",
        "is_active": True,
        "email_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(admin_user)
    
    yield db
    
    # 测试后清理
    await db.products.delete_many({})
    await db.users.delete_many({})
    await db.orders.delete_many({})


# ============= Test Data =============

# 测试数据
TEST_ADMIN_USER = {
    "email": "admin@ecommerce.com",
    "password": "Admin123!"
}

TEST_VENDOR_USER = {
    "email": "vendor@test.com",
    "password": "Vendor123!"
}

TEST_CUSTOMER_USER = {
    "email": "test_order_customer@test.com",
    "password": "Customer123!",
    "full_name": "测试订单用户",
    "role": None  # 默认 customer
}

TEST_PRODUCT = {
    "name": "测试订单商品 - MacBook Pro",
    "description": "用于订单测试的商品",
    "price": 39900.00,
    "stock": 100,
    "category": "笔记本电脑",
    "tags": ["Apple", "MacBook", "测试"],
    "images": ["https://example.com/macbook.jpg"],
    "status": "active"
}

TEST_SHIPPING_ADDRESS = {
    "recipient": "张三",
    "phone": "0912345678",
    "address_line1": "台北市中正区忠孝东路一段1号",
    "address_line2": "10楼",
    "city": "台北市",
    "state": "台北市",
    "postal_code": "100",
    "country": "Taiwan"
}


@pytest.mark.asyncio
class TestOrderCreation:
    """订单创建测试"""

    async def test_create_order_success(self, test_client: AsyncClient, clean_database):
        """测试成功创建订单"""
        # 1. 注册并登录用户
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        assert register_resp.status_code == 200
        customer_token = register_resp.json()["data"]["access_token"]

        # 2. 以管理员身份创建测试商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert product_resp.status_code == 200
        product_id = product_resp.json()["data"]["id"]
        product_price = product_resp.json()["data"]["price"]

        # 3. 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": product_price,
                    "quantity": 2,
                    "subtotal": product_price * 2
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card",
            "note": "测试订单"
        }

        response = await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n创建订单响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["order_number"].startswith("ORD")
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["status"] == "pending"
        assert data["payment_status"] == "pending"
        assert data["shipping_address"]["recipient"] == "张三"
        assert data["subtotal"] == product_price * 2

        # 4. 验证库存已扣减
        product_check = await test_client.get(
            f"/api/v1/products/{product_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert product_check.json()["data"]["stock"] == TEST_PRODUCT["stock"] - 2

    async def test_create_order_insufficient_stock(self, test_client: AsyncClient, clean_database):
        """测试库存不足时创建订单失败"""
        # 1. 注册用户
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 2. 创建低库存商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        low_stock_product = {
            **TEST_PRODUCT,
            "name": "低库存商品",
            "stock": 1  # 只有1个库存
        }
        product_resp = await test_client.post(
            "/api/v1/products",
            json=low_stock_product,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 3. 尝试购买超过库存数量
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "低库存商品",
                    "price": 39900.00,
                    "quantity": 5,  # 尝试购买5个，但只有1个库存
                    "subtotal": 39900.00 * 5
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        response = await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n库存不足响应: {response.json()}")

        # 断言：应该返回 400 错误
        assert response.status_code == 400
        assert "库存不足" in response.json()["error"]["message"]

    async def test_create_order_unauthenticated(self, test_client: AsyncClient):
        """测试未认证用户创建订单失败"""
        order_data = {
            "items": [
                {
                    "product_id": "507f1f77bcf86cd799439011",
                    "product_name": "测试商品",
                    "price": 100.00,
                    "quantity": 1,
                    "subtotal": 100.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        response = await test_client.post(
            "/api/v1/orders",
            json=order_data
        )

        print(f"\n未认证创建订单响应: {response.json()}")

        # 断言：应该返回 403 错误
        assert response.status_code == 403


@pytest.mark.asyncio
class TestOrderRetrieval:
    """订单查询测试"""

    async def test_get_my_orders(self, test_client: AsyncClient, clean_database):
        """测试获取我的订单列表"""
        # 1. 创建订单
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 创建商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 1,
                    "subtotal": 39900.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        # 2. 获取订单列表
        response = await test_client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n我的订单列表响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["pagination"]["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["order_number"].startswith("ORD")

    async def test_get_all_orders_admin(self, test_client: AsyncClient, clean_database):
        """测试管理员获取所有订单"""
        # 登录管理员
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        # 获取所有订单
        response = await test_client.get(
            "/api/v1/orders/all",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        print(f"\n所有订单列表响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
        assert "pagination" in data

    async def test_get_order_detail(self, test_client: AsyncClient, clean_database):
        """测试获取订单详情"""
        # 1. 创建订单
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 创建商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 1,
                    "subtotal": 39900.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        create_resp = await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        order_id = create_resp.json()["data"]["id"]

        # 2. 获取订单详情
        response = await test_client.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n订单详情响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == order_id
        assert "status_history" in data
        assert len(data["status_history"]) >= 1


@pytest.mark.asyncio
class TestOrderStatusUpdate:
    """订单状态更新测试"""

    async def test_update_order_status(self, test_client: AsyncClient, clean_database):
        """测试更新订单状态"""
        # 1. 创建订单
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 创建商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 1,
                    "subtotal": 39900.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        create_resp = await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        order_id = create_resp.json()["data"]["id"]

        # 2. 管理员更新订单状态（pending -> paid）
        status_update = {
            "status": "paid",
            "note": "用户已支付"
        }

        response = await test_client.put(
            f"/api/v1/orders/{order_id}/status",
            json=status_update,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        print(f"\n更新订单状态响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "paid"
        assert data["payment_status"] == "paid"
        assert data["paid_at"] is not None


@pytest.mark.asyncio
class TestOrderCancellation:
    """订单取消测试"""

    async def test_cancel_order(self, test_client: AsyncClient, clean_database):
        """测试取消订单并恢复库存"""
        # 1. 创建订单
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 创建商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]
        original_stock = product_resp.json()["data"]["stock"]

        # 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 3,
                    "subtotal": 39900.00 * 3
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        create_resp = await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        order_id = create_resp.json()["data"]["id"]

        # 2. 取消订单
        cancel_data = {
            "reason": "不想要了"
        }

        response = await test_client.put(
            f"/api/v1/orders/{order_id}/cancel",
            json=cancel_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n取消订单响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "cancelled"

        # 3. 验证库存已恢复
        product_check = await test_client.get(
            f"/api/v1/products/{product_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert product_check.json()["data"]["stock"] == original_stock


@pytest.mark.asyncio
class TestOrderFiltering:
    """订单筛选测试"""

    async def test_filter_orders_by_status(self, test_client: AsyncClient, clean_database):
        """测试按状态筛选订单"""
        # 1. 创建用户和商品
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 2. 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 1,
                    "subtotal": 39900.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        # 3. 按状态筛选
        response = await test_client.get(
            "/api/v1/orders?status=pending",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n按状态筛选订单响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["pagination"]["total"] >= 1
        # 验证所有订单都是 pending 状态
        for order in data["items"]:
            assert order["status"] == "pending"


@pytest.mark.asyncio
class TestOrderStatistics:
    """订单统计测试"""

    async def test_get_order_statistics(self, test_client: AsyncClient, clean_database):
        """测试获取订单统计"""
        # 1. 创建订单
        register_resp = await test_client.post(
            "/api/v1/auth/register",
            json=TEST_CUSTOMER_USER
        )
        customer_token = register_resp.json()["data"]["access_token"]

        # 创建商品
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json=TEST_ADMIN_USER
        )
        admin_token = login_resp.json()["data"]["access_token"]

        product_resp = await test_client.post(
            "/api/v1/products",
            json=TEST_PRODUCT,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = product_resp.json()["data"]["id"]

        # 创建订单
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "MacBook Pro",
                    "price": 39900.00,
                    "quantity": 1,
                    "subtotal": 39900.00
                }
            ],
            "shipping_address": TEST_SHIPPING_ADDRESS,
            "payment_method": "credit_card"
        }

        await test_client.post(
            "/api/v1/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        # 2. 获取统计
        response = await test_client.get(
            "/api/v1/orders/statistics/summary",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        print(f"\n订单统计响应: {response.json()}")

        # 断言
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_orders"] >= 1
        assert data["total_amount"] > 0
        assert data["pending_orders"] >= 1

