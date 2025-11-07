"""
快速查看 MongoDB 数据库中的用户
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def check_users():
    # 连接数据库
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ecommerce_db
    
    print("=" * 60)
    print("📊 MongoDB 数据库用户查询")
    print("=" * 60)
    print()
    
    # 统计用户数量
    total_users = await db.users.count_documents({})
    print(f"📈 总用户数: {total_users}")
    print()
    
    # 获取所有用户
    users_cursor = db.users.find().sort("created_at", -1)
    users = await users_cursor.to_list(length=100)
    
    if not users:
        print("⚠️  数据库中没有用户")
        return
    
    print("👥 用户列表:")
    print("-" * 60)
    
    for i, user in enumerate(users, 1):
        print(f"\n用户 {i}:")
        print(f"  ID: {user['_id']}")
        print(f"  📧 Email: {user['email']}")
        print(f"  👤 姓名: {user.get('full_name', 'N/A')}")
        print(f"  📱 电话: {user.get('phone', 'N/A')}")
        print(f"  🎭 角色: {user['role']}")
        print(f"  ✅ 状态: {'活跃' if user['is_active'] else '非活跃'}")
        print(f"  🔐 密码哈希: {user['hashed_password'][:30]}...")
        print(f"  📅 创建时间: {user['created_at']}")
        print(f"  🔄 更新时间: {user['updated_at']}")
    
    print()
    print("=" * 60)
    print("✅ 查询完成")
    
    # 关闭连接
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())

