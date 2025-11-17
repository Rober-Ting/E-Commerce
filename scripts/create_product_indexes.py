"""
创建商品集合的索引

这个脚本会为 products 集合创建必要的索引以优化查询性能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def create_product_indexes():
    """创建商品集合的所有索引"""
    print("🔌 连接到 MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    collection = db.products
    
    try:
        print(f"📊 在数据库 '{settings.MONGODB_DB_NAME}' 的 'products' 集合创建索引...\n")
        
        # 1. 商品名称索引（单字段）
        print("1️⃣  创建商品名称索引...")
        await collection.create_index("name")
        print("   ✅ name 索引创建成功")
        
        # 2. 商品分类索引（单字段）
        print("2️⃣  创建商品分类索引...")
        await collection.create_index("category")
        print("   ✅ category 索引创建成功")
        
        # 3. 商品状态索引（单字段）
        print("3️⃣  创建商品状态索引...")
        await collection.create_index("status")
        print("   ✅ status 索引创建成功")
        
        # 4. 标签索引（数组字段）
        print("4️⃣  创建标签索引...")
        await collection.create_index("tags")
        print("   ✅ tags 索引创建成功")
        
        # 5. 价格索引（单字段，用于排序和范围查询）
        print("5️⃣  创建价格索引...")
        await collection.create_index("price")
        print("   ✅ price 索引创建成功")
        
        # 6. 创建时间索引（用于排序）
        print("6️⃣  创建创建时间索引...")
        await collection.create_index("created_at")
        print("   ✅ created_at 索引创建成功")
        
        # 7. 更新时间索引（用于排序）
        print("7️⃣  创建更新时间索引...")
        await collection.create_index("updated_at")
        print("   ✅ updated_at 索引创建成功")
        
        # 8. 销售数量索引（用于排行榜）
        print("8️⃣  创建销售数量索引...")
        await collection.create_index("sales_count")
        print("   ✅ sales_count 索引创建成功")
        
        # 9. 浏览次数索引（用于热门商品）
        print("9️⃣  创建浏览次数索引...")
        await collection.create_index("views")
        print("   ✅ views 索引创建成功")
        
        # 10. 评分索引（用于排序）
        print("🔟 创建评分索引...")
        await collection.create_index("rating")
        print("   ✅ rating 索引创建成功")
        
        # 11. 文本索引（用于全文搜索）
        print("📝 创建文本索引（全文搜索）...")
        try:
            await collection.create_index(
                [
                    ("name", "text"),
                    ("description", "text"),
                    ("tags", "text")
                ],
                default_language="none",  # 不使用特定语言的分词
                name="text_search_index"
            )
            print("   ✅ 文本搜索索引创建成功")
        except Exception as e:
            if "already exists" in str(e):
                print("   ⚠️  文本搜索索引已存在，跳过")
            else:
                raise
        
        # 12. 复合索引：分类 + 状态 + 价格（常用组合查询）
        print("🔗 创建复合索引（category + status + price）...")
        await collection.create_index(
            [
                ("category", 1),
                ("status", 1),
                ("price", 1)
            ],
            name="category_status_price_idx"
        )
        print("   ✅ 复合索引创建成功")
        
        # 13. 复合索引：软删除 + 状态（有效商品查询）
        print("🔗 创建复合索引（is_deleted + status）...")
        await collection.create_index(
            [
                ("is_deleted", 1),
                ("status", 1)
            ],
            name="deleted_status_idx"
        )
        print("   ✅ 复合索引创建成功")
        
        # 14. 唯一索引：URL slug（可选字段，稀疏索引）
        print("🔑 创建唯一索引（slug）...")
        await collection.create_index(
            "slug",
            unique=True,
            sparse=True,  # 稀疏索引：只索引存在该字段的文档
            name="slug_unique_idx"
        )
        print("   ✅ slug 唯一索引创建成功")
        
        # 15. 创建者索引（用于查询某个用户创建的商品）
        print("👤 创建创建者索引...")
        await collection.create_index("created_by")
        print("   ✅ created_by 索引创建成功")
        
        print("\n" + "="*50)
        print("✅ 所有索引创建完成！")
        print("="*50)
        
        # 列出所有索引
        print("\n📋 当前所有索引：")
        indexes = await collection.list_indexes().to_list(length=None)
        for idx, index in enumerate(indexes, 1):
            index_name = index.get("name")
            index_keys = index.get("key")
            unique = index.get("unique", False)
            sparse = index.get("sparse", False)
            
            print(f"\n{idx}. {index_name}")
            print(f"   字段: {index_keys}")
            if unique:
                print("   类型: 唯一索引")
            if sparse:
                print("   类型: 稀疏索引")
        
        print(f"\n总计: {len(indexes)} 个索引")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        raise
    finally:
        client.close()
        print("\n🔌 已关闭 MongoDB 连接")


async def drop_all_indexes(confirm: bool = False):
    """
    删除所有索引（保留 _id 索引）
    
    警告：这会删除除 _id 以外的所有索引！
    """
    if not confirm:
        print("⚠️  警告：此操作会删除所有索引！")
        print("如需执行，请使用参数 confirm=True")
        return
    
    print("🔌 连接到 MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    collection = db.products
    
    try:
        print("🗑️  删除所有索引（保留 _id）...")
        await collection.drop_indexes()
        print("✅ 所有索引已删除")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        raise
    finally:
        client.close()
        print("🔌 已关闭 MongoDB 连接")


async def get_index_stats():
    """获取索引统计信息"""
    print("🔌 连接到 MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    collection = db.products
    
    try:
        print("📊 索引统计信息：\n")
        
        # 获取集合统计
        stats = await db.command("collStats", "products")
        
        print(f"集合: products")
        print(f"文档数量: {stats.get('count', 0)}")
        print(f"平均文档大小: {stats.get('avgObjSize', 0)} bytes")
        print(f"索引数量: {stats.get('nindexes', 0)}")
        print(f"总索引大小: {stats.get('totalIndexSize', 0)} bytes")
        
        # 索引详细信息
        index_sizes = stats.get("indexSizes", {})
        if index_sizes:
            print("\n索引大小详情：")
            for index_name, size in index_sizes.items():
                print(f"  • {index_name}: {size} bytes")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        raise
    finally:
        client.close()
        print("\n🔌 已关闭 MongoDB 连接")


if __name__ == "__main__":
    import sys
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            # 创建索引
            asyncio.run(create_product_indexes())
        
        elif command == "drop":
            # 删除索引
            confirm = len(sys.argv) > 2 and sys.argv[2] == "--confirm"
            asyncio.run(drop_all_indexes(confirm))
        
        elif command == "stats":
            # 查看统计
            asyncio.run(get_index_stats())
        
        else:
            print("❌ 未知命令")
            print("\n用法:")
            print("  python scripts/create_product_indexes.py create        # 创建索引")
            print("  python scripts/create_product_indexes.py drop --confirm # 删除所有索引")
            print("  python scripts/create_product_indexes.py stats         # 查看统计")
    else:
        # 默认创建索引
        asyncio.run(create_product_indexes())

