# 🧪 Pytest 完整使用指南

## 📚 什么是 Pytest？

Pytest 是 Python 最流行的测试框架，它让编写和运行测试变得**简单且强大**。

### 为什么要写测试？
- ✅ 确保代码正常工作
- ✅ 防止修改代码时破坏现有功能
- ✅ 作为代码的使用文档
- ✅ 增加代码可靠性和信心

---

## 🚀 快速开始

### 1. 确保已安装 pytest

```powershell
# 激活虚拟环境
.\venv\Scripts\activate

# 检查 pytest 是否安装
pytest --version

# 如果没有，安装它
pip install pytest
```

### 2. 运行测试的基本命令

```powershell
# 运行所有测试
pytest

# 运行特定文件的测试
pytest tests/test_day4_5.py

# 详细模式（显示每个测试的名称）
pytest tests/test_day4_5.py -v

# 显示详细输出（包括 print）
pytest tests/test_day4_5.py -v -s

# 只运行失败的测试
pytest --lf

# 停在第一个失败的测试
pytest -x
```

---

## 📖 理解 test_day4_5.py 文件结构

### 文件开头：导入模块

```python
"""
Day 4-5 功能測試
測試通用模型、工具函數、錯誤處理和日誌配置
"""

import pytest  # 导入 pytest 框架
from bson import ObjectId  # MongoDB 的 ObjectId
from app.models.common import (  # 导入要测试的模型
    ResponseModel, ErrorResponse, PaginationParams,
    PaginationMeta, success_response, error_response, paginated_response
)
```

**说明：**
- 三引号文档字符串：描述这个测试文件的用途
- `import pytest`：导入测试框架
- `from app.xxx import xxx`：导入你要测试的代码

---

## 🔍 详细解析：测试类和测试函数

### 结构 1：测试类（Test Class）

```python
class TestCommonModels:
    """測試通用響應模型"""
```

**为什么用类？**
- 📦 组织相关的测试
- 🏷️ 清晰的分类
- 🔄 共享测试设置（如果需要）

**命名规则：**
- ✅ 类名必须以 `Test` 开头（大写 T）
- ✅ 例如：`TestCommonModels`, `TestHelpers`, `TestErrorHandler`

---

### 结构 2：测试函数（Test Function）

```python
def test_success_response(self):
    """測試成功響應"""
    # 1. 准备（Arrange）- 设置测试数据
    response = success_response(
        data={"user_id": "123"},
        message="User created"
    )
    
    # 2. 执行（Act）- 已在上面完成
    
    # 3. 断言（Assert）- 验证结果
    assert response["success"] is True
    assert response["data"]["user_id"] == "123"
    assert response["message"] == "User created"
```

**AAA 模式（Arrange-Act-Assert）：**
1. **Arrange（准备）**: 设置测试所需的数据和环境
2. **Act（执行）**: 执行要测试的代码
3. **Assert（断言）**: 验证结果是否符合预期

**命名规则：**
- ✅ 函数名必须以 `test_` 开头（小写 t）
- ✅ 名称要描述性强：`test_什么功能`
- ✅ 例如：`test_success_response`, `test_generate_order_number`

---

## 🎯 Assert 断言详解

断言是测试的核心，用来验证结果是否正确。

### 基本断言

```python
# 1. 相等性断言
assert response["success"] is True
assert user_id == "123"
assert len(items) == 2

# 2. 不等性断言
assert order_num != order_num2  # 两个值不相等

# 3. 包含性断言
assert "TWD" in formatted  # 字符串包含
assert user in user_list   # 列表包含

# 4. 类型断言
assert isinstance(oid, ObjectId)  # 检查类型

# 5. 布尔断言
assert is_valid_objectid(valid_id) is True
assert meta.has_next is True
```

### 断言失败时会发生什么？

```python
# 例如这个断言失败：
assert response["success"] is True

# Pytest 会显示：
# AssertionError: assert False is True
#   where False = response["success"]
```

**Pytest 会自动显示：**
- ❌ 哪一行失败了
- ❌ 期望值是什么
- ❌ 实际值是什么

---

## 📝 逐行解析测试示例

### 示例 1：测试成功响应

```python
def test_success_response(self):
    """測試成功響應"""
    # 步骤 1：调用函数，创建响应
    response = success_response(
        data={"user_id": "123"},
        message="User created"
    )
    
    # 步骤 2：验证响应的各个部分
    assert response["success"] is True        # 检查 success 字段
    assert response["data"]["user_id"] == "123"  # 检查数据内容
    assert response["message"] == "User created" # 检查消息
```

**这个测试在检查什么？**
- ✅ `success_response()` 函数能正常工作
- ✅ 返回的格式正确
- ✅ 数据内容符合预期

---

### 示例 2：测试分页参数

```python
def test_pagination_params(self):
    """測試分頁參數"""
    # 步骤 1：创建分页参数对象
    params = PaginationParams(page=2, per_page=10)
    
    # 步骤 2：验证属性值
    assert params.page == 2           # 页码是 2
    assert params.per_page == 10      # 每页 10 条
    assert params.skip == 10          # 跳过 10 条（计算属性）
    #                                 # skip = (page - 1) * per_page
    #                                 # skip = (2 - 1) * 10 = 10
```

**这个测试在检查什么？**
- ✅ `PaginationParams` 类能正常创建
- ✅ 属性值正确赋值
- ✅ 计算属性 `skip` 的逻辑正确

---

### 示例 3：测试 ObjectId 验证

```python
def test_is_valid_objectid(self):
    """測試 ObjectId 驗證"""
    # 步骤 1：准备测试数据
    valid_id = "507f1f77bcf86cd799439011"  # 有效的 ObjectId
    
    # 步骤 2：测试有效的 ID
    assert is_valid_objectid(valid_id) is True
    
    # 步骤 3：测试无效的 ID
    assert is_valid_objectid("invalid") is False
    assert is_valid_objectid("") is False
```

**这个测试在检查什么？**
- ✅ 有效的 ObjectId 能被正确识别
- ✅ 无效的字符串返回 False
- ✅ 空字符串也返回 False
- ✅ 边界情况都被考虑到

---

### 示例 4：测试订单编号生成

```python
def test_generate_order_number(self):
    """測試訂單編號生成"""
    # 步骤 1：生成第一个订单号
    order_num = generate_order_number("ORD")
    
    # 步骤 2：验证格式
    assert order_num.startswith("ORD")  # 以 ORD 开头
    assert len(order_num) == 23         # 总长度是 23
    #      ORD(3) + YYYYMMDD(8) + HHMMSS(6) + Random(6) = 23
    
    # 步骤 3：生成第二个订单号
    order_num2 = generate_order_number("ORD")
    
    # 步骤 4：验证唯一性
    assert order_num != order_num2  # 两个订单号应该不同
```

**这个测试在检查什么？**
- ✅ 订单号格式正确
- ✅ 长度符合预期
- ✅ 每次生成的订单号都是唯一的

---

### 示例 5：测试异常类

```python
def test_not_found_exception(self):
    """測試資源不存在異常"""
    # 步骤 1：创建异常实例
    exc = NotFoundException(resource="User", resource_id="123")
    
    # 步骤 2：验证异常属性
    assert exc.status_code == 404           # HTTP 状态码
    assert exc.code == "NOT_FOUND"          # 错误代码
    assert "User not found" in exc.message  # 错误消息
    assert exc.details["id"] == "123"       # 详细信息
```

**这个测试在检查什么？**
- ✅ 异常类能正确创建
- ✅ 状态码是 404
- ✅ 错误信息包含资源名称
- ✅ 详细信息正确传递

---

## 🎮 实战：运行测试

### 步骤 1：激活虚拟环境

```powershell
# 在项目根目录
.\venv\Scripts\activate
```

### 步骤 2：运行所有测试

```powershell
pytest tests/test_day4_5.py -v
```

### 预期输出：

```
====================================== test session starts ======================================
platform win32 -- Python 3.12.9, pytest-8.3.4, pluggy-1.6.0
collected 15 items

tests/test_day4_5.py::TestCommonModels::test_success_response PASSED                    [  6%]
tests/test_day4_5.py::TestCommonModels::test_error_response PASSED                      [ 13%]
tests/test_day4_5.py::TestCommonModels::test_pagination_params PASSED                   [ 20%]
tests/test_day4_5.py::TestCommonModels::test_pagination_meta_create PASSED              [ 26%]
tests/test_day4_5.py::TestCommonModels::test_paginated_response PASSED                  [ 33%]
tests/test_day4_5.py::TestHelpers::test_is_valid_objectid PASSED                        [ 40%]
tests/test_day4_5.py::TestHelpers::test_str_to_objectid PASSED                          [ 46%]
tests/test_day4_5.py::TestHelpers::test_generate_order_number PASSED                    [ 53%]
tests/test_day4_5.py::TestHelpers::test_format_currency PASSED                          [ 60%]
tests/test_day4_5.py::TestHelpers::test_mask_email PASSED                               [ 66%]
tests/test_day4_5.py::TestHelpers::test_safe_divide PASSED                              [ 73%]
tests/test_day4_5.py::TestErrorHandler::test_api_exception PASSED                       [ 80%]
tests/test_day4_5.py::TestErrorHandler::test_not_found_exception PASSED                 [ 86%]
tests/test_day4_5.py::TestErrorHandler::test_validation_exception PASSED                [ 93%]
tests/test_day4_5.py::test_imports PASSED                                               [100%]

====================================== 15 passed in 6.83s ======================================
```

### 理解输出：

- **`collected 15 items`**: 发现了 15 个测试
- **`PASSED`**: ✅ 测试通过
- **`[ 6%]`**: 进度百分比
- **`15 passed in 6.83s`**: 15 个全部通过，耗时 6.83 秒

---

## ❌ 当测试失败时

### 假设我们故意制造一个错误：

```python
def test_success_response(self):
    response = success_response(
        data={"user_id": "123"},
        message="User created"
    )
    assert response["success"] is False  # ❌ 故意写错
```

### 运行测试会看到：

```
FAILED tests/test_day4_5.py::TestCommonModels::test_success_response - AssertionError

================================= FAILURES =================================
________ TestCommonModels.test_success_response ________

self = <tests.test_day4_5.TestCommonModels object at 0x...>

    def test_success_response(self):
        response = success_response(
            data={"user_id": "123"},
            message="User created"
        )
>       assert response["success"] is False
E       assert True is False

tests/test_day4_5.py:32: AssertionError
```

**Pytest 告诉你：**
- ❌ 哪个测试失败了
- ❌ 在哪一行失败
- ❌ 期望值是什么（False）
- ❌ 实际值是什么（True）

---

## 🎯 运行特定测试的技巧

### 1. 运行单个测试类

```powershell
pytest tests/test_day4_5.py::TestHelpers -v
# 只运行 TestHelpers 类中的所有测试
```

### 2. 运行单个测试函数

```powershell
pytest tests/test_day4_5.py::TestHelpers::test_generate_order_number -v
# 只运行订单号生成测试
```

### 3. 使用关键字过滤

```powershell
pytest tests/test_day4_5.py -k "objectid" -v
# 运行所有名称包含 "objectid" 的测试
```

### 4. 显示 print 输出

```powershell
pytest tests/test_day4_5.py -v -s
# -s 参数会显示 print() 的内容
```

---

## 💡 自己写测试的技巧

### 技巧 1：从简单开始

```python
def test_my_first_test(self):
    """我的第一个测试"""
    # 测试一个简单的加法
    result = 1 + 1
    assert result == 2
```

### 技巧 2：测试边界情况

```python
def test_divide_by_zero(self):
    """测试除以零的情况"""
    result = safe_divide(10, 0)
    assert result == 0.0  # 应该返回默认值
```

### 技巧 3：测试异常

```python
def test_invalid_input_raises_exception(self):
    """测试无效输入会抛出异常"""
    with pytest.raises(ValidationException):
        # 这里的代码应该抛出 ValidationException
        validate_user_data({"email": "invalid"})
```

### 技巧 4：使用参数化测试

```python
@pytest.mark.parametrize("input_id,expected", [
    ("507f1f77bcf86cd799439011", True),   # 有效 ID
    ("invalid", False),                    # 无效 ID
    ("", False),                           # 空字符串
])
def test_objectid_validation(input_id, expected):
    """参数化测试多个输入"""
    result = is_valid_objectid(input_id)
    assert result == expected
```

---

## 📊 测试覆盖率

### 查看哪些代码被测试覆盖了：

```powershell
# 安装 pytest-cov
pip install pytest-cov

# 运行测试并显示覆盖率
pytest tests/test_day4_5.py --cov=app --cov-report=html

# 会生成 htmlcov/index.html，用浏览器打开查看
```

---

## 🎓 测试的最佳实践

### ✅ 好的测试特征：

1. **快速（Fast）**: 测试应该很快完成
2. **独立（Independent）**: 测试之间不应该相互依赖
3. **可重复（Repeatable）**: 每次运行结果应该一致
4. **自验证（Self-Validating）**: 自动判断通过或失败
5. **及时（Timely）**: 在写代码的同时写测试

### ❌ 要避免的：

- ❌ 测试太复杂，难以理解
- ❌ 测试依赖外部服务（如真实数据库）
- ❌ 测试之间有依赖关系
- ❌ 测试名称不清晰

---

## 🚀 实战练习

### 练习 1：运行现有测试

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 运行所有测试
pytest tests/test_day4_5.py -v

# 3. 只运行 TestHelpers
pytest tests/test_day4_5.py::TestHelpers -v

# 4. 运行并显示详细输出
pytest tests/test_day4_5.py -v -s
```

### 练习 2：修改测试观察失败

1. 打开 `tests/test_day4_5.py`
2. 找到 `test_mask_email` 函数
3. 修改断言：`assert masked == "wrong_value"`
4. 运行测试，观察错误信息
5. 改回正确的值

### 练习 3：添加自己的测试

在 `tests/test_day4_5.py` 最后添加：

```python
class TestMyOwnTests:
    """我自己的测试"""
    
    def test_truncate_text(self):
        """测试文字截断功能"""
        from app.utils.helpers import truncate_text
        
        # 测试短文本（不需要截断）
        result = truncate_text("Hello", max_length=10)
        assert result == "Hello"
        
        # 测试长文本（需要截断）
        result = truncate_text("This is a long text", max_length=10)
        assert result == "This is..."
        assert len(result) == 10
```

然后运行：
```powershell
pytest tests/test_day4_5.py::TestMyOwnTests -v
```

---

## 📚 更多资源

### Pytest 官方文档
- https://docs.pytest.org/

### 常用命令速查

| 命令 | 说明 |
|------|------|
| `pytest` | 运行所有测试 |
| `pytest -v` | 详细模式 |
| `pytest -s` | 显示 print 输出 |
| `pytest -x` | 遇到失败就停止 |
| `pytest --lf` | 只运行上次失败的测试 |
| `pytest -k "关键字"` | 运行包含关键字的测试 |
| `pytest --collect-only` | 列出所有测试但不运行 |

---

## 🎉 总结

**你已经学会了：**
- ✅ Pytest 的基本概念
- ✅ 测试的 AAA 模式
- ✅ 如何运行测试
- ✅ 如何理解测试结果
- ✅ 如何读懂现有测试
- ✅ 如何编写自己的测试

**下一步：**
1. 自己运行 `pytest tests/test_day4_5.py -v`
2. 观察每个测试的结果
3. 尝试修改一个测试看看失败是什么样子
4. 尝试添加一个新的测试

Happy Testing! 🧪✨

