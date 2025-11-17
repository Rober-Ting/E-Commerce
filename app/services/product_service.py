"""
商品服务层

提供商品管理的业务逻辑
"""

from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import re

from app.models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductInDB,
    ProductListFilter,
    ProductStatus
)
from app.middleware.error_handler import (
    NotFoundException,
    ValidationException,
    DatabaseException
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProductService:
    """商品服务类"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化商品服务
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db.products
    
    def _product_helper(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换商品文档格式
        
        Args:
            product: MongoDB 文档
            
        Returns:
            Dict[str, Any]: 格式化的商品数据
        """
        if product:
            product["id"] = str(product.pop("_id"))
            # 处理 Decimal128 (如果使用)
            if "price" in product and hasattr(product["price"], "to_decimal"):
                product["price"] = float(product["price"].to_decimal())
            return product
        return None
    
    def _generate_slug(self, name: str) -> str:
        """
        生成 URL 友好的 slug
        
        Args:
            name: 商品名称
            
        Returns:
            str: slug 字符串
        """
        # 转为小写
        slug = name.lower()
        # 替换空格为连字符
        slug = re.sub(r'\s+', '-', slug)
        # 移除特殊字符，只保留字母、数字、连字符
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # 移除多余的连字符
        slug = re.sub(r'-+', '-', slug)
        # 去除首尾连字符
        slug = slug.strip('-')
        return slug or "product"
    
    async def create_product(
        self,
        product_data: ProductCreate,
        user_id: str
    ) -> ProductResponse:
        """
        创建商品
        
        Args:
            product_data: 商品创建数据
            user_id: 创建者 ID
            
        Returns:
            ProductResponse: 创建的商品
            
        Raises:
            ValidationException: 数据验证失败
            DatabaseException: 数据库操作失败
        """
        try:
            logger.info(f"创建商品: name={product_data.name}, user_id={user_id}")
            
            # 准备商品数据
            product_dict = product_data.dict()
            
            # 生成 slug（如果没有提供）
            if not product_dict.get("slug"):
                product_dict["slug"] = self._generate_slug(product_dict["name"])
            
            # 检查 slug 是否已存在
            existing_product = await self.collection.find_one({
                "slug": product_dict["slug"],
                "is_deleted": False
            })
            
            if existing_product:
                # 如果 slug 已存在，添加后缀
                import uuid
                product_dict["slug"] = f"{product_dict['slug']}-{str(uuid.uuid4())[:8]}"
            
            # 添加元数据
            product_dict["views"] = 0
            product_dict["sales_count"] = 0
            product_dict["rating"] = 0.0
            product_dict["is_deleted"] = False
            product_dict["created_at"] = datetime.utcnow()
            product_dict["updated_at"] = datetime.utcnow()
            product_dict["created_by"] = user_id
            product_dict["updated_by"] = user_id
            
            # 插入数据库
            result = await self.collection.insert_one(product_dict)
            
            # 获取创建的商品
            created_product = await self.collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"商品创建成功: product_id={result.inserted_id}")
            
            return ProductResponse(**self._product_helper(created_product))
        
        except Exception as e:
            logger.error(f"创建商品失败: {str(e)}")
            raise DatabaseException(
                message="Failed to create product",
                details={"error": str(e), "product_name": product_data.name}
            )
    
    async def get_product_by_id(
        self,
        product_id: str,
        increment_views: bool = False
    ) -> Optional[ProductResponse]:
        """
        根据 ID 获取商品
        
        Args:
            product_id: 商品 ID
            increment_views: 是否增加浏览次数
            
        Returns:
            Optional[ProductResponse]: 商品数据或 None
            
        Raises:
            ValidationException: 无效的 ID 格式
        """
        logger.info(f"获取商品: product_id={product_id}")
        
        # 验证 ID 格式
        if not ObjectId.is_valid(product_id):
            raise ValidationException(
                message="Invalid product ID format",
                details={"product_id": product_id}
            )
        
        # 查询商品（排除已删除的）
        product = await self.collection.find_one({
            "_id": ObjectId(product_id),
            "is_deleted": False
        })
        
        if not product:
            return None
        
        # 增加浏览次数（可选）
        if increment_views:
            await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$inc": {"views": 1}}
            )
            product["views"] = product.get("views", 0) + 1
        
        return ProductResponse(**self._product_helper(product))
    
    async def get_products(
        self,
        filter_params: ProductListFilter,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[ProductResponse], int]:
        """
        获取商品列表（分页、筛选、搜索、排序）
        
        Args:
            filter_params: 筛选参数
            page: 页码（从 1 开始）
            page_size: 每页数量
            
        Returns:
            Tuple[List[ProductResponse], int]: (商品列表, 总数)
        """
        logger.info(f"获取商品列表: page={page}, page_size={page_size}")
        
        # 构建查询条件
        query = {"is_deleted": False}
        
        # 分类筛选
        if filter_params.category:
            query["category"] = filter_params.category
        
        # 状态筛选
        if filter_params.status:
            query["status"] = filter_params.status
        else:
            # 默认只显示上架中的商品
            query["status"] = {"$ne": ProductStatus.INACTIVE}
        
        # 价格区间
        if filter_params.min_price is not None or filter_params.max_price is not None:
            price_filter = {}
            if filter_params.min_price is not None:
                price_filter["$gte"] = filter_params.min_price
            if filter_params.max_price is not None:
                price_filter["$lte"] = filter_params.max_price
            query["price"] = price_filter
        
        # 标签筛选
        if filter_params.tags:
            query["tags"] = {"$all": filter_params.tags}
        
        # 搜索（使用正则表达式）
        if filter_params.search:
            search_pattern = {"$regex": filter_params.search, "$options": "i"}
            query["$or"] = [
                {"name": search_pattern},
                {"description": search_pattern},
                {"tags": search_pattern}
            ]
        
        # 计算总数
        total = await self.collection.count_documents(query)
        
        # 构建排序
        sort_direction = 1 if filter_params.order == "asc" else -1
        sort_field = filter_params.sort_by
        
        # 分页查询
        skip = (page - 1) * page_size
        cursor = self.collection.find(query)\
            .sort(sort_field, sort_direction)\
            .skip(skip)\
            .limit(page_size)
        
        products = await cursor.to_list(length=page_size)
        
        # 转换格式
        product_list = [
            ProductResponse(**self._product_helper(product))
            for product in products
        ]
        
        logger.info(f"获取商品列表成功: 返回 {len(product_list)} 个商品，总数 {total}")
        
        return product_list, total
    
    async def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate,
        user_id: str
    ) -> Optional[ProductResponse]:
        """
        更新商品
        
        Args:
            product_id: 商品 ID
            product_data: 更新数据
            user_id: 更新者 ID
            
        Returns:
            Optional[ProductResponse]: 更新后的商品或 None
            
        Raises:
            ValidationException: 无效的 ID 格式或数据
            DatabaseException: 数据库操作失败
        """
        logger.info(f"更新商品: product_id={product_id}, user_id={user_id}")
        
        # 验证 ID 格式
        if not ObjectId.is_valid(product_id):
            raise ValidationException(
                message="Invalid product ID format",
                details={"product_id": product_id}
            )
        
        # 检查商品是否存在
        existing_product = await self.collection.find_one({
            "_id": ObjectId(product_id),
            "is_deleted": False
        })
        
        if not existing_product:
            return None
        
        # 准备更新数据（排除 None 值）
        update_dict = {
            k: v for k, v in product_data.dict().items()
            if v is not None
        }
        
        if not update_dict:
            # 没有需要更新的数据
            return ProductResponse(**self._product_helper(existing_product))
        
        # 如果更新了 slug，检查是否重复
        if "slug" in update_dict:
            duplicate = await self.collection.find_one({
                "slug": update_dict["slug"],
                "_id": {"$ne": ObjectId(product_id)},
                "is_deleted": False
            })
            if duplicate:
                raise ValidationException(
                    message="Slug already exists",
                    details={"slug": update_dict["slug"]}
                )
        
        # 添加更新时间和更新者
        update_dict["updated_at"] = datetime.utcnow()
        update_dict["updated_by"] = user_id
        
        try:
            # 更新数据库
            result = await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                logger.warning(f"商品未更新: product_id={product_id}")
            
            # 获取更新后的商品
            updated_product = await self.collection.find_one({"_id": ObjectId(product_id)})
            
            logger.info(f"商品更新成功: product_id={product_id}")
            
            return ProductResponse(**self._product_helper(updated_product))
        
        except Exception as e:
            logger.error(f"更新商品失败: {str(e)}")
            raise DatabaseException(
                message="Failed to update product",
                details={"error": str(e), "product_id": product_id}
            )
    
    async def delete_product(
        self,
        product_id: str,
        user_id: str
    ) -> bool:
        """
        删除商品（软删除）
        
        Args:
            product_id: 商品 ID
            user_id: 删除者 ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            ValidationException: 无效的 ID 格式
        """
        logger.info(f"删除商品: product_id={product_id}, user_id={user_id}")
        
        # 验证 ID 格式
        if not ObjectId.is_valid(product_id):
            raise ValidationException(
                message="Invalid product ID format",
                details={"product_id": product_id}
            )
        
        # 软删除（标记为已删除）
        result = await self.collection.update_one(
            {
                "_id": ObjectId(product_id),
                "is_deleted": False
            },
            {
                "$set": {
                    "is_deleted": True,
                    "updated_at": datetime.utcnow(),
                    "updated_by": user_id
                }
            }
        )
        
        success = result.modified_count > 0
        
        if success:
            logger.info(f"商品删除成功: product_id={product_id}")
        else:
            logger.warning(f"商品删除失败或已删除: product_id={product_id}")
        
        return success
    
    async def update_stock(
        self,
        product_id: str,
        quantity: int,
        user_id: str
    ) -> Optional[ProductResponse]:
        """
        更新库存
        
        Args:
            product_id: 商品 ID
            quantity: 库存变动数量（正数增加，负数扣减）
            user_id: 操作者 ID
            
        Returns:
            Optional[ProductResponse]: 更新后的商品或 None
            
        Raises:
            ValidationException: 库存不足或无效的 ID
        """
        logger.info(f"更新库存: product_id={product_id}, quantity={quantity}")
        
        # 验证 ID 格式
        if not ObjectId.is_valid(product_id):
            raise ValidationException(
                message="Invalid product ID format",
                details={"product_id": product_id}
            )
        
        # 获取当前商品
        product = await self.collection.find_one({
            "_id": ObjectId(product_id),
            "is_deleted": False
        })
        
        if not product:
            return None
        
        # 检查库存是否足够（扣减时）
        current_stock = product.get("stock", 0)
        new_stock = current_stock + quantity
        
        if new_stock < 0:
            raise ValidationException(
                message="Insufficient stock",
                details={
                    "product_id": product_id,
                    "current_stock": current_stock,
                    "requested_quantity": abs(quantity),
                    "shortage": abs(new_stock)
                }
            )
        
        # 更新库存
        await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {"stock": quantity},
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "updated_by": user_id
                }
            }
        )
        
        # 获取更新后的商品
        updated_product = await self.collection.find_one({"_id": ObjectId(product_id)})
        
        logger.info(f"库存更新成功: product_id={product_id}, new_stock={new_stock}")
        
        return ProductResponse(**self._product_helper(updated_product))
    
    async def check_stock_available(
        self,
        product_id: str,
        quantity: int
    ) -> bool:
        """
        检查库存是否足够
        
        Args:
            product_id: 商品 ID
            quantity: 需要的数量
            
        Returns:
            bool: 库存是否足够
        """
        if not ObjectId.is_valid(product_id):
            return False
        
        product = await self.collection.find_one({
            "_id": ObjectId(product_id),
            "is_deleted": False,
            "status": ProductStatus.ACTIVE
        })
        
        if not product:
            return False
        
        return product.get("stock", 0) >= quantity
    
    async def get_products_by_category(
        self,
        category: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[ProductResponse], int]:
        """
        按分类获取商品
        
        Args:
            category: 商品分类
            page: 页码
            page_size: 每页数量
            
        Returns:
            Tuple[List[ProductResponse], int]: (商品列表, 总数)
        """
        filter_params = ProductListFilter(category=category)
        return await self.get_products(filter_params, page, page_size)
    
    async def search_products(
        self,
        search_query: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[ProductResponse], int]:
        """
        搜索商品
        
        Args:
            search_query: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            Tuple[List[ProductResponse], int]: (商品列表, 总数)
        """
        filter_params = ProductListFilter(search=search_query)
        return await self.get_products(filter_params, page, page_size)
    
    async def get_categories(self) -> List[str]:
        """
        获取所有商品分类
        
        Returns:
            List[str]: 分类列表
        """
        categories = await self.collection.distinct(
            "category",
            {"is_deleted": False, "status": ProductStatus.ACTIVE}
        )
        return sorted(categories)
    
    async def increment_sales_count(
        self,
        product_id: str,
        quantity: int = 1
    ) -> bool:
        """
        增加销售计数
        
        Args:
            product_id: 商品 ID
            quantity: 销售数量
            
        Returns:
            bool: 是否成功
        """
        if not ObjectId.is_valid(product_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"sales_count": quantity}}
        )
        
        return result.modified_count > 0



