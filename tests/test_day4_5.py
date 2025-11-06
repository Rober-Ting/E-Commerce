"""
Day 4-5 功能測試

測試通用模型、工具函數、錯誤處理和日誌配置
"""

import pytest
from bson import ObjectId
from app.models.common import (
    ResponseModel, ErrorResponse, PaginationParams,
    PaginationMeta, success_response, error_response, paginated_response
)
from app.utils.helpers import (
    is_valid_objectid, str_to_objectid, generate_order_number,
    format_currency, mask_email, safe_divide
)
from app.middleware.error_handler import (
    APIException, NotFoundException, ValidationException
)


class TestCommonModels:
    """測試通用響應模型"""
    
    def test_success_response(self):
        """測試成功響應"""
        response = success_response(
            data={"user_id": "123"},
            message="User created"
        )
        assert response["success"] is True
        assert response["data"]["user_id"] == "123"
        assert response["message"] == "User created"
    
    def test_error_response(self):
        """測試錯誤響應"""
        response = error_response(
            code="NOT_FOUND",
            message="User not found",
            details={"user_id": "123"}
        )
        assert response["success"] is False
        assert response["error"]["code"] == "NOT_FOUND"
        assert response["error"]["message"] == "User not found"
    
    def test_pagination_params(self):
        """測試分頁參數"""
        params = PaginationParams(page=2, per_page=10)
        assert params.page == 2
        assert params.per_page == 10
        assert params.skip == 10  # (2-1) * 10
    
    def test_pagination_meta_create(self):
        """測試分頁元資料創建"""
        meta = PaginationMeta.create(page=1, per_page=20, total=100)
        assert meta.page == 1
        assert meta.per_page == 20
        assert meta.total == 100
        assert meta.total_pages == 5
        assert meta.has_next is True
        assert meta.has_prev is False
    
    def test_paginated_response(self):
        """測試分頁響應"""
        items = [{"id": "1"}, {"id": "2"}]
        response = paginated_response(
            items=items,
            page=1,
            per_page=20,
            total=100
        )
        assert response["success"] is True
        assert len(response["data"]["items"]) == 2
        assert response["data"]["pagination"]["total"] == 100


class TestHelpers:
    """測試工具函數"""
    
    def test_is_valid_objectid(self):
        """測試 ObjectId 驗證"""
        valid_id = "507f1f77bcf86cd799439011"
        assert is_valid_objectid(valid_id) is True
        assert is_valid_objectid("invalid") is False
        assert is_valid_objectid("") is False
    
    def test_str_to_objectid(self):
        """測試字串轉 ObjectId"""
        valid_id = "507f1f77bcf86cd799439011"
        oid = str_to_objectid(valid_id)
        assert oid is not None
        assert isinstance(oid, ObjectId)
        
        invalid_oid = str_to_objectid("invalid")
        assert invalid_oid is None
    
    def test_generate_order_number(self):
        """測試訂單編號生成"""
        order_num = generate_order_number("ORD")
        assert order_num.startswith("ORD")
        assert len(order_num) == 23  # ORD(3) + YYYYMMDD(8) + HHMMSS(6) + Random(6)
        
        # 生成兩個訂單號應該不同
        order_num2 = generate_order_number("ORD")
        assert order_num != order_num2
    
    def test_format_currency(self):
        """測試貨幣格式化"""
        formatted = format_currency(1234.56, "TWD")
        assert "TWD" in formatted
        assert "1,234.56" in formatted
    
    def test_mask_email(self):
        """測試 Email 遮蔽"""
        masked = mask_email("user@example.com")
        assert masked == "u***@example.com"
        
        masked2 = mask_email("ab@test.com")
        assert masked2 == "a***@test.com"
    
    def test_safe_divide(self):
        """測試安全除法"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=1.0) == 1.0


class TestErrorHandler:
    """測試錯誤處理"""
    
    def test_api_exception(self):
        """測試 API 異常"""
        exc = APIException(
            status_code=500,
            code="TEST_ERROR",
            message="Test error message"
        )
        assert exc.status_code == 500
        assert exc.code == "TEST_ERROR"
        assert exc.message == "Test error message"
    
    def test_not_found_exception(self):
        """測試資源不存在異常"""
        exc = NotFoundException(resource="User", resource_id="123")
        assert exc.status_code == 404
        assert exc.code == "NOT_FOUND"
        assert "User not found" in exc.message
        assert exc.details["id"] == "123"
    
    def test_validation_exception(self):
        """測試驗證異常"""
        exc = ValidationException(
            message="Invalid data",
            details={"field": "email"}
        )
        assert exc.status_code == 422
        assert exc.code == "VALIDATION_ERROR"
        assert exc.message == "Invalid data"


def test_imports():
    """測試所有模組可以正常導入"""
    # 這個測試確保所有新模組都能正確導入
    from app.models import common
    from app.utils import helpers
    from app.utils import logging_config
    from app.middleware import error_handler
    
    assert common is not None
    assert helpers is not None
    assert logging_config is not None
    assert error_handler is not None


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v"])

