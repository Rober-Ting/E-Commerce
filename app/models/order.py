"""
订单管理模块 - 数据模型

此模块定义了订单管理相关的 Pydantic 模型，包括：
- 订单创建、更新、响应模型
- 订单商品项模型
- 订单状态枚举
- 支付相关模型
- 收货地址模型
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待付款
    PAID = "paid"  # 已付款
    PROCESSING = "processing"  # 待发货/处理中
    SHIPPED = "shipped"  # 已发货
    DELIVERED = "delivered"  # 已送达
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"  # 已退款


class PaymentStatus(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    FAILED = "failed"  # 支付失败
    REFUNDED = "refunded"  # 已退款
    CANCELLED = "cancelled"  # 已取消


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    CREDIT_CARD = "credit_card"  # 信用卡
    DEBIT_CARD = "debit_card"  # 借记卡
    PAYPAL = "paypal"  # PayPal
    BANK_TRANSFER = "bank_transfer"  # 银行转账
    CASH_ON_DELIVERY = "cod"  # 货到付款
    ALIPAY = "alipay"  # 支付宝
    WECHAT_PAY = "wechat_pay"  # 微信支付


class ShippingAddress(BaseModel):
    """收货地址模型"""
    recipient: str = Field(..., min_length=1, max_length=100, description="收件人姓名")
    phone: str = Field(..., description="联系电话")
    address_line1: str = Field(..., min_length=5, max_length=200, description="地址第一行")
    address_line2: Optional[str] = Field(None, max_length=200, description="地址第二行（可选）")
    city: str = Field(..., min_length=1, max_length=100, description="城市")
    state: Optional[str] = Field(None, max_length=100, description="州/省（可选）")
    postal_code: str = Field(..., description="邮政编码")
    country: str = Field(default="Taiwan", max_length=100, description="国家/地区")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "recipient": "张三",
                "phone": "0912345678",
                "address_line1": "台北市中正区忠孝东路一段1号",
                "address_line2": "10楼",
                "city": "台北市",
                "state": "台北市",
                "postal_code": "100",
                "country": "Taiwan"
            }]
        }
    }


class OrderItem(BaseModel):
    """订单商品项模型"""
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称（下单时快照）")
    product_slug: Optional[str] = Field(None, description="商品Slug")
    price: float = Field(..., gt=0, description="商品单价（下单时价格）")
    quantity: int = Field(..., gt=0, description="购买数量")
    subtotal: float = Field(..., gt=0, description="小计金额")
    product_image: Optional[str] = Field(None, description="商品图片URL")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="商品属性（如颜色、尺寸）")

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """验证并格式化价格（保留两位小数）"""
        return round(v, 2)

    @field_validator('subtotal')
    @classmethod
    def validate_subtotal(cls, v: float) -> float:
        """验证并格式化小计（保留两位小数）"""
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "product_id": "507f1f77bcf86cd799439011",
                "product_name": "iPhone 15 Pro Max",
                "product_slug": "iphone-15-pro-max",
                "price": 39900.00,
                "quantity": 1,
                "subtotal": 39900.00,
                "product_image": "https://example.com/iphone.jpg",
                "attributes": {
                    "color": "钛金属",
                    "storage": "256GB"
                }
            }]
        }
    }


class OrderStatusHistory(BaseModel):
    """订单状态历史记录模型"""
    status: OrderStatus = Field(..., description="订单状态")
    changed_at: datetime = Field(default_factory=datetime.utcnow, description="状态变更时间")
    changed_by: Optional[str] = Field(None, description="变更人ID")
    note: Optional[str] = Field(None, max_length=500, description="备注说明")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "paid",
                "changed_at": "2025-11-21T10:30:00Z",
                "changed_by": "507f1f77bcf86cd799439011",
                "note": "用户完成支付"
            }]
        }
    }


class OrderCreate(BaseModel):
    """创建订单模型"""
    items: List[OrderItem] = Field(..., min_length=1, description="订单商品列表")
    shipping_address: ShippingAddress = Field(..., description="收货地址")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    note: Optional[str] = Field(None, max_length=500, description="订单备注")
    coupon_code: Optional[str] = Field(None, max_length=50, description="优惠券代码（可选）")

    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[OrderItem]) -> List[OrderItem]:
        """验证订单商品列表"""
        if not v:
            raise ValueError('订单至少需要包含一个商品')
        if len(v) > 50:
            raise ValueError('订单商品数量不能超过50个')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439011",
                        "product_name": "iPhone 15 Pro Max",
                        "price": 39900.00,
                        "quantity": 1,
                        "subtotal": 39900.00
                    }
                ],
                "shipping_address": {
                    "recipient": "张三",
                    "phone": "0912345678",
                    "address_line1": "台北市中正区忠孝东路一段1号",
                    "city": "台北市",
                    "postal_code": "100",
                    "country": "Taiwan"
                },
                "payment_method": "credit_card",
                "note": "请在周末送达"
            }]
        }
    }


class OrderUpdate(BaseModel):
    """更新订单模型（仅管理员）"""
    status: Optional[OrderStatus] = Field(None, description="订单状态")
    payment_status: Optional[PaymentStatus] = Field(None, description="支付状态")
    shipping_address: Optional[ShippingAddress] = Field(None, description="收货地址")
    tracking_number: Optional[str] = Field(None, max_length=100, description="物流单号")
    note: Optional[str] = Field(None, max_length=500, description="备注")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "shipped",
                "tracking_number": "SF1234567890",
                "note": "已通过顺丰速运发货"
            }]
        }
    }


class OrderStatusUpdate(BaseModel):
    """订单状态更新模型"""
    status: OrderStatus = Field(..., description="新的订单状态")
    note: Optional[str] = Field(None, max_length=500, description="状态变更备注")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "shipped",
                "note": "订单已发货，物流单号：SF1234567890"
            }]
        }
    }


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: str = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单编号")
    user_id: str = Field(..., description="用户ID")
    
    # 订单商品
    items: List[OrderItem] = Field(..., description="订单商品列表")
    
    # 金额信息
    subtotal: float = Field(..., description="商品总额")
    shipping_fee: float = Field(default=0.0, description="运费")
    discount: float = Field(default=0.0, description="折扣金额")
    total_amount: float = Field(..., description="订单总金额")
    
    # 收货信息
    shipping_address: ShippingAddress = Field(..., description="收货地址")
    
    # 状态信息
    status: OrderStatus = Field(..., description="订单状态")
    payment_status: PaymentStatus = Field(..., description="支付状态")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    
    # 物流信息
    tracking_number: Optional[str] = Field(None, description="物流单号")
    
    # 其他信息
    note: Optional[str] = Field(None, description="订单备注")
    coupon_code: Optional[str] = Field(None, description="使用的优惠券")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    paid_at: Optional[datetime] = Field(None, description="支付时间")
    shipped_at: Optional[datetime] = Field(None, description="发货时间")
    delivered_at: Optional[datetime] = Field(None, description="送达时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    cancelled_at: Optional[datetime] = Field(None, description="取消时间")
    
    # 状态历史
    status_history: List[OrderStatusHistory] = Field(default_factory=list, description="状态历史记录")

    @field_validator('subtotal', 'shipping_fee', 'discount', 'total_amount')
    @classmethod
    def validate_amounts(cls, v: float) -> float:
        """验证并格式化金额（保留两位小数）"""
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "507f1f77bcf86cd799439011",
                "order_number": "ORD202511211430001234567",
                "user_id": "507f1f77bcf86cd799439012",
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439013",
                        "product_name": "iPhone 15 Pro Max",
                        "price": 39900.00,
                        "quantity": 1,
                        "subtotal": 39900.00
                    }
                ],
                "subtotal": 39900.00,
                "shipping_fee": 100.00,
                "discount": 0.00,
                "total_amount": 40000.00,
                "shipping_address": {
                    "recipient": "张三",
                    "phone": "0912345678",
                    "address_line1": "台北市中正区忠孝东路一段1号",
                    "city": "台北市",
                    "postal_code": "100",
                    "country": "Taiwan"
                },
                "status": "paid",
                "payment_status": "paid",
                "payment_method": "credit_card",
                "created_at": "2025-11-21T10:00:00Z",
                "updated_at": "2025-11-21T10:30:00Z",
                "paid_at": "2025-11-21T10:30:00Z"
            }]
        }
    }


class OrderInDB(BaseModel):
    """订单数据库存储模型（内部使用）"""
    order_number: str
    user_id: str
    items: List[Dict[str, Any]]
    subtotal: float
    shipping_fee: float
    discount: float
    total_amount: float
    shipping_address: Dict[str, Any]
    status: str
    payment_status: str
    payment_method: str
    tracking_number: Optional[str] = None
    note: Optional[str] = None
    coupon_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    is_deleted: bool = False
    status_history: List[Dict[str, Any]] = []


class OrderListFilter(BaseModel):
    """订单列表筛选参数模型"""
    status: Optional[OrderStatus] = Field(None, description="订单状态筛选")
    payment_status: Optional[PaymentStatus] = Field(None, description="支付状态筛选")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    min_amount: Optional[float] = Field(None, gt=0, description="最低金额")
    max_amount: Optional[float] = Field(None, gt=0, description="最高金额")
    search: Optional[str] = Field(None, max_length=200, description="搜索关键词（订单编号、收件人）")
    sort_by: str = Field(
        default="created_at",
        description="排序字段",
        pattern="^(created_at|updated_at|total_amount|paid_at)$"
    )
    order: str = Field(
        default="desc",
        description="排序方向",
        pattern="^(asc|desc)$"
    )

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """验证日期范围"""
        if v and 'start_date' in info.data and info.data['start_date']:
            if v < info.data['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v

    @field_validator('max_amount')
    @classmethod
    def validate_amount_range(cls, v: Optional[float], info) -> Optional[float]:
        """验证金额范围"""
        if v and 'min_amount' in info.data and info.data['min_amount']:
            if v < info.data['min_amount']:
                raise ValueError('最高金额不能小于最低金额')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "paid",
                "start_date": "2025-11-01T00:00:00Z",
                "end_date": "2025-11-30T23:59:59Z",
                "min_amount": 1000.00,
                "max_amount": 100000.00,
                "sort_by": "created_at",
                "order": "desc"
            }]
        }
    }


class OrderCancelRequest(BaseModel):
    """取消订单请求模型"""
    reason: Optional[str] = Field(None, max_length=500, description="取消原因")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "reason": "不想要了"
            }]
        }
    }


class OrderStatistics(BaseModel):
    """订单统计模型"""
    total_orders: int = Field(..., description="订单总数")
    total_amount: float = Field(..., description="总金额")
    pending_orders: int = Field(..., description="待付款订单数")
    paid_orders: int = Field(..., description="已付款订单数")
    processing_orders: int = Field(..., description="处理中订单数")
    completed_orders: int = Field(..., description="已完成订单数")
    cancelled_orders: int = Field(..., description="已取消订单数")
    average_order_value: float = Field(..., description="平均订单金额")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "total_orders": 150,
                "total_amount": 5000000.00,
                "pending_orders": 10,
                "paid_orders": 20,
                "processing_orders": 15,
                "completed_orders": 100,
                "cancelled_orders": 5,
                "average_order_value": 33333.33
            }]
        }
    }

