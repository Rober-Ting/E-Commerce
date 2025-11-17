"""
初始化管理員賬戶腳本

創建默認的管理員賬戶，用於系統管理
⚠️ 安全提示：創建後請立即修改密碼！
"""

import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, close_mongo_connection, db
from app.utils.security import hash_password
from app.models.user import UserRole
from datetime import datetime


async def init_admin_user():
    """初始化管理員用戶"""
    
    print("\n" + "="*60)
    print("🔐 初始化管理員賬戶")
    print("="*60 + "\n")
    
    # 連接到數據庫
    print("📡 連接到 MongoDB...")
    await connect_to_mongo()
    
    try:
        users_collection = db.db.users
        
        # 檢查是否已存在 admin 用戶
        admin_email = "admin@ecommerce.com"
        existing_admin = await users_collection.find_one({"email": admin_email})
        
        if existing_admin:
            print(f"\n⚠️  管理員賬戶已存在！")
            print(f"   Email: {admin_email}")
            print(f"   如需重置，請手動刪除後重新運行此腳本。\n")
            return
        
        # 創建管理員賬戶
        print("\n✨ 創建新的管理員賬戶...")
        
        admin_data = {
            "email": admin_email,
            "hashed_password": hash_password("Admin123!"),  # 默認密碼
            "full_name": "System Administrator",
            "phone": "0900000000",
            "role": UserRole.ADMIN.value,
            "is_active": True,
            "is_email_verified": True,
            "addresses": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await users_collection.insert_one(admin_data)
        
        if result.inserted_id:
            print("\n" + "="*60)
            print("✅ 管理員賬戶創建成功！")
            print("="*60)
            print("\n📋 賬戶信息：")
            print(f"   📧 Email:    {admin_email}")
            print(f"   🔒 Password: Admin123!")
            print(f"   👤 姓名:     System Administrator")
            print(f"   🎭 角色:     {UserRole.ADMIN.value}")
            print(f"   🆔 ID:       {result.inserted_id}")
            print("\n" + "="*60)
            print("⚠️  重要安全提示：")
            print("="*60)
            print("   1. 請立即登錄並修改默認密碼！")
            print("   2. 不要將此賬戶信息分享給非管理員用戶！")
            print("   3. 定期更新管理員密碼以確保安全！")
            print("="*60 + "\n")
            
            # 顯示如何登錄
            print("🚀 快速開始：")
            print("   1. 啟動後端: .\\start_backend.ps1")
            print("   2. 訪問 Swagger UI: http://localhost:8000/docs")
            print("   3. 使用上述賬戶信息登錄")
            print("   4. 立即修改密碼\n")
        else:
            print("\n❌ 創建管理員賬戶失敗！\n")
            
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}\n")
    finally:
        await close_mongo_connection()
        print("📡 數據庫連接已關閉\n")


async def create_test_users():
    """創建測試用戶（可選）"""
    
    print("\n" + "="*60)
    print("👥 創建測試用戶")
    print("="*60 + "\n")
    
    await connect_to_mongo()
    
    try:
        users_collection = db.db.users
        
        # 測試用戶列表
        test_users = [
            {
                "email": "vendor@test.com",
                "password": "Vendor123!",
                "full_name": "測試商家",
                "phone": "0911111111",
                "role": UserRole.VENDOR.value
            },
            {
                "email": "customer@test.com",
                "password": "Customer123!",
                "full_name": "測試顧客",
                "phone": "0922222222",
                "role": UserRole.CUSTOMER.value
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_info in test_users:
            # 檢查是否已存在
            existing = await users_collection.find_one({"email": user_info["email"]})
            
            if existing:
                print(f"⏭️  跳過已存在的用戶: {user_info['email']}")
                skipped_count += 1
                continue
            
            # 創建用戶
            user_data = {
                "email": user_info["email"],
                "hashed_password": hash_password(user_info["password"]),
                "full_name": user_info["full_name"],
                "phone": user_info["phone"],
                "role": user_info["role"],
                "is_active": True,
                "is_email_verified": True,
                "addresses": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await users_collection.insert_one(user_data)
            
            if result.inserted_id:
                print(f"✅ 創建測試用戶: {user_info['email']} ({user_info['role']})")
                created_count += 1
        
        print(f"\n📊 結果:")
        print(f"   ✅ 創建: {created_count} 個")
        print(f"   ⏭️  跳過: {skipped_count} 個")
        
        if created_count > 0:
            print("\n" + "="*60)
            print("📋 測試賬戶列表：")
            print("="*60)
            print("\n   1. 商家賬戶 (Vendor):")
            print("      📧 Email:    vendor@test.com")
            print("      🔒 Password: Vendor123!")
            print("\n   2. 顧客賬戶 (Customer):")
            print("      📧 Email:    customer@test.com")
            print("      🔒 Password: Customer123!")
            print("\n" + "="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}\n")
    finally:
        await close_mongo_connection()


async def main():
    """主函數"""
    
    print("\n" + "="*60)
    print("🎯 E-Commerce 用戶初始化腳本")
    print("="*60)
    
    # 創建管理員賬戶
    await init_admin_user()
    
    # 詢問是否創建測試用戶
    print("\n📝 是否同時創建測試用戶？(y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes', 'Y']:
            await create_test_users()
        else:
            print("\n⏭️  跳過創建測試用戶\n")
    except Exception:
        print("\n⏭️  跳過創建測試用戶\n")
    
    print("✅ 初始化完成！\n")


if __name__ == "__main__":
    asyncio.run(main())

