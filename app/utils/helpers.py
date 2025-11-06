"""
工具輔助函數

提供常用的工具函數，包括 ObjectId 處理、訂單編號生成等
"""

from datetime import datetime, timezone
from typing import Optional, Any
from bson import ObjectId as BsonObjectId
from bson.errors import InvalidId
import secrets
import string


def is_valid_objectid(oid: str) -> bool:
    """
    驗證字串是否為有效的 MongoDB ObjectId
    
    Args:
        oid: 要驗證的字串
    
    Returns:
        bool: 是否為有效的 ObjectId
    
    Examples:
        >>> is_valid_objectid("507f1f77bcf86cd799439011")
        True
        >>> is_valid_objectid("invalid")
        False
    """
    try:
        BsonObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


def str_to_objectid(oid: str) -> Optional[BsonObjectId]:
    """
    將字串轉換為 ObjectId
    
    Args:
        oid: ObjectId 字串
    
    Returns:
        Optional[BsonObjectId]: 轉換成功返回 ObjectId，失敗返回 None
    
    Examples:
        >>> str_to_objectid("507f1f77bcf86cd799439011")
        ObjectId('507f1f77bcf86cd799439011')
        >>> str_to_objectid("invalid")
        None
    """
    try:
        return BsonObjectId(oid)
    except (InvalidId, TypeError):
        return None


def objectid_to_str(oid: BsonObjectId) -> str:
    """
    將 ObjectId 轉換為字串
    
    Args:
        oid: ObjectId 實例
    
    Returns:
        str: ObjectId 的字串表示
    
    Examples:
        >>> from bson import ObjectId
        >>> oid = ObjectId("507f1f77bcf86cd799439011")
        >>> objectid_to_str(oid)
        '507f1f77bcf86cd799439011'
    """
    return str(oid)


def convert_objectid_fields(doc: dict, fields: list = None) -> dict:
    """
    轉換文檔中的 ObjectId 欄位為字串
    
    Args:
        doc: MongoDB 文檔
        fields: 要轉換的欄位列表，None 表示只轉換 _id
    
    Returns:
        dict: 轉換後的文檔
    
    Examples:
        >>> doc = {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Test"}
        >>> convert_objectid_fields(doc)
        {"_id": "507f1f77bcf86cd799439011", "name": "Test"}
    """
    if not doc:
        return doc
    
    result = doc.copy()
    
    # 預設只轉換 _id
    if fields is None:
        fields = ['_id']
    
    for field in fields:
        if field in result and isinstance(result[field], BsonObjectId):
            result[field] = str(result[field])
    
    return result


def generate_order_number(prefix: str = "ORD") -> str:
    """
    生成唯一的訂單編號
    
    格式: {PREFIX}{YYYYMMDD}{HHMMSS}{隨機6位數字}
    例如: ORD202510311430001A2B3C
    
    Args:
        prefix: 訂單編號前綴（預設為 "ORD"）
    
    Returns:
        str: 唯一的訂單編號
    
    Examples:
        >>> order_num = generate_order_number("ORD")
        >>> order_num.startswith("ORD")
        True
        >>> len(order_num)
        23  # ORD(3) + YYYYMMDD(8) + HHMMSS(6) + Random(6)
    """
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M%S")
    
    # 生成 6 位隨機字母數字組合
    random_part = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )
    
    return f"{prefix}{date_part}{time_part}{random_part}"


def generate_transaction_id(prefix: str = "TXN") -> str:
    """
    生成唯一的交易 ID
    
    格式: {PREFIX}{YYYYMMDD}{HHMMSS}{隨機8位數字}
    
    Args:
        prefix: 交易 ID 前綴（預設為 "TXN"）
    
    Returns:
        str: 唯一的交易 ID
    
    Examples:
        >>> txn_id = generate_transaction_id("TXN")
        >>> txn_id.startswith("TXN")
        True
    """
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M%S")
    
    # 生成 8 位隨機字母數字組合
    random_part = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(8)
    )
    
    return f"{prefix}{date_part}{time_part}{random_part}"


def get_utc_now() -> datetime:
    """
    獲取當前 UTC 時間（帶時區資訊）
    
    Returns:
        datetime: 當前 UTC 時間
    
    Examples:
        >>> now = get_utc_now()
        >>> now.tzinfo is not None
        True
    """
    return datetime.now(timezone.utc)


def format_currency(amount: float, currency: str = "TWD") -> str:
    """
    格式化貨幣金額
    
    Args:
        amount: 金額
        currency: 貨幣代碼（預設為 TWD）
    
    Returns:
        str: 格式化後的金額字串
    
    Examples:
        >>> format_currency(1234.56, "TWD")
        'TWD 1,234.56'
        >>> format_currency(1000000, "USD")
        'USD 1,000,000.00'
    """
    formatted_amount = f"{amount:,.2f}"
    return f"{currency} {formatted_amount}"


def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    清理和截斷字串
    
    移除前後空白並限制長度
    
    Args:
        text: 要清理的文字
        max_length: 最大長度
    
    Returns:
        str: 清理後的文字
    
    Examples:
        >>> sanitize_string("  Hello World  ")
        'Hello World'
        >>> sanitize_string("A" * 300, max_length=10)
        'AAAAAAAAAA'
    """
    if not text:
        return ""
    
    cleaned = text.strip()
    if len(cleaned) > max_length:
        return cleaned[:max_length]
    return cleaned


def calculate_pagination_offset(page: int, per_page: int) -> int:
    """
    計算分頁偏移量
    
    Args:
        page: 頁碼（從 1 開始）
        per_page: 每頁數量
    
    Returns:
        int: 要跳過的筆數
    
    Examples:
        >>> calculate_pagination_offset(1, 20)
        0
        >>> calculate_pagination_offset(3, 20)
        40
    """
    return (page - 1) * per_page


def calculate_total_pages(total: int, per_page: int) -> int:
    """
    計算總頁數
    
    Args:
        total: 總筆數
        per_page: 每頁數量
    
    Returns:
        int: 總頁數
    
    Examples:
        >>> calculate_total_pages(100, 20)
        5
        >>> calculate_total_pages(95, 20)
        5
        >>> calculate_total_pages(0, 20)
        0
    """
    if total == 0:
        return 0
    return (total + per_page - 1) // per_page


def mask_email(email: str) -> str:
    """
    遮蔽 Email 地址（用於日誌或顯示）
    
    Args:
        email: Email 地址
    
    Returns:
        str: 遮蔽後的 Email
    
    Examples:
        >>> mask_email("user@example.com")
        'u***@example.com'
        >>> mask_email("a@test.com")
        'a***@test.com'
    """
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 1:
        masked_username = username + "***"
    else:
        masked_username = username[0] + "***"
    
    return f"{masked_username}@{domain}"


def mask_phone(phone: str, visible_digits: int = 4) -> str:
    """
    遮蔽電話號碼（用於日誌或顯示）
    
    Args:
        phone: 電話號碼
        visible_digits: 顯示最後幾位數字
    
    Returns:
        str: 遮蔽後的電話號碼
    
    Examples:
        >>> mask_phone("0912345678")
        '******5678'
        >>> mask_phone("0912345678", visible_digits=3)
        '*******678'
    """
    if not phone:
        return phone
    
    if len(phone) <= visible_digits:
        return "*" * len(phone)
    
    masked_part = "*" * (len(phone) - visible_digits)
    visible_part = phone[-visible_digits:]
    return masked_part + visible_part


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全的除法運算（避免除以零）
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 除以零時的預設值
    
    Returns:
        float: 計算結果
    
    Examples:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        0.0
        >>> safe_divide(10, 0, default=1.0)
        1.0
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截斷文字並添加後綴
    
    Args:
        text: 要截斷的文字
        max_length: 最大長度（包含後綴）
        suffix: 後綴字串
    
    Returns:
        str: 截斷後的文字
    
    Examples:
        >>> truncate_text("This is a long text", max_length=10)
        'This is...'
        >>> truncate_text("Short", max_length=10)
        'Short'
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def dict_to_snake_case(data: dict) -> dict:
    """
    將字典的鍵轉換為 snake_case
    
    Args:
        data: 輸入字典
    
    Returns:
        dict: 轉換後的字典
    
    Note:
        這是一個簡單實現，只處理簡單的轉換
    """
    import re
    
    def to_snake_case(name: str) -> str:
        # camelCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    return {to_snake_case(k): v for k, v in data.items()}


def remove_none_values(data: dict) -> dict:
    """
    移除字典中值為 None 的項目
    
    Args:
        data: 輸入字典
    
    Returns:
        dict: 清理後的字典
    
    Examples:
        >>> remove_none_values({"a": 1, "b": None, "c": "test"})
        {'a': 1, 'c': 'test'}
    """
    return {k: v for k, v in data.items() if v is not None}

