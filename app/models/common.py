"""
通用資料模型

定義整個 API 使用的通用響應模型、分頁模型和錯誤模型
"""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field


# 泛型類型變數
T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    通用 API 響應模型
    
    使用泛型支援任意資料類型的回應
    
    Attributes:
        success: 請求是否成功
        data: 實際返回的資料
        message: 額外的描述訊息
    
    Examples:
        >>> response = ResponseModel(success=True, data={"user_id": "123"}, message="User created")
        >>> response.model_dump()
        {'success': True, 'data': {'user_id': '123'}, 'message': 'User created'}
    """
    success: bool = Field(default=True, description="請求是否成功")
    data: Optional[T] = Field(default=None, description="回應資料")
    message: str = Field(default="Operation successful", description="操作結果訊息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "507f1f77bcf86cd799439011"},
                "message": "Operation successful"
            }
        }


class ErrorDetail(BaseModel):
    """
    錯誤詳細資訊
    
    Attributes:
        code: 錯誤代碼（用於程式判斷）
        message: 錯誤訊息（給用戶看的）
        details: 額外的錯誤細節
    """
    code: str = Field(..., description="錯誤代碼")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[dict] = Field(default=None, description="額外的錯誤細節")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "email", "issue": "Invalid email format"}
            }
        }


class ErrorResponse(BaseModel):
    """
    錯誤回應模型
    
    用於統一的錯誤回應格式
    
    Attributes:
        success: 固定為 False
        error: 錯誤詳細資訊
    """
    success: bool = Field(default=False, description="固定為 False")
    error: ErrorDetail = Field(..., description="錯誤詳細資訊")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Resource not found",
                    "details": {"resource": "user", "id": "123"}
                }
            }
        }


class PaginationParams(BaseModel):
    """
    分頁參數模型
    
    用於查詢列表時的分頁參數
    
    Attributes:
        page: 當前頁碼（從 1 開始）
        per_page: 每頁顯示數量
        skip: 計算得出的跳過筆數
    """
    page: int = Field(default=1, ge=1, description="頁碼（從 1 開始）")
    per_page: int = Field(default=20, ge=1, le=100, description="每頁數量（最多 100）")
    
    @property
    def skip(self) -> int:
        """計算要跳過的文檔數量"""
        return (self.page - 1) * self.per_page
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 20
            }
        }


class PaginationMeta(BaseModel):
    """
    分頁元資料
    
    用於回應中包含的分頁資訊
    
    Attributes:
        page: 當前頁碼
        per_page: 每頁數量
        total: 總筆數
        total_pages: 總頁數
        has_next: 是否有下一頁
        has_prev: 是否有上一頁
    """
    page: int = Field(..., description="當前頁碼")
    per_page: int = Field(..., description="每頁數量")
    total: int = Field(..., description="總筆數")
    total_pages: int = Field(..., description="總頁數")
    has_next: bool = Field(..., description="是否有下一頁")
    has_prev: bool = Field(..., description="是否有上一頁")
    
    @classmethod
    def create(cls, page: int, per_page: int, total: int) -> "PaginationMeta":
        """
        建立分頁元資料
        
        Args:
            page: 當前頁碼
            per_page: 每頁數量
            total: 總筆數
        
        Returns:
            PaginationMeta: 分頁元資料實例
        """
        total_pages = (total + per_page - 1) // per_page  # 向上取整
        return cls(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 20,
                "total": 100,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


class PaginatedData(BaseModel, Generic[T]):
    """
    分頁資料容器
    
    包含資料列表和分頁資訊
    
    Attributes:
        items: 資料列表
        pagination: 分頁資訊
    """
    items: List[T] = Field(default_factory=list, description="資料列表")
    pagination: PaginationMeta = Field(..., description="分頁資訊")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [{"id": "1", "name": "Item 1"}],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分頁回應模型
    
    結合 ResponseModel 和分頁資料
    
    Attributes:
        success: 請求是否成功
        data: 分頁資料（包含 items 和 pagination）
        message: 額外的描述訊息
    """
    success: bool = Field(default=True, description="請求是否成功")
    data: PaginatedData[T] = Field(..., description="分頁資料")
    message: str = Field(default="Data retrieved successfully", description="操作結果訊息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "items": [{"id": "1", "name": "Product 1"}],
                    "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "total": 100,
                        "total_pages": 5,
                        "has_next": True,
                        "has_prev": False
                    }
                },
                "message": "Data retrieved successfully"
            }
        }


# 常用的回應輔助函數
def success_response(data: Any = None, message: str = "Operation successful") -> dict:
    """
    建立成功回應
    
    Args:
        data: 要返回的資料
        message: 成功訊息
    
    Returns:
        dict: 格式化的成功回應
    
    Examples:
        >>> success_response({"user_id": "123"}, "User created")
        {'success': True, 'data': {'user_id': '123'}, 'message': 'User created'}
    """
    return {
        "success": True,
        "data": data,
        "message": message
    }


def error_response(
    code: str,
    message: str,
    details: Optional[dict] = None
) -> dict:
    """
    建立錯誤回應
    
    Args:
        code: 錯誤代碼
        message: 錯誤訊息
        details: 額外的錯誤細節
    
    Returns:
        dict: 格式化的錯誤回應
    
    Examples:
        >>> error_response("NOT_FOUND", "User not found", {"user_id": "123"})
        {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'User not found', 'details': {'user_id': '123'}}}
    """
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }


def paginated_response(
    items: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Data retrieved successfully"
) -> dict:
    """
    建立分頁回應
    
    Args:
        items: 資料列表
        page: 當前頁碼
        per_page: 每頁數量
        total: 總筆數
        message: 成功訊息
    
    Returns:
        dict: 格式化的分頁回應
    
    Examples:
        >>> paginated_response([{"id": "1"}], page=1, per_page=20, total=100)
        {
            'success': True,
            'data': {
                'items': [{'id': '1'}],
                'pagination': {...}
            },
            'message': 'Data retrieved successfully'
        }
    """
    pagination = PaginationMeta.create(page, per_page, total)
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": pagination.model_dump()
        },
        "message": message
    }

