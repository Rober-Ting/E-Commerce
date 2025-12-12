"""
订单集合索引创建脚本

此脚本用于为 MongoDB 的 orders 集合创建必要的索引，以优化查询性能。

索引列表：
1. order_number (唯一索引) - 订单编号
2. user_id - 用户ID
3. status - 订单状态
4. payment_status - 支付状态
5. created_at - 创建时间
6. updated_at - 更新时间
7. paid_at - 支付时间
8. {user_id, created_at} - 复合索引（用户订单列表查询）
9. {status, created_at} - 复合索引（按状态筛选订单）
10. {user_id, status} - 复合索引（用户特定状态订单）
11. is_deleted - 稀疏索引（软删除）

使用方法：
    python scripts/create_order_indexes.py create       # 创建所有索引
    python scripts/create_order_indexes.py drop --confirm # 删除所有索引
    python scripts/create_order_indexes.py stats        # 查看索引统计
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrderIndexManager:
    """订单索引管理器"""

    def __init__(self, mongodb_url: str = "mongodb://localhost:27017", db_name: str = "ecommerce_db"):
        """
        初始化索引管理器

        Args:
            mongodb_url: MongoDB 连接URL
            db_name: 数据库名称
        """
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        """连接到 MongoDB"""
        logger.info(f"正在连接到 MongoDB: {self.mongodb_url}")
        self.client = AsyncIOMotorClient(self.mongodb_url)
        self.db = self.client[self.db_name]
        self.collection = self.db["orders"]
        
        # 测试连接
        await self.client.admin.command('ping')
        logger.info(f"✅ 成功连接到数据库: {self.db_name}")

    async def close(self):
        """关闭 MongoDB 连接"""
        if self.client:
            self.client.close()
            logger.info("已关闭数据库连接")

    async def create_indexes(self):
        """创建所有索引"""
        logger.info("=" * 80)
        logger.info("开始创建订单集合索引")
        logger.info("=" * 80)

        indexes_to_create = [
            # 1. 订单编号唯一索引
            {
                "name": "order_number_unique",
                "keys": [("order_number", ASCENDING)],
                "unique": True,
                "description": "订单编号唯一索引"
            },
            # 2. 用户ID索引
            {
                "name": "user_id_index",
                "keys": [("user_id", ASCENDING)],
                "description": "用户ID索引（用于查询用户的所有订单）"
            },
            # 3. 订单状态索引
            {
                "name": "status_index",
                "keys": [("status", ASCENDING)],
                "description": "订单状态索引（用于按状态筛选订单）"
            },
            # 4. 支付状态索引
            {
                "name": "payment_status_index",
                "keys": [("payment_status", ASCENDING)],
                "description": "支付状态索引（用于按支付状态筛选）"
            },
            # 5. 创建时间索引（降序，最新订单优先）
            {
                "name": "created_at_index",
                "keys": [("created_at", DESCENDING)],
                "description": "创建时间索引（用于按时间排序）"
            },
            # 6. 更新时间索引
            {
                "name": "updated_at_index",
                "keys": [("updated_at", DESCENDING)],
                "description": "更新时间索引"
            },
            # 7. 支付时间索引（稀疏索引，因为不是所有订单都已支付）
            {
                "name": "paid_at_index",
                "keys": [("paid_at", DESCENDING)],
                "sparse": True,
                "description": "支付时间索引（稀疏索引）"
            },
            # 8. 用户ID + 创建时间复合索引
            {
                "name": "user_created_compound",
                "keys": [("user_id", ASCENDING), ("created_at", DESCENDING)],
                "description": "用户ID + 创建时间复合索引（优化用户订单列表查询）"
            },
            # 9. 状态 + 创建时间复合索引
            {
                "name": "status_created_compound",
                "keys": [("status", ASCENDING), ("created_at", DESCENDING)],
                "description": "状态 + 创建时间复合索引（优化按状态筛选查询）"
            },
            # 10. 用户ID + 状态复合索引
            {
                "name": "user_status_compound",
                "keys": [("user_id", ASCENDING), ("status", ASCENDING)],
                "description": "用户ID + 状态复合索引（查询用户特定状态的订单）"
            },
            # 11. 软删除标记索引（稀疏索引）
            {
                "name": "is_deleted_index",
                "keys": [("is_deleted", ASCENDING)],
                "sparse": True,
                "description": "软删除标记索引（稀疏索引，只索引已删除的文档）"
            },
            # 12. 订单金额索引（用于金额范围查询）
            {
                "name": "total_amount_index",
                "keys": [("total_amount", DESCENDING)],
                "description": "订单总金额索引（用于按金额排序和筛选）"
            },
        ]

        created_count = 0
        skipped_count = 0
        failed_count = 0

        for idx, index_spec in enumerate(indexes_to_create, 1):
            try:
                logger.info(f"\n[{idx}/{len(indexes_to_create)}] 正在创建索引: {index_spec['name']}")
                logger.info(f"  描述: {index_spec['description']}")
                logger.info(f"  字段: {index_spec['keys']}")

                # 检查索引是否已存在
                existing_indexes = await self.collection.index_information()
                if index_spec['name'] in existing_indexes:
                    logger.info(f"  ⚠️  索引已存在，跳过")
                    skipped_count += 1
                    continue

                # 准备索引选项
                index_options = {
                    "name": index_spec["name"]
                }

                if index_spec.get("unique"):
                    index_options["unique"] = True
                if index_spec.get("sparse"):
                    index_options["sparse"] = True

                # 创建索引
                await self.collection.create_index(
                    index_spec["keys"],
                    **index_options
                )

                logger.info(f"  ✅ 索引创建成功")
                created_count += 1

            except Exception as e:
                logger.error(f"  ❌ 索引创建失败: {str(e)}")
                failed_count += 1

        # 总结
        logger.info("\n" + "=" * 80)
        logger.info("索引创建完成")
        logger.info("=" * 80)
        logger.info(f"✅ 成功创建: {created_count} 个")
        logger.info(f"⚠️  跳过（已存在）: {skipped_count} 个")
        logger.info(f"❌ 失败: {failed_count} 个")
        logger.info(f"📊 总计: {len(indexes_to_create)} 个索引")
        logger.info("=" * 80)

        return created_count, skipped_count, failed_count

    async def drop_indexes(self, confirm: bool = False):
        """
        删除所有索引（保留 _id 索引）

        Args:
            confirm: 是否确认删除
        """
        if not confirm:
            logger.warning("⚠️  删除索引需要确认，请使用 --confirm 参数")
            return

        logger.info("=" * 80)
        logger.info("开始删除订单集合索引")
        logger.info("=" * 80)

        try:
            # 获取所有索引
            indexes = await self.collection.index_information()
            index_names = [name for name in indexes.keys() if name != "_id_"]

            logger.info(f"找到 {len(index_names)} 个自定义索引")

            if not index_names:
                logger.info("没有需要删除的索引")
                return

            # 逐个删除
            for idx, index_name in enumerate(index_names, 1):
                logger.info(f"[{idx}/{len(index_names)}] 正在删除索引: {index_name}")
                await self.collection.drop_index(index_name)
                logger.info(f"  ✅ 删除成功")

            logger.info("\n" + "=" * 80)
            logger.info(f"✅ 成功删除 {len(index_names)} 个索引")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ 删除索引失败: {str(e)}")

    async def show_index_stats(self):
        """显示索引统计信息"""
        logger.info("=" * 80)
        logger.info("订单集合索引统计")
        logger.info("=" * 80)

        try:
            # 获取集合统计信息
            stats = await self.db.command("collStats", "orders")
            
            # 获取索引信息
            indexes = await self.collection.index_information()

            # 基本统计
            logger.info("\n📊 集合统计:")
            logger.info(f"  • 文档数量: {stats.get('count', 0):,}")
            logger.info(f"  • 存储大小: {stats.get('size', 0) / 1024 / 1024:.2f} MB")
            logger.info(f"  • 索引数量: {len(indexes)}")
            logger.info(f"  • 索引大小: {stats.get('totalIndexSize', 0) / 1024 / 1024:.2f} MB")

            # 详细索引信息
            logger.info("\n📑 索引列表:")
            for idx, (name, info) in enumerate(indexes.items(), 1):
                logger.info(f"\n  {idx}. {name}")
                logger.info(f"     键: {info.get('key', {})}")
                if info.get('unique'):
                    logger.info("     类型: 唯一索引")
                if info.get('sparse'):
                    logger.info("     类型: 稀疏索引")

            logger.info("\n" + "=" * 80)

        except Exception as e:
            logger.error(f"❌ 获取索引统计失败: {str(e)}")


async def main():
    """主函数"""
    # 解析命令行参数
    import argparse

    parser = argparse.ArgumentParser(description="订单集合索引管理工具")
    parser.add_argument(
        "action",
        choices=["create", "drop", "stats"],
        help="操作类型: create=创建索引, drop=删除索引, stats=查看统计"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="确认删除索引（用于 drop 操作）"
    )
    parser.add_argument(
        "--db-url",
        default="mongodb://localhost:27017",
        help="MongoDB 连接URL（默认: mongodb://localhost:27017）"
    )
    parser.add_argument(
        "--db-name",
        default="ecommerce_db",
        help="数据库名称（默认: ecommerce_db）"
    )

    args = parser.parse_args()

    # 创建索引管理器
    manager = OrderIndexManager(mongodb_url=args.db_url, db_name=args.db_name)

    try:
        # 连接数据库
        await manager.connect()

        # 执行操作
        if args.action == "create":
            await manager.create_indexes()
        elif args.action == "drop":
            await manager.drop_indexes(confirm=args.confirm)
        elif args.action == "stats":
            await manager.show_index_stats()

    except Exception as e:
        logger.error(f"❌ 操作失败: {str(e)}")
        sys.exit(1)
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())

