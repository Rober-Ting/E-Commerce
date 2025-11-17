"""
商品管理 API 端点

提供商品的 CRUD、搜索、筛选等功能
"""

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List

from app.models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListFilter,
    ProductStatus,
    StockUpdate
)
from app.models.common import (
    ResponseModel,
    PaginatedResponse,
    PaginatedData,
    PaginationParams,
    success_response,
    paginated_response
)
from app.models.user import UserInDB, UserRole
from app.services.product_service import ProductService
from app.utils.dependencies import (
    get_current_active_user,
    require_vendor_or_admin
)
from app.database import get_database
from app.middleware.error_handler import NotFoundException, ForbiddenException
from app.utils.logging_config import get_logger

# 创建路由器
router = APIRouter(prefix="/products", tags=["Product Management"])
logger = get_logger(__name__)


@router.get("", response_model=ResponseModel[PaginatedData[ProductResponse]])
async def list_products(
    page: int = Query(1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量（最大 100）"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="商品分类"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    status: Optional[ProductStatus] = Query(None, description="商品状态"),
    tags: Optional[str] = Query(None, description="标签（逗号分隔）"),
    sort_by: str = Query("created_at", pattern="^(price|created_at|updated_at|sales_count|rating|views|name)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取商品列表
    
    - **所有用户都可以访问**
    - 支持分页、搜索、筛选、排序
    - 默认只显示上架中的商品
    """
    logger.info(f"获取商品列表请求: page={page}, page_size={page_size}, search={search}")
    
    # 解析标签
    tag_list = tags.split(",") if tags else None
    
    # 处理空字符串的 search（前端可能传递空字符串）
    search_value = search.strip() if search and search.strip() else None
    
    # 构建筛选参数
    filter_params = ProductListFilter(
        search=search_value,
        category=category,
        min_price=min_price,
        max_price=max_price,
        status=status,
        tags=tag_list,
        sort_by=sort_by,
        order=order
    )
    
    logger.debug(f"筛选参数: search={filter_params.search}, category={filter_params.category}, "
                 f"min_price={filter_params.min_price}, max_price={filter_params.max_price}, "
                 f"status={filter_params.status}, tags={filter_params.tags}")
    
    # 获取商品列表
    product_service = ProductService(db)
    products, total = await product_service.get_products(filter_params, page, page_size)
    
    # 将 ProductResponse 对象转换为字典以确保正确序列化（包括枚举类型）
    products_dict = [
        p.model_dump(mode='json') if hasattr(p, 'model_dump') else p.dict()
        for p in products
    ]
    
    # 返回分页响应
    return paginated_response(
        items=products_dict,
        total=total,
        page=page,
        per_page=page_size,
        message=f"获取商品列表成功，共 {total} 个商品"
    )


@router.get("/{product_id}", response_model=ResponseModel[ProductResponse])
async def get_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取商品详情
    
    - **所有用户都可以访问**
    - 自动增加浏览次数
    """
    logger.info(f"获取商品详情: product_id={product_id}")
    
    product_service = ProductService(db)
    product = await product_service.get_product_by_id(product_id, increment_views=True)
    
    if not product:
        logger.warning(f"商品不存在: product_id={product_id}")
        raise NotFoundException(resource="Product", resource_id=product_id)
    
    # 将 ProductResponse 转换为字典以确保正确序列化（包括枚举类型）
    product_dict = product.model_dump(mode='json') if hasattr(product, 'model_dump') else product.dict()
    
    return success_response(
        data=product_dict,
        message="获取商品详情成功"
    )


@router.post("", response_model=ResponseModel[ProductResponse], status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: UserInDB = Depends(require_vendor_or_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    创建商品
    
    - **需要 vendor 或 admin 权限**
    - 商品名称、价格、库存为必填项
    - 系统会自动生成 slug（如果未提供）
    """
    logger.info(f"创建商品请求: name={product_data.name}, user_id={current_user.id}")
    
    product_service = ProductService(db)
    new_product = await product_service.create_product(product_data, current_user.id)
    
    # 将 ProductResponse 转换为字典以确保正确序列化（包括枚举类型）
    product_dict = new_product.model_dump(mode='json') if hasattr(new_product, 'model_dump') else new_product.dict()
    
    return success_response(
        data=product_dict,
        message=f"商品创建成功: {new_product.name}"
    )


@router.put("/{product_id}", response_model=ResponseModel[ProductResponse])
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: UserInDB = Depends(require_vendor_or_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    更新商品
    
    - **需要 vendor 或 admin 权限**
    - vendor 只能更新自己创建的商品
    - admin 可以更新所有商品
    """
    logger.info(f"更新商品请求: product_id={product_id}, user_id={current_user.id}")
    
    product_service = ProductService(db)
    
    # 检查商品是否存在
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        logger.warning(f"商品不存在: product_id={product_id}")
        raise NotFoundException(resource="Product", resource_id=product_id)
    
    # 检查权限（vendor 只能更新自己的商品）
    if current_user.role == UserRole.VENDOR:
        if existing_product.created_by != current_user.id:
            logger.warning(
                f"权限不足: user_id={current_user.id} 尝试更新 product_id={product_id}"
            )
            raise ForbiddenException(
                message="You can only update your own products"
            )
    
    # 更新商品
    updated_product = await product_service.update_product(
        product_id,
        product_data,
        current_user.id
    )
    
    # 将 ProductResponse 转换为字典以确保正确序列化（包括枚举类型）
    product_dict = updated_product.model_dump(mode='json') if hasattr(updated_product, 'model_dump') else updated_product.dict()
    
    return success_response(
        data=product_dict,
        message="商品更新成功"
    )


@router.delete("/{product_id}", response_model=ResponseModel[dict])
async def delete_product(
    product_id: str,
    current_user: UserInDB = Depends(require_vendor_or_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    删除商品（软删除）
    
    - **需要 vendor 或 admin 权限**
    - vendor 只能删除自己创建的商品
    - admin 可以删除所有商品
    - 商品不会被物理删除，只是标记为已删除
    """
    logger.info(f"删除商品请求: product_id={product_id}, user_id={current_user.id}")
    
    product_service = ProductService(db)
    
    # 检查商品是否存在
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        logger.warning(f"商品不存在: product_id={product_id}")
        raise NotFoundException(resource="Product", resource_id=product_id)
    
    # 检查权限（vendor 只能删除自己的商品）
    if current_user.role == UserRole.VENDOR:
        if existing_product.created_by != current_user.id:
            logger.warning(
                f"权限不足: user_id={current_user.id} 尝试删除 product_id={product_id}"
            )
            raise ForbiddenException(
                message="You can only delete your own products"
            )
    
    # 删除商品
    success = await product_service.delete_product(product_id, current_user.id)
    
    if not success:
        logger.error(f"商品删除失败: product_id={product_id}")
        raise NotFoundException(resource="Product", resource_id=product_id)
    
    return success_response(
        data={"deleted": True, "product_id": product_id},
        message="商品删除成功"
    )


@router.put("/{product_id}/stock", response_model=ResponseModel[ProductResponse])
async def update_product_stock(
    product_id: str,
    stock_update: StockUpdate,
    current_user: UserInDB = Depends(require_vendor_or_admin()),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    更新商品库存
    
    - **需要 vendor 或 admin 权限**
    - 正数表示增加库存，负数表示扣减库存
    - 库存不能为负数
    """
    logger.info(
        f"更新库存请求: product_id={product_id}, quantity={stock_update.quantity}, "
        f"user_id={current_user.id}, reason={stock_update.reason}"
    )
    
    product_service = ProductService(db)
    
    # 检查商品是否存在
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        logger.warning(f"商品不存在: product_id={product_id}")
        raise NotFoundException(resource="Product", resource_id=product_id)
    
    # 检查权限（vendor 只能更新自己的商品）
    if current_user.role == UserRole.VENDOR:
        if existing_product.created_by != current_user.id:
            logger.warning(
                f"权限不足: user_id={current_user.id} 尝试更新库存 product_id={product_id}"
            )
            raise ForbiddenException(
                message="You can only update stock for your own products"
            )
    
    # 更新库存
    updated_product = await product_service.update_stock(
        product_id,
        stock_update.quantity,
        current_user.id
    )
    
    # 将 ProductResponse 转换为字典以确保正确序列化（包括枚举类型）
    product_dict = updated_product.model_dump(mode='json') if hasattr(updated_product, 'model_dump') else updated_product.dict()
    
    action = "增加" if stock_update.quantity > 0 else "扣减"
    
    return success_response(
        data=product_dict,
        message=f"库存{action}成功: {abs(stock_update.quantity)} 个"
    )


@router.get("/search/query", response_model=ResponseModel[PaginatedData[ProductResponse]])
async def search_products(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    搜索商品
    
    - **所有用户都可以访问**
    - 在商品名称、描述、标签中搜索
    - 不区分大小写
    """
    logger.info(f"搜索商品: query={q}, page={page}")
    
    product_service = ProductService(db)
    products, total = await product_service.search_products(q, page, page_size)
    
    # 将 ProductResponse 对象转换为字典以确保正确序列化（包括枚举类型）
    products_dict = [
        p.model_dump(mode='json') if hasattr(p, 'model_dump') else p.dict()
        for p in products
    ]
    
    return paginated_response(
        items=products_dict,
        total=total,
        page=page,
        per_page=page_size,
        message=f"搜索到 {total} 个商品"
    )


@router.get("/category/{category}", response_model=ResponseModel[PaginatedData[ProductResponse]])
async def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    按分类获取商品
    
    - **所有用户都可以访问**
    - 只显示上架中的商品
    """
    logger.info(f"按分类获取商品: category={category}, page={page}")
    
    product_service = ProductService(db)
    products, total = await product_service.get_products_by_category(category, page, page_size)
    
    # 将 ProductResponse 对象转换为字典以确保正确序列化（包括枚举类型）
    products_dict = [
        p.model_dump(mode='json') if hasattr(p, 'model_dump') else p.dict()
        for p in products
    ]
    
    return paginated_response(
        items=products_dict,
        total=total,
        page=page,
        per_page=page_size,
        message=f"分类 '{category}' 共有 {total} 个商品"
    )


@router.get("/categories/all", response_model=ResponseModel[List[str]])
async def get_all_categories(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取所有商品分类
    
    - **所有用户都可以访问**
    - 只返回有上架商品的分类
    """
    logger.info("获取所有商品分类")
    
    product_service = ProductService(db)
    categories = await product_service.get_categories()
    
    return success_response(
        data=categories,
        message=f"共有 {len(categories)} 个分类"
    )

