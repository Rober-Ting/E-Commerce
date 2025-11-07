"""
應用程式配置管理

使用 Pydantic BaseSettings 管理環境變數
從 .env 檔案讀取配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """應用程式設定類別"""
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ecommerce_db"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "E-Commerce API"
    DEBUG: bool = True
    
    # 日誌配置
    LOG_LEVEL: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # CORS 配置
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # 分頁配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # 用戶配置
    DEFAULT_USER_ROLE: str = "customer"
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_EMAIL_VERIFICATION: bool = False  # 是否需要郵箱驗證
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def allowed_origins_list(self) -> list:
        """將 ALLOWED_ORIGINS 字串轉換為列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# 建立全域設定實例
settings = Settings()

