"""
清理旧的 admin 账户（admin@ecommerce.local）

用于修复邮箱验证问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, close_mongo_connection, db


async def cleanup_old_admin():
    """删除旧的 admin 账户"""
    
    print("\n" + "="*60)
    print("🧹 清理旧的管理员账户")
    print("="*60 + "\n")
    
    # 连接到数据库
    print("📡 连接到 MongoDB...")
    await connect_to_mongo()
    
    try:
        users_collection = db.db.users
        
        # 删除 admin@ecommerce.local（如果存在）
        old_admin_email = "admin@ecommerce.local"
        result = await users_collection.delete_one({"email": old_admin_email})
        
        if result.deleted_count > 0:
            print(f"✅ 已删除旧管理员账户: {old_admin_email}")
        else:
            print(f"ℹ️  未找到旧管理员账户: {old_admin_email}")
        
        # 检查新的 admin@ecommerce.com 是否存在
        new_admin_email = "admin@ecommerce.com"
        existing_new = await users_collection.find_one({"email": new_admin_email})
        
        if existing_new:
            print(f"✅ 新管理员账户已存在: {new_admin_email}")
        else:
            print(f"⚠️  新管理员账户尚未创建: {new_admin_email}")
            print(f"   请运行: .\\init_users.ps1")
        
        print("\n" + "="*60)
        print("✅ 清理完成！")
        print("="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}\n")
    finally:
        await close_mongo_connection()
        print("📡 数据库连接已关闭\n")


if __name__ == "__main__":
    asyncio.run(cleanup_old_admin())


