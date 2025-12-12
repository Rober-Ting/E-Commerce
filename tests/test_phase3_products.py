"""
PHASE 3 商品管理功能测试

测试商品的 CRUD 操作、搜索、筛选、权限控制等功能
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.main import app
from app.database import get_database


@pytest_asyncio.fixture
async def test_client():
    """创建测试客户端"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def clean_database():
    """清理测试数据"""
    db: AsyncIOMotorDatabase = get_database()
    
    # 测试前清理
    await db.products.delete_many({})
    await db.users.delete_many({})
    
    yield db
    
    # 测试后清理
    await db.products.delete_many({})
    await db.users.delete_many({})


@pytest_asyncio.fixture
async def admin_token(test_client: AsyncClient, clean_database):
    """创建管理员并获取 Token"""
    # 注册管理员
    register_data = {
        "email": "admin@test.com",
        "password": "Admin123!",
        "full_name": "Test Admin",
        "phone": "1234567890"
    }
    
    response = await test_client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    # 手动将用户提升为管理员
    db = clean_database
    await db.users.update_one(
        {"email": "admin@test.com"},
        {"$set": {"role": "admin"}}
    )
    
    # 登录获取 Token
    login_data = {
        "email": "admin@test.com",
        "password": "Admin123!"
    }
    
    response = await test_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    
    return data["data"]["access_token"]


@pytest_asyncio.fixture
async def customer_token(test_client: AsyncClient, clean_database):
    """创建普通用户并获取 Token"""
    register_data = {
        "email": "customer@test.com",
        "password": "Customer123!",
        "full_name": "Test Customer",
        "phone": "0987654321"
    }
    
    response = await test_client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    # 登录获取 Token
    login_data = {
        "email": "customer@test.com",
        "password": "Customer123!"
    }
    
    response = await test_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    
    return data["data"]["access_token"]


class TestProductCreation:
    """测试商品创建功能"""
    
    @pytest.mark.asyncio
    async def test_create_product_as_admin(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试管理员创建商品"""
        product_data = {
            "name": "MacBook Pro 14 吋 M3",
            "description": "全新 Apple M3 晶片",
            "price": 59900.00,
            "stock": 10,
            "category": "筆記型電腦",
            "tags": ["Apple", "MacBook", "M3"],
            "images": ["https://example.com/macbook.jpg"],
            "attributes": {
                "color": "太空灰",
                "processor": "M3"
            }
        }
        
        response = await test_client.post(
            "/api/v1/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["name"] == product_data["name"]
        assert data["data"]["price"] == product_data["price"]
        assert "id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_product_as_customer(
        self,
        test_client: AsyncClient,
        customer_token: str
    ):
        """测试普通用户创建商品（应该失败）"""
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 100.00,
            "stock": 5,
            "category": "Test Category"
        }
        
        response = await test_client.post(
            "/api/v1/products",
            json=product_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.asyncio
    async def test_create_product_without_auth(
        self,
        test_client: AsyncClient
    ):
        """测试未认证创建商品（应该失败）"""
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 100.00,
            "stock": 5,
            "category": "Test Category"
        }
        
        response = await test_client.post(
            "/api/v1/products",
            json=product_data
        )
        
        assert response.status_code == 403


class TestProductRetrieval:
    """测试商品查询功能"""
    
    @pytest.mark.asyncio
    async def test_get_product_list(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试获取商品列表"""
        # 先创建几个商品
        for i in range(3):
            product_data = {
                "name": f"Product {i+1}",
                "description": f"Description {i+1}",
                "price": 100.00 * (i + 1),
                "stock": 10,
                "category": "Test Category"
            }
            
            await test_client.post(
                "/api/v1/products",
                json=product_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # 获取列表
        response = await test_client.get("/api/v1/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 3
        assert data["data"]["total"] == 3
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试获取单个商品"""
        # 创建商品
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 100.00,
            "stock": 10,
            "category": "Test Category"
        }
        
        create_response = await test_client.post(
            "/api/v1/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        product_id = create_response.json()["data"]["id"]
        
        # 获取商品详情
        response = await test_client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == product_id
        assert data["data"]["name"] == product_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_product(
        self,
        test_client: AsyncClient
    ):
        """测试获取不存在的商品"""
        fake_id = "507f191e810c19729de860ea"
        
        response = await test_client.get(f"/api/v1/products/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False


class TestProductUpdate:
    """测试商品更新功能"""
    
    @pytest.mark.asyncio
    async def test_update_product(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试更新商品"""
        # 创建商品
        product_data = {
            "name": "Original Name",
            "description": "Original Description",
            "price": 100.00,
            "stock": 10,
            "category": "Original Category"
        }
        
        create_response = await test_client.post(
            "/api/v1/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        product_id = create_response.json()["data"]["id"]
        
        # 更新商品
        update_data = {
            "name": "Updated Name",
            "price": 150.00
        }
        
        response = await test_client.put(
            f"/api/v1/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["price"] == 150.00
        # 未更新的字段应保持原值
        assert data["data"]["description"] == "Original Description"


class TestProductDeletion:
    """测试商品删除功能"""
    
    @pytest.mark.asyncio
    async def test_delete_product(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试删除商品"""
        # 创建商品
        product_data = {
            "name": "To Be Deleted",
            "description": "This product will be deleted",
            "price": 100.00,
            "stock": 10,
            "category": "Test Category"
        }
        
        create_response = await test_client.post(
            "/api/v1/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        product_id = create_response.json()["data"]["id"]
        
        # 删除商品
        response = await test_client.delete(
            f"/api/v1/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted"] is True
        
        # 验证商品已被删除（获取时应该返回 404）
        get_response = await test_client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 404


class TestProductSearch:
    """测试商品搜索功能"""
    
    @pytest.mark.asyncio
    async def test_search_products(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试搜索商品"""
        # 创建测试商品
        products = [
            {
                "name": "MacBook Pro",
                "description": "Apple laptop",
                "price": 50000.00,
                "stock": 5,
                "category": "Laptop"
            },
            {
                "name": "iPhone 15",
                "description": "Apple smartphone",
                "price": 30000.00,
                "stock": 10,
                "category": "Phone"
            },
            {
                "name": "Dell XPS",
                "description": "Windows laptop",
                "price": 40000.00,
                "stock": 3,
                "category": "Laptop"
            }
        ]
        
        for product in products:
            await test_client.post(
                "/api/v1/products",
                json=product,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # 搜索 "Apple"
        response = await test_client.get("/api/v1/products/search/query?q=Apple")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2  # MacBook 和 iPhone


class TestProductFiltering:
    """测试商品筛选功能"""
    
    @pytest.mark.asyncio
    async def test_filter_by_category(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试按分类筛选"""
        # 创建不同分类的商品
        await test_client.post(
            "/api/v1/products",
            json={
                "name": "Product 1",
                "description": "Description 1",
                "price": 100.00,
                "stock": 10,
                "category": "Category A"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        await test_client.post(
            "/api/v1/products",
            json={
                "name": "Product 2",
                "description": "Description 2",
                "price": 200.00,
                "stock": 5,
                "category": "Category B"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 按分类筛选
        response = await test_client.get("/api/v1/products?category=Category A")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["category"] == "Category A"
    
    @pytest.mark.asyncio
    async def test_filter_by_price_range(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试按价格区间筛选"""
        # 创建不同价格的商品
        for i in range(5):
            await test_client.post(
                "/api/v1/products",
                json={
                    "name": f"Product {i+1}",
                    "description": f"Description {i+1}",
                    "price": 100.00 * (i + 1),
                    "stock": 10,
                    "category": "Test"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # 筛选价格在 200-400 之间的商品
        response = await test_client.get("/api/v1/products?min_price=200&max_price=400")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3  # 200, 300, 400


class TestProductPagination:
    """测试商品分页功能"""
    
    @pytest.mark.asyncio
    async def test_pagination(
        self,
        test_client: AsyncClient,
        admin_token: str
    ):
        """测试分页查询"""
        # 创建 25 个商品
        for i in range(25):
            await test_client.post(
                "/api/v1/products",
                json={
                    "name": f"Product {i+1}",
                    "description": f"Description {i+1}",
                    "price": 100.00,
                    "stock": 10,
                    "category": "Test"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # 获取第一页（每页 10 个）
        response_page1 = await test_client.get("/api/v1/products?page=1&page_size=10")
        data_page1 = response_page1.json()
        
        assert data_page1["success"] is True
        assert len(data_page1["data"]["items"]) == 10
        assert data_page1["data"]["total"] == 25
        assert data_page1["data"]["page"] == 1
        assert data_page1["data"]["total_pages"] == 3
        
        # 获取第二页
        response_page2 = await test_client.get("/api/v1/products?page=2&page_size=10")
        data_page2 = response_page2.json()
        
        assert len(data_page2["data"]["items"]) == 10
        assert data_page2["data"]["page"] == 2
        
        # 获取第三页
        response_page3 = await test_client.get("/api/v1/products?page=3&page_size=10")
        data_page3 = response_page3.json()
        
        assert len(data_page3["data"]["items"]) == 5
        assert data_page3["data"]["page"] == 3


def test_imports():
    """测试模块导入"""
    from app.models import product
    from app.services import product_service
    from app.api.v1 import products
    
    assert product is not None
    assert product_service is not None
    assert products is not None

