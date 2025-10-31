"""
MongoDB 資料庫連線管理

使用 Motor (異步 PyMongo) 連接 MongoDB
提供資料庫連線的生命週期管理
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """資料庫連線管理類別"""
    
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


# 建立全域資料庫實例
db = Database()


async def connect_to_mongo():
    """
    建立 MongoDB 連線
    
    在應用程式啟動時呼叫
    """
    try:
        logger.info(f"正在連接 MongoDB: {settings.MONGODB_URL}")
        logger.debug("步驟 1/4: 建立 AsyncIOMotorClient 實例...")
        
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        logger.debug(f"  ✓ 客戶端建立完成: {type(db.client)}")
        
        logger.debug(f"步驟 2/4: 選擇資料庫 '{settings.MONGODB_DB_NAME}'...")
        db.db = db.client[settings.MONGODB_DB_NAME]
        logger.debug(f"  ✓ 資料庫實例: {db.db.name}")
        
        logger.debug("步驟 3/4: 執行 ping 命令測試連線...")
        ping_result = await db.client.admin.command('ping')
        logger.debug(f"  ✓ Ping 回應: {ping_result}")
        
        logger.debug("步驟 4/4: 獲取伺服器資訊...")
        server_info = await db.client.server_info()
        logger.debug(f"  ✓ MongoDB 版本: {server_info.get('version', 'unknown')}")
        logger.debug(f"  ✓ 伺服器位址: {db.client.address}")
        
        logger.info(f"✅ 成功連接到 MongoDB 資料庫: {settings.MONGODB_DB_NAME}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB 連線失敗: {str(e)}")
        logger.debug(f"錯誤類型: {type(e).__name__}")
        logger.debug(f"錯誤詳情: {e}", exc_info=True)
        raise


async def close_mongo_connection():
    """
    關閉 MongoDB 連線
    
    在應用程式關閉時呼叫
    """
    try:
        logger.debug("檢查是否有活動的資料庫連線...")
        if db.client:
            logger.debug(f"找到活動連線: {db.client.address}")
            logger.debug("正在關閉客戶端連線...")
            db.client.close()
            logger.debug("✓ 客戶端連線已關閉")
            logger.info("MongoDB 連線已關閉")
        else:
            logger.debug("沒有活動的資料庫連線")
    except Exception as e:
        logger.error(f"關閉 MongoDB 連線時發生錯誤: {str(e)}")
        logger.debug(f"錯誤詳情: {e}", exc_info=True)


def get_database() -> AsyncIOMotorDatabase:
    """
    獲取資料庫實例
    
    用於依賴注入
    
    Returns:
        AsyncIOMotorDatabase: MongoDB 資料庫實例
    """
    return db.db

