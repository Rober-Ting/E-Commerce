"""
订单管理 API 端点

此模块定义了订单管理的所有 RESTful API 端点：
- POST /orders - 创建订单
- GET /orders - 获取我的订单列表
- GET /orders/all - 获取所有订单（管理员）
- GET /orders/{order_id} - 获取订单详情
- PUT /orders/{order_id}/status - 更新订单状态
- PUT /orders/{order_id}/cancel - 取消订单
- GET /orders/statistics - 订单统计
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from datetime import datetime
import logging

from app.models.common import ResponseModel, success_response, paginated_response, PaginatedData
from app.models.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    OrderStatus,
    PaymentStatus,
    OrderListFilter,
    OrderCancelRequest,
    OrderStatistics,
)
from app.services.order_service import OrderService
from app.models.user import UserInDB
from app.utils.dependencies import (
    get_current_user,
    require_admin,
    require_vendor_or_admin,
    get_database,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Order Management"])


@router.post("", response_model=ResponseModel[OrderResponse])
async def create_order(
    order_data: OrderCreate,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    创建订单

    **权限**: 已认证用户

    **功能**:
    - 验证商品库存
    - 计算订单金额
    - 自动扣减库存
    - 生成订单编号
    - 使用事务保证数据一致性（如果支持）

    **请求体**:
    ```json
    {
        "items": [
            {
                "product_id": "商品ID",
                "product_name": "商品名称",
                "price": 单价,
                "quantity": 数量,
                "subtotal": 小计
            }
        ],
        "shipping_address": {
            "recipient": "收件人",
            "phone": "联系电话",
            "address_line1": "地址",
            "city": "城市",
            "postal_code": "邮编"
        },
        "payment_method": "支付方式",
        "note": "备注（可选）"
    }
    ```

    **返回**: 创建的订单详情
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id

    new_order = await order_service.create_order(
        order_data=order_data,
        user_id=user_id
    )

    # 转换为字典以确保正确序列化
    order_dict = new_order.model_dump(mode='json')

    logger.info(f"用户 {user_id} 创建订单成功: {new_order.order_number}")

    return success_response(
        data=order_dict,
        message=f"订单创建成功，订单编号: {new_order.order_number}"
    )


@router.get("", response_model=ResponseModel[PaginatedData[OrderResponse]])
async def get_my_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    payment_status: Optional[PaymentStatus] = Query(None, description="支付状态筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    min_amount: Optional[float] = Query(None, gt=0, description="最低金额"),
    max_amount: Optional[float] = Query(None, gt=0, description="最高金额"),
    search: Optional[str] = Query(None, max_length=200, description="搜索关键词"),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|total_amount|paid_at)$", description="排序字段"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    获取我的订单列表

    **权限**: 已认证用户

    **查询参数**:
    - `page`: 页码（默认 1）
    - `page_size`: 每页数量（默认 20，最大 100）
    - `status`: 订单状态筛选
    - `payment_status`: 支付状态筛选
    - `start_date`: 开始日期
    - `end_date`: 结束日期
    - `min_amount`: 最低金额
    - `max_amount`: 最高金额
    - `search`: 搜索关键词（订单编号、收件人）
    - `sort_by`: 排序字段（created_at, updated_at, total_amount, paid_at）
    - `order`: 排序方向（asc, desc）

    **返回**: 分页的订单列表
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id

    # 构建筛选参数
    filter_params = OrderListFilter(
        status=status,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        order=order
    )

    orders, total = await order_service.get_user_orders(
        user_id=user_id,
        filter_params=filter_params,
        page=page,
        page_size=page_size
    )

    # 转换为字典列表
    orders_dict = [
        order.model_dump(mode='json') for order in orders
    ]

    return paginated_response(
        items=orders_dict,
        total=total,
        page=page,
        per_page=page_size,
        message=f"获取订单列表成功，共 {total} 个订单"
    )


@router.get("/all", response_model=ResponseModel[PaginatedData[OrderResponse]])
async def get_all_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    payment_status: Optional[PaymentStatus] = Query(None, description="支付状态筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    min_amount: Optional[float] = Query(None, gt=0, description="最低金额"),
    max_amount: Optional[float] = Query(None, gt=0, description="最高金额"),
    search: Optional[str] = Query(None, max_length=200, description="搜索关键词"),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|total_amount|paid_at)$", description="排序字段"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    current_user: UserInDB = Depends(require_admin()),
    db = Depends(get_database)
):
    """
    获取所有订单列表（管理员）

    **权限**: admin

    **查询参数**: 同 "获取我的订单列表"

    **返回**: 分页的所有订单列表
    """
    order_service = OrderService(db)

    # 构建筛选参数
    filter_params = OrderListFilter(
        status=status,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        order=order
    )

    orders, total = await order_service.get_all_orders(
        filter_params=filter_params,
        page=page,
        page_size=page_size
    )

    # 转换为字典列表
    orders_dict = [
        order.model_dump(mode='json') for order in orders
    ]

    return paginated_response(
        items=orders_dict,
        total=total,
        page=page,
        per_page=page_size,
        message=f"获取所有订单列表成功，共 {total} 个订单"
    )


@router.get("/{order_id}", response_model=ResponseModel[OrderResponse])
async def get_order(
    order_id: str = Path(..., description="订单ID"),
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    获取订单详情

    **权限**: 订单所有者 或 admin

    **路径参数**:
    - `order_id`: 订单ID

    **返回**: 订单详细信息
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id
    user_role = current_user.role.value

    order = await order_service.get_order_by_id(
        order_id=order_id,
        user_id=user_id,
        user_role=user_role
    )

    # 转换为字典
    order_dict = order.model_dump(mode='json')

    return success_response(
        data=order_dict,
        message="获取订单详情成功"
    )


@router.put("/{order_id}/status", response_model=ResponseModel[OrderResponse])
async def update_order_status(
    order_id: str = Path(..., description="订单ID"),
    status_update: OrderStatusUpdate = ...,
    current_user: UserInDB = Depends(require_vendor_or_admin()),
    db = Depends(get_database)
):
    """
    更新订单状态

    **权限**: admin 或 vendor

    **路径参数**:
    - `order_id`: 订单ID

    **请求体**:
    ```json
    {
        "status": "新状态",
        "note": "备注（可选）"
    }
    ```

    **支持的状态转换**:
    - pending → paid, cancelled
    - paid → processing, cancelled
    - processing → shipped, cancelled
    - shipped → delivered, completed
    - delivered → completed, refunded
    - completed → refunded

    **返回**: 更新后的订单信息
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id
    user_role = current_user.role.value

    updated_order = await order_service.update_order_status(
        order_id=order_id,
        status_update=status_update,
        updated_by=user_id,
        user_role=user_role
    )

    # 转换为字典
    order_dict = updated_order.model_dump(mode='json')

    return success_response(
        data=order_dict,
        message=f"订单状态更新成功: {status_update.status.value}"
    )


@router.put("/{order_id}/cancel", response_model=ResponseModel[OrderResponse])
async def cancel_order(
    order_id: str = Path(..., description="订单ID"),
    cancel_request: OrderCancelRequest = ...,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    取消订单

    **权限**: 订单所有者 或 admin

    **功能**:
    - 将订单状态更新为已取消
    - 自动恢复商品库存
    - 记录取消原因

    **限制**:
    - 只有 pending、paid、processing 状态的订单可以取消
    - 已发货(shipped)或已完成(completed)的订单不能取消

    **请求体**:
    ```json
    {
        "reason": "取消原因（可选）"
    }
    ```

    **返回**: 取消后的订单信息
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id
    user_role = current_user.role.value

    cancelled_order = await order_service.cancel_order(
        order_id=order_id,
        user_id=user_id,
        user_role=user_role,
        reason=cancel_request.reason
    )

    # 转换为字典
    order_dict = cancelled_order.model_dump(mode='json')

    return success_response(
        data=order_dict,
        message="订单已取消，库存已恢复"
    )


@router.get("/statistics/summary", response_model=ResponseModel[OrderStatistics])
async def get_order_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    获取订单统计信息

    **权限**: 已认证用户（查看自己的统计）/ admin（查看所有统计）

    **查询参数**:
    - `start_date`: 开始日期（可选）
    - `end_date`: 结束日期（可选）

    **返回**:
    ```json
    {
        "total_orders": 订单总数,
        "total_amount": 总金额,
        "pending_orders": 待付款订单数,
        "paid_orders": 已付款订单数,
        "processing_orders": 处理中订单数,
        "completed_orders": 已完成订单数,
        "cancelled_orders": 已取消订单数,
        "average_order_value": 平均订单金额
    }
    ```
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id
    user_role = current_user.role.value

    # 如果不是管理员，只能查看自己的统计
    if user_role != "admin":
        stats = await order_service.get_order_statistics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    else:
        # 管理员可以查看所有统计
        stats = await order_service.get_order_statistics(
            user_id=None,
            start_date=start_date,
            end_date=end_date
        )

    # 转换为字典
    stats_dict = stats.model_dump()

    return success_response(
        data=stats_dict,
        message="获取订单统计成功"
    )


@router.get("/number/{order_number}", response_model=ResponseModel[OrderResponse])
async def get_order_by_number(
    order_number: str = Path(..., description="订单编号"),
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    根据订单编号获取订单详情

    **权限**: 订单所有者 或 admin

    **路径参数**:
    - `order_number`: 订单编号（例如：ORD202511211430001234567）

    **返回**: 订单详细信息
    """
    order_service = OrderService(db)
    # current_user 是 UserInDB Pydantic 模型实例，直接访问 id 属性
    user_id = current_user.id
    user_role = current_user.role.value

    order = await order_service.get_order_by_number(
        order_number=order_number,
        user_id=user_id,
        user_role=user_role
    )

    # 转换为字典
    order_dict = order.model_dump(mode='json')

    return success_response(
        data=order_dict,
        message="获取订单详情成功"
    )

