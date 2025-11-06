"""
日誌配置模組

提供統一的日誌配置，支援檔案輸出和控制台輸出
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional


# 日誌格式
DETAILED_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - '
    '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
)

SIMPLE_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

CONSOLE_FORMAT = (
    '%(levelname)-8s | %(name)-20s | %(message)s'
)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    json_format: bool = False,
    log_dir: str = "logs"
) -> None:
    """
    設定應用程式日誌系統
    
    Args:
        level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌檔案名稱（None 表示不寫入檔案）
        console: 是否輸出到控制台
        json_format: 是否使用 JSON 格式（用於日誌收集系統）
        log_dir: 日誌目錄路徑
    
    Examples:
        >>> # 基本配置：只輸出到控制台
        >>> setup_logging(level="INFO", console=True)
        
        >>> # 同時輸出到檔案和控制台
        >>> setup_logging(level="DEBUG", log_file="app.log", console=True)
        
        >>> # 生產環境：輸出到檔案，使用 JSON 格式
        >>> setup_logging(level="INFO", log_file="prod.log", json_format=True)
    """
    # 轉換日誌級別
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 取得根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除現有的 handlers
    root_logger.handlers.clear()
    
    # 設定格式
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT)
    
    console_formatter = logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT)
    
    # 控制台 handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 檔案 handler
    if log_file:
        # 確保日誌目錄存在
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        file_path = log_path / log_file
        
        # 使用 RotatingFileHandler（按大小輪轉）
        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 設定第三方庫的日誌級別（避免過於詳細）
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # 降低 pymongo 的日誌級別（避免過多心跳日誌）
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
    logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)
    
    root_logger.info(f"✅ 日誌系統初始化完成 - 級別: {level}")


def setup_daily_rotating_log(
    level: str = "INFO",
    log_name: str = "app",
    log_dir: str = "logs",
    console: bool = True,
    when: str = "midnight",
    backup_count: int = 30
) -> None:
    """
    設定每日輪轉的日誌系統
    
    Args:
        level: 日誌級別
        log_name: 日誌檔案名稱前綴
        log_dir: 日誌目錄
        console: 是否輸出到控制台
        when: 輪轉時間點 (midnight, H, D, W0-W6)
        backup_count: 保留的日誌檔案數量
    
    Examples:
        >>> # 每天午夜輪轉，保留 30 天
        >>> setup_daily_rotating_log(
        ...     level="INFO",
        ...     log_name="ecommerce",
        ...     when="midnight",
        ...     backup_count=30
        ... )
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    
    formatter = logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT)
    console_formatter = logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT)
    
    # 控制台 handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 確保日誌目錄存在
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 檔案名稱格式：app_2025-10-31.log
    file_path = log_path / f"{log_name}.log"
    
    # 使用 TimedRotatingFileHandler（按時間輪轉）
    timed_handler = TimedRotatingFileHandler(
        filename=file_path,
        when=when,
        interval=1,
        backupCount=backup_count,
        encoding='utf-8'
    )
    timed_handler.setLevel(log_level)
    timed_handler.setFormatter(formatter)
    timed_handler.suffix = "%Y-%m-%d"  # 輪轉檔案的日期格式
    root_logger.addHandler(timed_handler)
    
    # 設定第三方庫的日誌級別
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    
    root_logger.info(f"✅ 每日輪轉日誌系統初始化完成 - 級別: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    獲取指定名稱的 logger
    
    Args:
        name: Logger 名稱（通常使用 __name__）
    
    Returns:
        logging.Logger: Logger 實例
    
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is an info message")
    """
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """
    JSON 格式的日誌格式化器
    
    用於結構化日誌，方便日誌收集系統（如 ELK、Splunk）處理
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日誌記錄為 JSON
        
        Args:
            record: 日誌記錄對象
        
        Returns:
            str: JSON 格式的日誌字串
        """
        import json
        
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加異常資訊
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加額外的自定義欄位
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data, ensure_ascii=False)


class RequestIdFilter(logging.Filter):
    """
    添加請求 ID 到日誌記錄
    
    用於追蹤單個請求在系統中的所有日誌
    """
    
    def __init__(self, request_id: str = None):
        super().__init__()
        self.request_id = request_id or "N/A"
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        為日誌記錄添加 request_id 屬性
        
        Args:
            record: 日誌記錄對象
        
        Returns:
            bool: 總是返回 True（不過濾任何日誌）
        """
        record.request_id = self.request_id
        return True


def add_request_id_to_logger(logger: logging.Logger, request_id: str) -> None:
    """
    為 logger 添加請求 ID 過濾器
    
    Args:
        logger: Logger 實例
        request_id: 請求 ID
    
    Examples:
        >>> logger = get_logger(__name__)
        >>> add_request_id_to_logger(logger, "req-123-456")
        >>> logger.info("Processing request")  # 會包含 request_id
    """
    request_filter = RequestIdFilter(request_id)
    logger.addFilter(request_filter)


# 預設配置函數（用於快速啟動）

def setup_development_logging() -> None:
    """
    開發環境日誌配置
    
    特點：
    - DEBUG 級別
    - 輸出到控制台
    - 詳細格式
    """
    setup_logging(
        level="DEBUG",
        console=True,
        log_file=None
    )


def setup_production_logging() -> None:
    """
    生產環境日誌配置
    
    特點：
    - INFO 級別
    - 輸出到檔案和控制台
    - 每日輪轉，保留 30 天
    """
    setup_daily_rotating_log(
        level="INFO",
        log_name="ecommerce_prod",
        console=True,
        when="midnight",
        backup_count=30
    )


def setup_testing_logging() -> None:
    """
    測試環境日誌配置
    
    特點：
    - WARNING 級別
    - 只輸出到控制台
    - 簡化格式
    """
    setup_logging(
        level="WARNING",
        console=True,
        log_file=None
    )

