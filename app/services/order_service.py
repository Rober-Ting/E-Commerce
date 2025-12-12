"""
订单服务层 - 业务逻辑实现

此模块实现了订单管理的核心业务逻辑：
- 订单创建（含事务处理）
- 库存检查与扣减
- 订单查询与筛选
- 订单状态管理
- 订单取消与退款
"""

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from bson import ObjectId
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import random
import string
import logging

from app.models.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatusUpdate,
    OrderStatus,
    PaymentStatus,
    OrderItem,
    ShippingAddress,
    OrderStatusHistory,
    OrderListFilter,
    OrderStatistics,
)
from app.middleware.error_handler import (
    NotFoundException,
    ValidationException,
    DatabaseException,
    ForbiddenException,
)

logger = logging.getLogger(__name__)


class OrderService:
    """订单服务类"""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化订单服务

        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db["orders"]
        self.products_collection = db["products"]
        self.users_collection = db["users"]

    async def create_order(
        self,
        order_data: OrderCreate,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> OrderResponse:
        """
        创建订单（含事务处理）

        Args:
            order_data: 订单创建数据
            user_id: 用户ID
            session: MongoDB 会话（用于事务）

        Returns:
            OrderResponse: 创建的订单信息

        Raises:
            ValidationException: 商品不存在、库存不足等验证错误
            DatabaseException: 数据库操作错误
        """
        logger.info(f"用户 {user_id} 开始创建订单，包含 {len(order_data.items)} 个商品")

        # 1. 验证商品并检查库存
        validated_items, products_info = await self._validate_and_prepare_items(
            order_data.items,
            session
        )

        # 2. 计算订单金额
        amounts = self._calculate_order_amounts(validated_items, order_data.coupon_code)

        # 3. 生成订单编号
        order_number = self._generate_order_number()

        # 4. 准备订单数据
        now = datetime.utcnow()
        order_dict = {
            "order_number": order_number,
            "user_id": user_id,
            "items": [item.model_dump(mode='json') for item in validated_items],
            "subtotal": amounts['subtotal'],
            "shipping_fee": amounts['shipping_fee'],
            "discount": amounts['discount'],
            "total_amount": amounts['total_amount'],
            "shipping_address": order_data.shipping_address.model_dump(),
            "status": OrderStatus.PENDING.value,
            "payment_status": PaymentStatus.PENDING.value,
            "payment_method": order_data.payment_method.value,
            "note": order_data.note,
            "coupon_code": order_data.coupon_code,
            "created_at": now,
            "updated_at": now,
            "is_deleted": False,
            "status_history": [
                {
                    "status": OrderStatus.PENDING.value,
                    "changed_at": now,
                    "changed_by": user_id,
                    "note": "订单创建"
                }
            ]
        }

        try:
            # 5. 在事务中执行：扣减库存 + 创建订单
            if session:
                # 使用传入的会话（事务中）
                result = await self._create_order_with_transaction(
                    order_dict,
                    validated_items,
                    session
                )
            else:
                # 尝试使用事务创建订单
                try:
                    async with await self.db.client.start_session() as new_session:
                        async with new_session.start_transaction():
                            result = await self._create_order_with_transaction(
                                order_dict,
                                validated_items,
                                new_session
                            )
                except Exception as e:
                    # 如果事务失败（如未配置复制集），退回到非事务模式
                    logger.warning(f"事务创建订单失败，尝试非事务模式: {str(e)}")
                    result = await self._create_order_without_transaction(
                        order_dict,
                        validated_items
                    )

            order_id = str(result.inserted_id)
            logger.info(f"订单创建成功: {order_number} (ID: {order_id})")

            # 6. 获取并返回完整订单信息
            order = await self.get_order_by_id(order_id)
            return order

        except Exception as e:
            logger.error(f"创建订单失败: {str(e)}", exc_info=True)
            raise DatabaseException(f"创建订单失败: {str(e)}")

    async def _create_order_with_transaction(
        self,
        order_dict: Dict[str, Any],
        items: List[OrderItem],
        session: AsyncIOMotorClientSession
    ):
        """
        在事务中创建订单并扣减库存

        Args:
            order_dict: 订单数据字典
            items: 订单商品项列表
            session: MongoDB 会话

        Returns:
            插入结果
        """
        # 1. 扣减库存
        for item in items:
            update_result = await self.products_collection.update_one(
                {
                    "_id": ObjectId(item.product_id),
                    "stock": {"$gte": item.quantity},
                    "is_deleted": False
                },
                {
                    "$inc": {
                        "stock": -item.quantity,
                        "sales_count": item.quantity
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                },
                session=session
            )

            if update_result.modified_count == 0:
                raise ValidationException(f"商品 '{item.product_name}' 库存不足或已下架")

        # 2. 创建订单
        result = await self.collection.insert_one(order_dict, session=session)
        return result

    async def _create_order_without_transaction(
        self,
        order_dict: Dict[str, Any],
        items: List[OrderItem]
    ):
        """
        非事务模式创建订单（用于未配置复制集的环境）

        Args:
            order_dict: 订单数据字典
            items: 订单商品项列表

        Returns:
            插入结果
        """
        # 1. 检查库存
        for item in items:
            product = await self.products_collection.find_one({
                "_id": ObjectId(item.product_id),
                "is_deleted": False
            })

            if not product:
                raise ValidationException(f"商品 '{item.product_name}' 不存在或已下架")

            if product.get("stock", 0) < item.quantity:
                raise ValidationException(f"商品 '{item.product_name}' 库存不足")

        # 2. 扣减库存
        for item in items:
            await self.products_collection.update_one(
                {"_id": ObjectId(item.product_id)},
                {
                    "$inc": {
                        "stock": -item.quantity,
                        "sales_count": item.quantity
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

        # 3. 创建订单
        result = await self.collection.insert_one(order_dict)
        return result

    async def _validate_and_prepare_items(
        self,
        items: List[OrderItem],
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> Tuple[List[OrderItem], Dict[str, Any]]:
        """
        验证商品并准备订单项

        Args:
            items: 订单商品项列表
            session: MongoDB 会话

        Returns:
            Tuple[List[OrderItem], Dict]: 验证后的商品项列表和商品信息字典

        Raises:
            ValidationException: 商品不存在、库存不足
        """
        validated_items = []
        products_info = {}

        for item in items:
            # 验证商品ID
            if not ObjectId.is_valid(item.product_id):
                raise ValidationException(f"无效的商品ID: {item.product_id}")

            # 查询商品信息
            product = await self.products_collection.find_one(
                {
                    "_id": ObjectId(item.product_id),
                    "is_deleted": False
                },
                session=session
            )

            if not product:
                raise ValidationException(f"商品不存在或已下架: {item.product_id}")

            # 检查库存
            if product.get("stock", 0) < item.quantity:
                raise ValidationException(
                    f"商品 '{product.get('name')}' 库存不足 "
                    f"(可用: {product.get('stock', 0)}, 需要: {item.quantity})"
                )

            # 检查商品状态
            if product.get("status") != "active":
                raise ValidationException(f"商品 '{product.get('name')}' 当前不可购买")

            # 创建订单项（使用实时商品信息）
            validated_item = OrderItem(
                product_id=item.product_id,
                product_name=product.get("name"),
                product_slug=product.get("slug"),
                price=product.get("price"),  # 使用当前价格
                quantity=item.quantity,
                subtotal=round(product.get("price") * item.quantity, 2),
                product_image=product.get("images", [None])[0] if product.get("images") else None,
                attributes=item.attributes
            )

            validated_items.append(validated_item)
            products_info[item.product_id] = product

        return validated_items, products_info

    def _calculate_order_amounts(
        self,
        items: List[OrderItem],
        coupon_code: Optional[str] = None
    ) -> Dict[str, float]:
        """
        计算订单金额

        Args:
            items: 订单商品项列表
            coupon_code: 优惠券代码（可选）

        Returns:
            Dict: 包含 subtotal, shipping_fee, discount, total_amount 的字典
        """
        # 商品总额
        subtotal = sum(item.subtotal for item in items)

        # 运费（根据金额计算，可以配置）
        if subtotal >= 1000:
            shipping_fee = 0.0  # 满1000免运费
        elif subtotal >= 500:
            shipping_fee = 50.0  # 满500运费50
        else:
            shipping_fee = 100.0  # 基础运费100

        # 折扣（TODO: 实现优惠券系统）
        discount = 0.0
        if coupon_code:
            # 这里可以查询优惠券数据库并计算折扣
            logger.info(f"应用优惠券: {coupon_code}")
            # discount = calculate_coupon_discount(coupon_code, subtotal)

        # 最终金额
        total_amount = round(subtotal + shipping_fee - discount, 2)

        return {
            'subtotal': round(subtotal, 2),
            'shipping_fee': round(shipping_fee, 2),
            'discount': round(discount, 2),
            'total_amount': total_amount
        }

    def _generate_order_number(self) -> str:
        """
        生成唯一订单编号

        格式: ORD + YYYYMMDDHHMMSS + 6位随机数字
        例如: ORD202511211430001234567

        Returns:
            str: 订单编号
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.digits, k=6))
        return f"ORD{timestamp}{random_suffix}"

    async def get_order_by_id(
        self,
        order_id: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> OrderResponse:
        """
        根据ID获取订单详情

        Args:
            order_id: 订单ID
            user_id: 用户ID（用于权限验证）
            user_role: 用户角色（用于权限验证）

        Returns:
            OrderResponse: 订单详情

        Raises:
            NotFoundException: 订单不存在
            ForbiddenException: 无权访问
        """
        if not ObjectId.is_valid(order_id):
            raise NotFoundException("无效的订单ID")

        order = await self.collection.find_one({
            "_id": ObjectId(order_id),
            "is_deleted": False
        })

        if not order:
            raise NotFoundException("订单不存在")

        # 权限验证：只有订单所有者和管理员可以查看
        if user_id and user_role != "admin":
            if order.get("user_id") != user_id:
                raise ForbiddenException("无权访问此订单")

        return self._order_helper(order)

    async def get_order_by_number(
        self,
        order_number: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> OrderResponse:
        """
        根据订单编号获取订单详情

        Args:
            order_number: 订单编号
            user_id: 用户ID
            user_role: 用户角色

        Returns:
            OrderResponse: 订单详情
        """
        order = await self.collection.find_one({
            "order_number": order_number,
            "is_deleted": False
        })

        if not order:
            raise NotFoundException("订单不存在")

        # 权限验证
        if user_id and user_role != "admin":
            if order.get("user_id") != user_id:
                raise ForbiddenException("无权访问此订单")

        return self._order_helper(order)

    async def get_user_orders(
        self,
        user_id: str,
        filter_params: OrderListFilter,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[OrderResponse], int]:
        """
        获取用户的订单列表

        Args:
            user_id: 用户ID
            filter_params: 筛选参数
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[List[OrderResponse], int]: 订单列表和总数
        """
        # 构建查询条件
        query = {
            "user_id": user_id,
            "is_deleted": False
        }

        # 应用筛选条件
        query = self._build_filter_query(query, filter_params)

        # 构建排序
        sort_direction = 1 if filter_params.order == "asc" else -1
        sort_field = filter_params.sort_by

        # 查询总数
        total = await self.collection.count_documents(query)

        # 分页查询
        skip = (page - 1) * page_size
        cursor = self.collection.find(query)\
            .sort(sort_field, sort_direction)\
            .skip(skip)\
            .limit(page_size)

        orders = await cursor.to_list(length=page_size)
        orders_response = [self._order_helper(order) for order in orders]

        logger.info(f"用户 {user_id} 的订单列表查询成功，共 {total} 个订单")
        return orders_response, total

    async def get_all_orders(
        self,
        filter_params: OrderListFilter,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[OrderResponse], int]:
        """
        获取所有订单列表（管理员）

        Args:
            filter_params: 筛选参数
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[List[OrderResponse], int]: 订单列表和总数
        """
        # 构建查询条件
        query = {"is_deleted": False}
        query = self._build_filter_query(query, filter_params)

        # 构建排序
        sort_direction = 1 if filter_params.order == "asc" else -1
        sort_field = filter_params.sort_by

        # 查询总数
        total = await self.collection.count_documents(query)

        # 分页查询
        skip = (page - 1) * page_size
        cursor = self.collection.find(query)\
            .sort(sort_field, sort_direction)\
            .skip(skip)\
            .limit(page_size)

        orders = await cursor.to_list(length=page_size)
        orders_response = [self._order_helper(order) for order in orders]

        logger.info(f"管理员订单列表查询成功，共 {total} 个订单")
        return orders_response, total

    def _build_filter_query(
        self,
        query: Dict[str, Any],
        filter_params: OrderListFilter
    ) -> Dict[str, Any]:
        """
        构建筛选查询条件

        Args:
            query: 基础查询条件
            filter_params: 筛选参数

        Returns:
            Dict: 完整的查询条件
        """
        # 订单状态筛选
        if filter_params.status:
            query["status"] = filter_params.status.value

        # 支付状态筛选
        if filter_params.payment_status:
            query["payment_status"] = filter_params.payment_status.value

        # 日期范围筛选
        if filter_params.start_date or filter_params.end_date:
            query["created_at"] = {}
            if filter_params.start_date:
                query["created_at"]["$gte"] = filter_params.start_date
            if filter_params.end_date:
                query["created_at"]["$lte"] = filter_params.end_date

        # 金额范围筛选
        if filter_params.min_amount or filter_params.max_amount:
            query["total_amount"] = {}
            if filter_params.min_amount:
                query["total_amount"]["$gte"] = filter_params.min_amount
            if filter_params.max_amount:
                query["total_amount"]["$lte"] = filter_params.max_amount

        # 关键词搜索（订单编号、收件人）
        if filter_params.search:
            query["$or"] = [
                {"order_number": {"$regex": filter_params.search, "$options": "i"}},
                {"shipping_address.recipient": {"$regex": filter_params.search, "$options": "i"}}
            ]

        return query

    async def update_order_status(
        self,
        order_id: str,
        status_update: OrderStatusUpdate,
        updated_by: str,
        user_role: str
    ) -> OrderResponse:
        """
        更新订单状态

        Args:
            order_id: 订单ID
            status_update: 状态更新数据
            updated_by: 更新人ID
            user_role: 更新人角色

        Returns:
            OrderResponse: 更新后的订单

        Raises:
            NotFoundException: 订单不存在
            ValidationException: 状态转换不合法
        """
        if not ObjectId.is_valid(order_id):
            raise NotFoundException("无效的订单ID")

        # 获取当前订单
        order = await self.collection.find_one({
            "_id": ObjectId(order_id),
            "is_deleted": False
        })

        if not order:
            raise NotFoundException("订单不存在")

        current_status = OrderStatus(order.get("status"))
        new_status = status_update.status

        # 验证状态转换合法性
        if not self._is_valid_status_transition(current_status, new_status):
            raise ValidationException(
                f"不能从 '{current_status.value}' 转换到 '{new_status.value}'"
            )

        # 准备更新数据
        now = datetime.utcnow()
        update_dict = {
            "$set": {
                "status": new_status.value,
                "updated_at": now
            },
            "$push": {
                "status_history": {
                    "status": new_status.value,
                    "changed_at": now,
                    "changed_by": updated_by,
                    "note": status_update.note or f"状态更新为 {new_status.value}"
                }
            }
        }

        # 更新特定状态的时间戳
        if new_status == OrderStatus.PAID:
            update_dict["$set"]["paid_at"] = now
            update_dict["$set"]["payment_status"] = PaymentStatus.PAID.value
        elif new_status == OrderStatus.SHIPPED:
            update_dict["$set"]["shipped_at"] = now
        elif new_status == OrderStatus.DELIVERED:
            update_dict["$set"]["delivered_at"] = now
        elif new_status == OrderStatus.COMPLETED:
            update_dict["$set"]["completed_at"] = now
        elif new_status == OrderStatus.CANCELLED:
            update_dict["$set"]["cancelled_at"] = now

        # 更新订单
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            update_dict
        )

        logger.info(
            f"订单 {order.get('order_number')} 状态更新: "
            f"{current_status.value} -> {new_status.value} (by: {updated_by})"
        )

        # 返回更新后的订单
        updated_order = await self.get_order_by_id(order_id)
        return updated_order

    def _is_valid_status_transition(
        self,
        current: OrderStatus,
        new: OrderStatus
    ) -> bool:
        """
        验证订单状态转换是否合法

        Args:
            current: 当前状态
            new: 新状态

        Returns:
            bool: 是否合法
        """
        # 定义合法的状态转换
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.COMPLETED],
            OrderStatus.DELIVERED: [OrderStatus.COMPLETED, OrderStatus.REFUNDED],
            OrderStatus.COMPLETED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [],  # 已取消的订单不能再转换
            OrderStatus.REFUNDED: [],  # 已退款的订单不能再转换
        }

        # 检查是否在合法转换列表中
        return new in valid_transitions.get(current, [])

    async def cancel_order(
        self,
        order_id: str,
        user_id: str,
        user_role: str,
        reason: Optional[str] = None
    ) -> OrderResponse:
        """
        取消订单（并恢复库存）

        Args:
            order_id: 订单ID
            user_id: 用户ID
            user_role: 用户角色
            reason: 取消原因

        Returns:
            OrderResponse: 取消后的订单

        Raises:
            NotFoundException: 订单不存在
            ForbiddenException: 无权取消
            ValidationException: 订单状态不允许取消
        """
        if not ObjectId.is_valid(order_id):
            raise NotFoundException("无效的订单ID")

        # 获取订单
        order = await self.collection.find_one({
            "_id": ObjectId(order_id),
            "is_deleted": False
        })

        if not order:
            raise NotFoundException("订单不存在")

        # 权限验证：只有订单所有者和管理员可以取消
        if user_role != "admin" and order.get("user_id") != user_id:
            raise ForbiddenException("无权取消此订单")

        # 检查订单状态是否可以取消
        current_status = OrderStatus(order.get("status"))
        cancellable_statuses = [
            OrderStatus.PENDING,
            OrderStatus.PAID,
            OrderStatus.PROCESSING
        ]

        if current_status not in cancellable_statuses:
            raise ValidationException(
                f"订单状态为 '{current_status.value}'，不能取消"
            )

        # 恢复库存
        for item in order.get("items", []):
            await self.products_collection.update_one(
                {"_id": ObjectId(item["product_id"])},
                {
                    "$inc": {
                        "stock": item["quantity"],
                        "sales_count": -item["quantity"]
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

        # 更新订单状态为已取消
        now = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": OrderStatus.CANCELLED.value,
                    "cancelled_at": now,
                    "updated_at": now
                },
                "$push": {
                    "status_history": {
                        "status": OrderStatus.CANCELLED.value,
                        "changed_at": now,
                        "changed_by": user_id,
                        "note": reason or "订单已取消"
                    }
                }
            }
        )

        logger.info(f"订单 {order.get('order_number')} 已取消，库存已恢复")

        # 返回取消后的订单
        cancelled_order = await self.get_order_by_id(order_id)
        return cancelled_order

    async def get_order_statistics(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> OrderStatistics:
        """
        获取订单统计信息

        Args:
            user_id: 用户ID（可选，为空则统计所有）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            OrderStatistics: 订单统计信息
        """
        # 构建查询条件
        match_stage: Dict[str, Any] = {"is_deleted": False}
        if user_id:
            match_stage["user_id"] = user_id
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date

        # 聚合查询
        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "total_orders": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"},
                    "pending_orders": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", OrderStatus.PENDING.value]}, 1, 0]
                        }
                    },
                    "paid_orders": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", OrderStatus.PAID.value]}, 1, 0]
                        }
                    },
                    "processing_orders": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", OrderStatus.PROCESSING.value]}, 1, 0]
                        }
                    },
                    "completed_orders": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", OrderStatus.COMPLETED.value]}, 1, 0]
                        }
                    },
                    "cancelled_orders": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", OrderStatus.CANCELLED.value]}, 1, 0]
                        }
                    }
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return OrderStatistics(
                total_orders=0,
                total_amount=0.0,
                pending_orders=0,
                paid_orders=0,
                processing_orders=0,
                completed_orders=0,
                cancelled_orders=0,
                average_order_value=0.0
            )

        stats = result[0]
        total_orders = stats.get("total_orders", 0)
        total_amount = round(stats.get("total_amount", 0.0), 2)
        average_order_value = round(total_amount / total_orders, 2) if total_orders > 0 else 0.0

        return OrderStatistics(
            total_orders=total_orders,
            total_amount=total_amount,
            pending_orders=stats.get("pending_orders", 0),
            paid_orders=stats.get("paid_orders", 0),
            processing_orders=stats.get("processing_orders", 0),
            completed_orders=stats.get("completed_orders", 0),
            cancelled_orders=stats.get("cancelled_orders", 0),
            average_order_value=average_order_value
        )

    def _order_helper(self, order: Dict[str, Any]) -> OrderResponse:
        """
        将数据库订单文档转换为 OrderResponse 模型

        Args:
            order: 数据库订单文档

        Returns:
            OrderResponse: 订单响应模型
        """
        # 转换商品项
        items = [OrderItem(**item) for item in order.get("items", [])]

        # 转换收货地址
        shipping_address = ShippingAddress(**order.get("shipping_address", {}))

        # 转换状态历史
        status_history = [
            OrderStatusHistory(**history)
            for history in order.get("status_history", [])
        ]

        return OrderResponse(
            id=str(order["_id"]),
            order_number=order.get("order_number"),
            user_id=order.get("user_id"),
            items=items,
            subtotal=order.get("subtotal"),
            shipping_fee=order.get("shipping_fee", 0.0),
            discount=order.get("discount", 0.0),
            total_amount=order.get("total_amount"),
            shipping_address=shipping_address,
            status=OrderStatus(order.get("status")),
            payment_status=PaymentStatus(order.get("payment_status")),
            payment_method=order.get("payment_method"),
            tracking_number=order.get("tracking_number"),
            note=order.get("note"),
            coupon_code=order.get("coupon_code"),
            created_at=order.get("created_at"),
            updated_at=order.get("updated_at"),
            paid_at=order.get("paid_at"),
            shipped_at=order.get("shipped_at"),
            delivered_at=order.get("delivered_at"),
            completed_at=order.get("completed_at"),
            cancelled_at=order.get("cancelled_at"),
            status_history=status_history
        )

