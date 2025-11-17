"""
商品数据模型

定义商品相关的 Pydantic 模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProductStatus(str, Enum):
    """商品状态枚举"""
    ACTIVE = "active"           # 上架中
    INACTIVE = "inactive"       # 已下架
    OUT_OF_STOCK = "out_of_stock"  # 缺货


class ProductBase(BaseModel):
    """商品基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    description: str = Field(..., min_length=1, description="商品描述")
    price: float = Field(..., gt=0, description="商品价格（必须大于 0）")
    stock: int = Field(..., ge=0, description="库存数量（必须大于等于 0）")
    category: str = Field(..., min_length=1, description="商品分类")
    tags: List[str] = Field(default_factory=list, description="商品标签")
    images: List[str] = Field(default_factory=list, description="商品图片 URL 列表")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="商品属性（如颜色、尺寸等）")
    
    @validator('price')
    def validate_price(cls, v):
        """验证价格"""
        if v <= 0:
            raise ValueError('价格必须大于 0')
        # 限制小数点后两位
        return round(v, 2)
    
    @validator('stock')
    def validate_stock(cls, v):
        """验证库存"""
        if v < 0:
            raise ValueError('库存不能为负数')
        return v
    
    @validator('images')
    def validate_images(cls, v):
        """验证图片列表"""
        if len(v) > 10:
            raise ValueError('最多只能上传 10 张图片')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """验证标签列表"""
        if len(v) > 20:
            raise ValueError('最多只能添加 20 个标签')
        # 移除重复标签
        return list(set(v))

    class Config:
        json_schema_extra = {
            "example": {
                "name": "MacBook Pro 14 吋 M3",
                "description": "全新 Apple M3 晶片，14 吋 Liquid Retina XDR 顯示器",
                "price": 59900.00,
                "stock": 15,
                "category": "筆記型電腦",
                "tags": ["Apple", "MacBook", "M3", "筆電"],
                "images": [
                    "https://example.com/images/macbook-1.jpg",
                    "https://example.com/images/macbook-2.jpg"
                ],
                "attributes": {
                    "color": "太空灰",
                    "screen_size": "14 吋",
                    "processor": "Apple M3",
                    "ram": "16GB",
                    "storage": "512GB SSD"
                }
            }
        }


class ProductCreate(ProductBase):
    """创建商品模型"""
    status: ProductStatus = Field(
        default=ProductStatus.ACTIVE,
        description="商品状态"
    )
    slug: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="URL 友好标识（可选，系统可自动生成）"
    )
    
    @validator('slug')
    def validate_slug(cls, v):
        """验证 slug"""
        if v:
            # 只允许小写字母、数字、连字符
            import re
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug 只能包含小写字母、数字和连字符')
        return v


class ProductUpdate(BaseModel):
    """更新商品模型（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    status: Optional[ProductStatus] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    
    @validator('price')
    def validate_price(cls, v):
        """验证价格"""
        if v is not None and v <= 0:
            raise ValueError('价格必须大于 0')
        if v is not None:
            return round(v, 2)
        return v
    
    @validator('stock')
    def validate_stock(cls, v):
        """验证库存"""
        if v is not None and v < 0:
            raise ValueError('库存不能为负数')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "price": 55900.00,
                "stock": 20,
                "status": "active"
            }
        }


class ProductResponse(ProductBase):
    """商品响应模型"""
    id: str = Field(..., description="商品 ID")
    status: ProductStatus = Field(..., description="商品状态")
    slug: Optional[str] = Field(None, description="URL 友好标识")
    views: int = Field(default=0, description="浏览次数")
    sales_count: int = Field(default=0, description="销售数量")
    rating: float = Field(default=0.0, ge=0, le=5, description="平均评分")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f191e810c19729de860ea",
                "name": "MacBook Pro 14 吋 M3",
                "description": "全新 Apple M3 晶片",
                "price": 59900.00,
                "stock": 15,
                "category": "筆記型電腦",
                "tags": ["Apple", "MacBook"],
                "images": ["https://example.com/images/macbook-1.jpg"],
                "attributes": {"color": "太空灰"},
                "status": "active",
                "slug": "macbook-pro-14-m3",
                "views": 1250,
                "sales_count": 48,
                "rating": 4.8,
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z",
                "created_by": "507f1f77bcf86cd799439011"
            }
        }


class ProductInDB(ProductResponse):
    """数据库存储模型"""
    is_deleted: bool = Field(default=False, description="软删除标记")
    updated_by: Optional[str] = Field(None, description="最后更新者 ID")


class ProductListFilter(BaseModel):
    """商品列表筛选参数"""
    search: Optional[str] = Field(None, description="搜索关键词（商品名称、描述、标签）")
    category: Optional[str] = Field(None, description="商品分类")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    status: Optional[ProductStatus] = Field(None, description="商品状态")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    sort_by: Optional[str] = Field(
        "created_at",
        description="排序字段",
        pattern="^(price|created_at|updated_at|sales_count|rating|views|name)$"
    )
    order: Optional[str] = Field(
        "desc",
        description="排序方向",
        pattern="^(asc|desc)$"
    )
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """验证价格区间"""
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('最高价格不能小于最低价格')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "search": "MacBook",
                "category": "筆記型電腦",
                "min_price": 30000,
                "max_price": 80000,
                "status": "active",
                "tags": ["Apple"],
                "sort_by": "price",
                "order": "asc"
            }
        }


class StockUpdate(BaseModel):
    """库存更新模型"""
    quantity: int = Field(..., description="库存变动数量（正数为增加，负数为扣减）")
    reason: Optional[str] = Field(None, description="变动原因")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 10,
                "reason": "补货入库"
            }
        }


class ProductSearchResult(BaseModel):
    """商品搜索结果"""
    products: List[ProductResponse]
    total: int
    search_query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [...],
                "total": 25,
                "search_query": "MacBook"
            }
        }

