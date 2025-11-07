# 🐛 VS Code 调试指南

## ✅ 问题已解决！

我已经为你创建了完整的 VS Code 配置文件，现在可以直接按 F5 运行测试了！

---

## 📁 创建的配置文件

### 1. `.vscode/launch.json` - 调试配置
定义了如何运行和调试你的代码

### 2. `.vscode/settings.json` - VS Code 设置
配置了 Python 解释器、测试框架等

---

## 🎯 现在你可以做什么

### 方式 1：按 F5 运行（推荐 ⭐⭐⭐）

1. **打开测试文件** `tests/test_day4_5.py`
2. **按 F5** 或点击 "运行和调试" 按钮
3. **选择配置**：`Python: 运行当前测试文件 (Pytest)`
4. **查看结果** 在终端中

```
选择这个配置：
┌─────────────────────────────────────────┐
│ Python: 运行当前测试文件 (Pytest)      │  ← 选这个！
│ Python: 运行所有测试                    │
│ Python: 运行当前文件                    │
│ Python: 运行 FastAPI 服务器             │
└─────────────────────────────────────────┘
```

---

### 方式 2：使用 VS Code 测试面板（最强大 ⭐⭐⭐⭐）

#### 步骤 1：打开测试面板

点击 VS Code 左侧的烧杯图标 🧪，或按 `Ctrl+Shift+P` 输入 "Test: Focus on Test Explorer View"

#### 步骤 2：刷新测试

点击测试面板顶部的刷新按钮 🔄

#### 步骤 3：你会看到所有测试的树状结构

```
🧪 测试
 └─ test_day4_5.py
     ├─ TestCommonModels
     │   ├─ ✓ test_success_response
     │   ├─ ✓ test_error_response
     │   ├─ ✓ test_pagination_params
     │   ├─ ✓ test_pagination_meta_create
     │   └─ ✓ test_paginated_response
     ├─ TestHelpers
     │   ├─ ✓ test_is_valid_objectid
     │   ├─ ✓ test_str_to_objectid
     │   ├─ ✓ test_generate_order_number
     │   ├─ ✓ test_format_currency
     │   ├─ ✓ test_mask_email
     │   └─ ✓ test_safe_divide
     ├─ TestErrorHandler
     │   ├─ ✓ test_api_exception
     │   ├─ ✓ test_not_found_exception
     │   └─ ✓ test_validation_exception
     └─ ✓ test_imports
```

#### 步骤 4：运行测试

**运行单个测试：** 点击测试名称旁的播放按钮 ▶️

**运行整个类：** 点击类名旁的播放按钮

**运行所有测试：** 点击文件名旁的播放按钮

**调试测试：** 右键测试 → "Debug Test" 🐛

---

### 方式 3：在代码中直接运行

在测试函数上方会出现 "Run Test" | "Debug Test" 按钮：

```python
def test_success_response(self):    # ← 鼠标悬停会看到 Run | Debug
    """測試成功響應"""
    response = success_response(
        data={"user_id": "123"},
        message="User created"
    )
    assert response["success"] is True
```

点击 **"Run Test"** 就能立即运行这个测试！

---

## 🚀 4 种调试配置详解

我为你准备了 4 个预设配置，按 F5 时可以选择：

### 1️⃣ Python: 运行当前测试文件 (Pytest)

**用途：** 运行你当前打开的测试文件

**使用场景：**
- 你正在编辑 `test_day4_5.py`
- 想要运行这个文件中的所有测试

**参数：**
- `-v`: 详细模式
- `-s`: 显示 print 输出

---

### 2️⃣ Python: 运行所有测试

**用途：** 运行 `tests/` 目录下的所有测试

**使用场景：**
- 提交代码前，确保所有测试都通过
- 全面检查项目状态

---

### 3️⃣ Python: 运行当前文件

**用途：** 直接运行当前的 Python 文件（不通过 pytest）

**使用场景：**
- 运行普通的 Python 脚本
- 例如：`python test_demo.py`

---

### 4️⃣ Python: 运行 FastAPI 服务器

**用途：** 启动你的 FastAPI 应用

**使用场景：**
- 启动 API 服务器
- 在浏览器中访问 http://localhost:8000
- 自动重载（--reload）

---

## 🐛 调试功能（超强大！）

### 设置断点

1. **在代码行号左侧点击**，会出现红色圆点 🔴
2. **按 F5 运行**，程序会在断点处暂停
3. **查看变量值**，鼠标悬停在变量上

### 调试控制

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `F5` | 继续 | 运行到下一个断点 |
| `F10` | 单步跳过 | 执行当前行，不进入函数 |
| `F11` | 单步进入 | 进入函数内部 |
| `Shift+F11` | 单步跳出 | 跳出当前函数 |
| `Shift+F5` | 停止 | 停止调试 |

### 调试面板

调试时，左侧会显示：
- **变量（Variables）**: 查看所有变量的值
- **监视（Watch）**: 监视特定表达式
- **调用堆栈（Call Stack）**: 查看函数调用链
- **断点（Breakpoints）**: 管理所有断点

---

## 📝 实战演示

### 演示 1：调试单个测试

1. 打开 `tests/test_day4_5.py`
2. 找到 `test_generate_order_number` 函数
3. 在第 100 行设置断点（点击行号左侧）
   ```python
   assert order_num.startswith("ORD")  # ← 在这里设置断点
   ```
4. 右键测试函数 → "Debug Test"
5. 程序会在断点处暂停
6. 鼠标悬停在 `order_num` 上，查看其值
7. 按 F10 单步执行，观察每一行的效果

### 演示 2：调试失败的测试

1. 修改测试让它失败：
   ```python
   def test_mask_email(self):
       masked = mask_email("user@example.com")
       assert masked == "wrong_value"  # 故意写错
   ```

2. 在断言行设置断点
3. 运行测试
4. 在断点处查看 `masked` 的实际值
5. 对比期望值和实际值
6. 找出问题所在

---

## 💡 常用技巧

### 技巧 1：快速运行/调试当前测试

- **光标放在测试函数内**
- **按 F5** → 会自动运行该测试
- **或右键** → "Debug Test"

### 技巧 2：使用条件断点

1. 右键断点（红色圆点）
2. 选择 "Edit Breakpoint"
3. 输入条件，例如：`order_num == "ORD20251031"`
4. 只有满足条件时才会暂停

### 技巧 3：查看表达式的值

在调试时：
1. 选中任意表达式（例如 `response["success"]`）
2. 右键 → "Evaluate in Debug Console"
3. 或者添加到 Watch 面板

### 技巧 4：使用 Debug Console

调试时可以在 Debug Console 中执行代码：
```python
# 查看变量
>>> response
{'success': True, 'data': {'user_id': '123'}, 'message': 'User created'}

# 调用函数
>>> mask_email("test@example.com")
't***@example.com'

# 执行任意 Python 代码
>>> len(order_num)
23
```

---

## ⚙️ 配置文件详解

### launch.json 关键配置

```json
{
    "module": "pytest",              // 使用 pytest 模块运行
    "args": ["${file}", "-v", "-s"], // 参数：当前文件、详细模式、显示输出
    "cwd": "${workspaceFolder}",     // 工作目录：项目根目录
    "env": {
        "PYTHONPATH": "${workspaceFolder}"  // ✅ 这解决了 "No module named 'app'" 问题
    },
    "python": "${workspaceFolder}/venv/Scripts/python.exe"  // 使用虚拟环境的 Python
}
```

### settings.json 关键配置

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    // ✅ 使用虚拟环境的 Python
    
    "python.testing.pytestEnabled": true,
    // ✅ 启用 pytest 测试框架
    
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}"
    }
    // ✅ 终端中也设置 PYTHONPATH
}
```

---

## 🔧 故障排除

### 问题 1：按 F5 后没有反应

**解决方案：**
1. 确保虚拟环境已创建：`python -m venv venv`
2. 重启 VS Code
3. 按 `Ctrl+Shift+P` → "Python: Select Interpreter" → 选择虚拟环境

---

### 问题 2：仍然显示 "No module named 'app'"

**解决方案：**
1. 检查你是否在**项目根目录**打开 VS Code
2. 确认 `.vscode` 文件夹在项目根目录
3. 重新加载窗口：`Ctrl+Shift+P` → "Developer: Reload Window"

---

### 问题 3：测试面板没有显示测试

**解决方案：**
1. 打开测试面板（左侧烧杯图标 🧪）
2. 点击刷新按钮 🔄
3. 如果还是没有，执行：`Ctrl+Shift+P` → "Python: Configure Tests" → 选择 "pytest"

---

### 问题 4：断点不起作用

**解决方案：**
1. 确保使用了 "Debug Test" 而不是 "Run Test"
2. 检查 `justMyCode` 是否设置为 `false`
3. 尝试在代码中添加 `breakpoint()` 语句

---

## 🎯 推荐工作流

### 日常开发

1. **编写代码** → 在 `app/` 目录
2. **编写测试** → 在 `tests/` 目录
3. **运行测试** → 点击测试旁的播放按钮 ▶️
4. **调试问题** → 设置断点 🔴，按 F5

### 提交代码前

1. **运行所有测试** → 选择 "Python: 运行所有测试"
2. **确保全部通过** → 看到 ✅
3. **提交代码** → `git commit`

---

## 📚 VS Code 快捷键速查

| 快捷键 | 功能 |
|--------|------|
| `F5` | 开始调试 / 继续 |
| `Ctrl+F5` | 运行（不调试） |
| `F9` | 切换断点 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |
| `Ctrl+Shift+F5` | 重启调试 |
| `Shift+F5` | 停止调试 |
| `Ctrl+Shift+P` | 命令面板 |
| `` Ctrl+` `` | 打开终端 |

---

## 🎓 学习资源

### VS Code 官方文档
- Python 调试：https://code.visualstudio.com/docs/python/debugging
- 测试：https://code.visualstudio.com/docs/python/testing

### 推荐插件
- **Python** (Microsoft) - 必装
- **Pylance** - Python 语言服务器
- **Better Comments** - 更好的注释高亮

---

## 🎉 总结

**你现在可以：**
- ✅ 按 F5 直接运行测试文件
- ✅ 在测试面板中管理所有测试
- ✅ 使用断点调试代码
- ✅ 在 Debug Console 中实时测试代码

**下一步：**
1. 打开 `tests/test_day4_5.py`
2. 按 F5 试试看！
3. 尝试设置断点并调试

---

Happy Debugging! 🐛✨

