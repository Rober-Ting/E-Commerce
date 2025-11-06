"""
FastAPI 應用程式主入口

電商訂單管理系統 API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.config import settings
from app.utils.logging_config import setup_logging, get_logger
from app.middleware.error_handler import register_exception_handlers
from app.models.common import ResponseModel, success_response

# 設定日誌系統
setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    log_file="ecommerce_api.log",
    console=True,
    log_dir="logs"
)

logger = get_logger(__name__)

logger.debug("=" * 80)
logger.debug("開始載入 FastAPI 應用模組")
logger.debug(f"當前設定 - DEBUG: {settings.DEBUG}")
logger.debug(f"當前設定 - PROJECT_NAME: {settings.PROJECT_NAME}")
logger.debug(f"當前設定 - MONGODB_URL: {settings.MONGODB_URL}")
logger.debug(f"當前設定 - MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
logger.debug("=" * 80)

# 建立 FastAPI 應用實例
logger.debug("正在建立 FastAPI 應用實例...")
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="MongoDB 電商訂單管理系統 API - 提供用戶管理、商品管理、訂單處理和數據分析功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
logger.debug(f"✅ FastAPI 應用實例建立完成: {app.title} v{app.version}")

# 註冊異常處理器
logger.debug("正在註冊異常處理器...")
register_exception_handlers(app)

# CORS 中介軟體設定
logger.debug("正在設定 CORS 中介軟體...")
allowed_origins = settings.allowed_origins_list if not settings.DEBUG else ["*"]
logger.debug(f"允許的來源: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("✅ CORS 中介軟體設定完成")


@app.on_event("startup")
async def startup_event():
    """
    應用程式啟動事件
    
    - 連接 MongoDB 資料庫
    - 初始化其他資源
    """
    logger.info("=" * 80)
    logger.info("🚀 應用程式啟動事件觸發")
    logger.info("=" * 80)
    logger.debug("步驟 1/3: 準備連接 MongoDB...")
    
    await connect_to_mongo()
    
    logger.debug("步驟 2/3: 驗證資料庫連線...")
    from app.database import db
    if db.client is not None and db.db is not None:
        logger.debug(f"  ✓ 資料庫客戶端: {db.client}")
        logger.debug(f"  ✓ 資料庫實例: {db.db.name}")
    
    logger.debug("步驟 3/3: 初始化完成")
    logger.info("✅ 應用程式啟動完成")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    應用程式關閉事件
    
    - 關閉 MongoDB 連線
    - 清理資源
    """
    logger.info("=" * 80)
    logger.info("⏹ 應用程式關閉事件觸發")
    logger.info("=" * 80)
    logger.debug("正在關閉 MongoDB 連線...")
    
    await close_mongo_connection()
    
    logger.debug("清理完成")
    logger.info("✅ 應用程式已關閉")
    logger.info("=" * 80)


@app.get("/", tags=["Root"], response_model=ResponseModel)
async def root():
    """
    根路由 - 歡迎訊息和 API 資訊
    
    Returns:
        ResponseModel: 包含 API 基本資訊的標準回應
    """
    logger.debug("收到根路由請求 GET /")
    
    data = {
        "message": "歡迎使用電商訂單管理系統 API",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "db_info": "/db-info"
    }
    
    logger.debug(f"返回根路由回應: {data['message']}")
    return success_response(data=data, message="Welcome to E-Commerce API")


@app.get("/health", tags=["Health"], response_model=ResponseModel)
async def health_check():
    """
    健康檢查端點
    
    用於確認 API 服務和資料庫是否正常運行
    
    Returns:
        ResponseModel: 服務健康狀態資訊
    """
    logger.debug("收到健康檢查請求 GET /health")
    
    # 檢查資料庫連線
    from app.database import db
    db_status = "connected"
    db_ping_success = False
    
    try:
        logger.debug("正在驗證資料庫連線...")
        await db.client.admin.command('ping')
        db_ping_success = True
        logger.debug("✓ 資料庫連線正常")
    except Exception as e:
        db_status = "disconnected"
        logger.warning(f"✗ 資料庫連線失敗: {e}")
    
    is_healthy = db_ping_success
    
    data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "service": settings.PROJECT_NAME,
        "database": {
            "status": db_status,
            "ping_successful": db_ping_success
        }
    }
    
    message = "Service is healthy" if is_healthy else "Service is unhealthy"
    logger.debug(f"返回健康檢查回應: {message}")
    
    return success_response(data=data, message=message)
    
@app.get("/db-info", tags=["Database"], response_model=ResponseModel)
async def database_info():
    """
    資料庫資訊端點
    
    獲取 MongoDB 版本、資料庫和集合資訊
    
    Returns:
        ResponseModel: 資料庫詳細資訊
    
    Raises:
        DatabaseException: 當資料庫操作失敗時
    """
    from app.database import db
    from app.middleware.error_handler import DatabaseException
    
    try:
        logger.debug("正在獲取資料庫資訊...")
        
        # 獲取伺服器資訊
        server_info = await db.client.server_info()
        
        # 列出所有資料庫
        db_list = await db.client.list_database_names()
        
        # 獲取當前資料庫的集合
        collections = await db.db.list_collection_names()
        
        data = {
            "mongodb_version": server_info.get("version"),
            "current_database": settings.MONGODB_DB_NAME,
            "total_databases": len(db_list),
            "database_list": db_list,
            "collections_in_current_db": collections,
            "total_collections": len(collections)
        }
        
        logger.debug(f"✓ 成功獲取資料庫資訊: MongoDB {data['mongodb_version']}")
        return success_response(data=data, message="Database information retrieved successfully")
        
    except Exception as e:
        logger.error(f"✗ 獲取資料庫資訊失敗: {str(e)}")
        raise DatabaseException(
            message="Failed to retrieve database information",
            details={"error": str(e)}
        )

# 這裡之後會加入 API 路由
# from app.api.v1 import auth, users, products, orders, analytics
# app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
# app.include_router(users.router, prefix=settings.API_V1_PREFIX)
# app.include_router(products.router, prefix=settings.API_V1_PREFIX)
# app.include_router(orders.router, prefix=settings.API_V1_PREFIX)
# app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)

