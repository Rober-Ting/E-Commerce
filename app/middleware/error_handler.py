"""
錯誤處理中介軟體

統一處理 API 錯誤和異常，提供一致的錯誤回應格式
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import PyMongoError
from pydantic import ValidationError
import logging
from typing import Union

logger = logging.getLogger(__name__)


class APIException(Exception):
    """
    自定義 API 異常基礎類別
    
    所有業務邏輯相關的異常都應該繼承此類別
    
    Attributes:
        status_code: HTTP 狀態碼
        code: 錯誤代碼（用於程式判斷）
        message: 錯誤訊息（給用戶看的）
        details: 額外的錯誤細節
    
    Examples:
        >>> raise APIException(
        ...     status_code=404,
        ...     code="USER_NOT_FOUND",
        ...     message="User not found",
        ...     details={"user_id": "123"}
        ... )
    """
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        message: str = "An internal error occurred",
        details: dict = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# 常用的業務異常類別

class NotFoundException(APIException):
    """資源不存在異常"""
    
    def __init__(self, resource: str = "Resource", resource_id: str = None):
        message = f"{resource} not found"
        details = {"resource": resource}
        if resource_id:
            details["id"] = resource_id
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details
        )


class AlreadyExistsException(APIException):
    """資源已存在異常"""
    
    def __init__(self, resource: str = "Resource", field: str = None, value: str = None):
        message = f"{resource} already exists"
        details = {"resource": resource}
        if field and value:
            details["field"] = field
            details["value"] = value
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="ALREADY_EXISTS",
            message=message,
            details=details
        )


class UnauthorizedException(APIException):
    """未授權異常"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message
        )


class ForbiddenException(APIException):
    """權限不足異常"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message
        )


class ValidationException(APIException):
    """資料驗證失敗異常"""
    
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details or {}
        )


class BadRequestException(APIException):
    """錯誤請求異常"""
    
    def __init__(self, message: str = "Bad request", details: dict = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            message=message,
            details=details or {}
        )


class DatabaseException(APIException):
    """資料庫錯誤異常"""
    
    def __init__(self, message: str = "Database operation failed", details: dict = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message,
            details=details or {}
        )


# 異常處理函數

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    處理自定義 API 異常
    
    Args:
        request: FastAPI 請求對象
        exc: API 異常實例
    
    Returns:
        JSONResponse: 格式化的錯誤回應
    """
    logger.warning(
        f"API Exception: {exc.code} - {exc.message} | "
        f"Path: {request.url.path} | Details: {exc.details}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    處理 HTTP 異常（Starlette/FastAPI 內建異常）
    
    Args:
        request: FastAPI 請求對象
        exc: HTTP 異常實例
    
    Returns:
        JSONResponse: 格式化的錯誤回應
    """
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} | "
        f"Path: {request.url.path}"
    )
    
    # 根據狀態碼映射錯誤代碼
    code_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = code_mapping.get(exc.status_code, "HTTP_ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": exc.detail,
                "details": {}
            }
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    處理請求驗證錯誤（Pydantic 驗證失敗）
    
    Args:
        request: FastAPI 請求對象
        exc: 驗證錯誤實例
    
    Returns:
        JSONResponse: 格式化的錯誤回應
    """
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)
    
    logger.warning(
        f"Validation Error: Path: {request.url.path} | "
        f"Errors: {errors}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": errors
                }
            }
        }
    )


async def pymongo_exception_handler(
    request: Request,
    exc: PyMongoError
) -> JSONResponse:
    """
    處理 PyMongo 資料庫錯誤
    
    Args:
        request: FastAPI 請求對象
        exc: PyMongo 錯誤實例
    
    Returns:
        JSONResponse: 格式化的錯誤回應
    """
    logger.error(
        f"Database Error: {str(exc)} | "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred",
                "details": {
                    "error_type": type(exc).__name__
                }
            }
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    處理所有未捕獲的異常（兜底處理）
    
    Args:
        request: FastAPI 請求對象
        exc: 異常實例
    
    Returns:
        JSONResponse: 格式化的錯誤回應
    """
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)} | "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "error_type": type(exc).__name__
                }
            }
        }
    )


def register_exception_handlers(app):
    """
    註冊所有異常處理器到 FastAPI 應用
    
    Args:
        app: FastAPI 應用實例
    
    Usage:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> register_exception_handlers(app)
    """
    # 自定義 API 異常
    app.add_exception_handler(APIException, api_exception_handler)
    
    # HTTP 異常
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 驗證錯誤
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # 資料庫錯誤
    app.add_exception_handler(PyMongoError, pymongo_exception_handler)
    
    # 通用異常（兜底）
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("✅ 異常處理器註冊完成")

