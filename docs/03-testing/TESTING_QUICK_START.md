# 🚀 测试快速开始指南

## 🎯 三步开始测试

### 步骤 1️⃣: 激活虚拟环境

```powershell
# 在项目根目录
.\venv\Scripts\activate
```

### 步骤 2️⃣: 运行测试（三种方式任选一种）

#### 方式 A：使用快捷脚本（推荐 ⭐）

```powershell
.\run_tests.ps1
```

#### 方式 B：直接使用 pytest

```powershell
pytest tests/test_day4_5.py -v
```

#### 方式 C：交互式演示

```powershell
python test_demo.py
```

### 步骤 3️⃣: 查看结果

看到 `✅ PASSED` 就表示测试通过了！

---

## 📚 学习资源

### 1. 完整教程
📖 **PYTEST_GUIDE.md** - 详细的 pytest 使用指南
- Pytest 是什么
- 如何写测试
- 如何运行测试
- 逐行代码解析

### 2. 互动演示
🎓 **test_demo.py** - 交互式演示脚本
```powershell
python test_demo.py
```

### 3. 实际测试代码
🧪 **tests/test_day4_5.py** - 15 个实际测试
```powershell
pytest tests/test_day4_5.py -v
```

---

## 🎮 实战练习

### 练习 1：运行所有测试

```powershell
pytest tests/test_day4_5.py -v
```

**预期结果：** 看到 15 个测试全部 PASSED ✅

---

### 练习 2：运行单个测试类

```powershell
pytest tests/test_day4_5.py::TestHelpers -v
```

**预期结果：** 只运行 TestHelpers 类中的 6 个测试

---

### 练习 3：运行特定测试

```powershell
pytest tests/test_day4_5.py::TestHelpers::test_generate_order_number -v
```

**预期结果：** 只运行订单号生成测试

---

### 练习 4：查找包含关键字的测试

```powershell
pytest tests/test_day4_5.py -k "objectid" -v
```

**预期结果：** 运行所有名称包含 "objectid" 的测试

---

### 练习 5：观察测试失败

1. 打开 `tests/test_day4_5.py`
2. 找到第 116 行的 `test_mask_email`
3. 修改断言：`assert masked == "wrong_value"`  （故意写错）
4. 运行测试：`pytest tests/test_day4_5.py::TestHelpers::test_mask_email -v`
5. 观察 pytest 如何显示错误信息
6. 改回正确的值：`assert masked == "u***@example.com"`

---

## 💡 常用命令速查表

| 命令 | 说明 | 何时使用 |
|------|------|---------|
| `pytest` | 运行所有测试 | 提交代码前 |
| `pytest -v` | 详细模式 | 想看每个测试的名称 |
| `pytest -v -s` | 显示 print 输出 | 调试测试代码 |
| `pytest -x` | 遇到失败就停止 | 快速定位问题 |
| `pytest --lf` | 只运行上次失败的测试 | 修复失败后验证 |
| `pytest -k "关键字"` | 运行包含关键字的测试 | 测试特定功能 |

---

## 📖 测试文件结构解析

```python
# tests/test_day4_5.py 的结构

"""文档字符串：说明这个文件的用途"""

import pytest  # 导入 pytest

# 导入要测试的代码
from app.models.common import ResponseModel
from app.utils.helpers import is_valid_objectid

# 测试类 1：测试响应模型
class TestCommonModels:
    def test_success_response(self):  # 测试函数 1
        # 测试代码...
        pass
    
    def test_error_response(self):    # 测试函数 2
        # 测试代码...
        pass

# 测试类 2：测试工具函数
class TestHelpers:
    def test_is_valid_objectid(self):
        # 测试代码...
        pass

# 独立测试函数
def test_imports():
    # 测试代码...
    pass
```

**关键要点：**
- ✅ 测试类名以 `Test` 开头（大写 T）
- ✅ 测试函数名以 `test_` 开头（小写 t）
- ✅ 使用 `assert` 进行断言验证

---

## 🎯 测试的 3A 模式

每个测试都遵循 AAA 模式：

```python
def test_example(self):
    # 1️⃣ Arrange（准备）- 设置测试数据
    user_data = {"name": "John", "age": 30}
    
    # 2️⃣ Act（执行）- 调用要测试的函数
    result = create_user(user_data)
    
    # 3️⃣ Assert（断言）- 验证结果
    assert result["name"] == "John"
    assert result["age"] == 30
```

---

## ✅ 测试通过时的输出

```
====================================== test session starts ======================================
collected 15 items

tests/test_day4_5.py::TestCommonModels::test_success_response PASSED                    [  6%]
tests/test_day4_5.py::TestCommonModels::test_error_response PASSED                      [ 13%]
...
====================================== 15 passed in 6.83s ======================================
```

**解读：**
- `collected 15 items` → 找到 15 个测试
- `PASSED` → ✅ 测试通过
- `[ 6%]` → 进度百分比
- `15 passed in 6.83s` → 全部通过，耗时 6.83 秒

---

## ❌ 测试失败时的输出

```
FAILED tests/test_day4_5.py::TestHelpers::test_mask_email - AssertionError

================================= FAILURES =================================
________ TestHelpers.test_mask_email ________

    def test_mask_email(self):
        masked = mask_email("user@example.com")
>       assert masked == "wrong_value"
E       AssertionError: assert 'u***@example.com' == 'wrong_value'

tests/test_day4_5.py:116: AssertionError
```

**解读：**
- `FAILED` → ❌ 测试失败
- 显示失败的测试名称
- 显示失败的代码行
- 显示期望值和实际值的差异

---

## 🎓 进阶技巧

### 1. 参数化测试（测试多组数据）

```python
@pytest.mark.parametrize("input,expected", [
    ("507f1f77bcf86cd799439011", True),   # 测试数据 1
    ("invalid", False),                    # 测试数据 2
    ("", False),                           # 测试数据 3
])
def test_objectid_validation(input, expected):
    result = is_valid_objectid(input)
    assert result == expected
```

### 2. 测试异常

```python
def test_raises_exception(self):
    """测试函数应该抛出异常"""
    with pytest.raises(ValueError):
        # 这里的代码应该抛出 ValueError
        int("not a number")
```

### 3. 使用 fixture（共享测试数据）

```python
@pytest.fixture
def sample_user():
    """创建测试用户数据"""
    return {"name": "John", "email": "john@example.com"}

def test_create_user(sample_user):
    """测试可以直接使用 fixture"""
    result = create_user(sample_user)
    assert result["name"] == "John"
```

---

## 🐛 常见问题

### Q1: ModuleNotFoundError: No module named 'pytest'

**解决方案：**
```powershell
.\venv\Scripts\activate
pip install pytest pytest-asyncio httpx
```

### Q2: ModuleNotFoundError: No module named 'app'

**解决方案：**
确保在项目根目录运行测试，且虚拟环境已激活。

### Q3: 测试运行很慢

**解决方案：**
- 只运行需要的测试：`pytest tests/test_day4_5.py::TestHelpers -v`
- 使用 `-x` 参数在第一个失败时停止

---

## 🎉 下一步

**你现在可以：**
1. ✅ 运行现有的测试
2. ✅ 理解测试的工作原理
3. ✅ 阅读和修改测试代码

**继续学习：**
1. 📖 阅读 `PYTEST_GUIDE.md` 获取详细教程
2. 🧪 运行 `python test_demo.py` 查看交互式演示
3. ✍️ 尝试在 `tests/test_day4_5.py` 中添加自己的测试

---

**Happy Testing! 🧪✨**

有任何问题，请查看 `PYTEST_GUIDE.md` 或运行交互式演示！

