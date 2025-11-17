# 🐛 登入功能调试完整指南

## 📌 前置条件

1. ✅ 后端服务器正在运行（`uvicorn app.main:app --reload`）
2. ✅ MongoDB 已启动
3. ✅ 数据库中有测试用户
4. ✅ VS Code 已安装 Python 扩展

---

## 🎯 调试流程图

```
前端页面
    ↓
【断点 1】app/api/v1/auth.py:86 - login() 函数入口
    ↓ 接收 credentials (email, password)
    ↓
【断点 2】app/services/user_service.py:236 - authenticate_user()
    ↓ 调用 get_user_by_email(email)
    ↓ 检查用户是否存在
    ↓
【断点 3】app/services/user_service.py:240 - 密码验证前
    ↓ 调用 verify_password()
    ↓
【断点 4】app/utils/security.py:65 - verify_password()
    ↓ bcrypt 验证密码
    ↓ 返回 True/False
    ↓
【断点 5】app/api/v1/auth.py:96 - 检查认证结果
    ↓ 如果成功，继续
    ↓
【断点 6】app/api/v1/auth.py:112 - 创建 JWT Token
    ↓
返回给前端
```

---

## 🔴 关键断点位置

### **断点 1：路由入口（必设）**

**文件：`app/api/v1/auth.py`**  
**行号：86**

```python
logger.info(f"登入請求: email={credentials.email}")
```

**检查内容：**
- `credentials.email` - 前端传来的邮箱
- `credentials.password` - 前端传来的密码

---

### **断点 2：查找用户（必设）**

**文件：`app/services/user_service.py`**  
**行号：236**

```python
user = await self.get_user_by_email(email)
```

**检查内容：**
- `email` - 查询的邮箱
- `user` - 查询结果（UserInDB 对象或 None）
- `user.hashed_password` - 数据库中存储的哈希密码

---

### **断点 3：密码验证调用（必设）**

**文件：`app/services/user_service.py`**  
**行号：240**

```python
if not verify_password(password, user.hashed_password):
```

**检查内容：**
- `password` - 用户输入的明文密码
- `user.hashed_password` - 数据库中的哈希密码
- 即将进入 `verify_password()` 函数

---

### **断点 4：密码验证执行（必设）**

**文件：`app/utils/security.py`**  
**行号：65**

```python
return pwd_context.verify(plain_password, hashed_password)
```

**检查内容：**
- `plain_password` - 用户输入的密码
- `hashed_password` - 数据库中的哈希密码
- **函数返回值** - True（密码正确）或 False（密码错误）

---

### **断点 5：检查认证结果（可选）**

**文件：`app/api/v1/auth.py`**  
**行号：96**

```python
if user is None:
```

**检查内容：**
- `user` - 认证结果
- 如果是 `None`，表示认证失败

---

### **断点 6：创建 Token（可选）**

**文件：`app/api/v1/auth.py`**  
**行号：112**

```python
access_token = create_access_token(
    data={"sub": user.email, "role": user.role.value}
)
```

**检查内容：**
- `user.email` - 用户邮箱
- `user.role` - 用户角色
- `access_token` - 生成的 JWT Token

---

## 🚀 操作步骤

### **方法一：使用 VS Code 调试（推荐）**

#### **1. 设置断点**

在以下文件中点击行号左侧设置红色断点：

```
✅ app/api/v1/auth.py          → 第 86 行
✅ app/services/user_service.py → 第 236 行
✅ app/services/user_service.py → 第 240 行
✅ app/utils/security.py        → 第 65 行
```

#### **2. 启动调试服务器**

**按 `F5` 或点击 "Run and Debug"**

选择配置：`FastAPI: Run Server (Debug Mode)`

等待看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ 應用啟動完成！
```

#### **3. 打开前端页面**

在浏览器访问：
```
http://localhost:8080/frontend_demo.html
```

#### **4. 触发登入**

1. 输入邮箱和密码
2. 点击 **"登入"** 按钮
3. VS Code 会自动暂停在第一个断点

#### **5. 逐步调试**

使用调试控制按钮：

| 按钮 | 快捷键 | 功能 |
|------|--------|------|
| ▶️ Continue | `F5` | 继续到下一个断点 |
| ⤵️ Step Over | `F10` | 执行当前行，不进入函数 |
| ⤴️ Step Into | `F11` | 进入函数内部 |
| ⤴️ Step Out | `Shift+F11` | 跳出当前函数 |
| 🔄 Restart | `Ctrl+Shift+F5` | 重新启动调试 |
| ⏹️ Stop | `Shift+F5` | 停止调试 |

#### **6. 查看变量**

在 VS Code 左侧面板查看：

- **Variables（变量）**：所有局部变量和全局变量
- **Watch（监视）**：添加自定义表达式监视
- **Call Stack（调用栈）**：函数调用链

**推荐监视的表达式：**
```python
credentials.email
credentials.password
user.hashed_password if user else None
user.is_active if user else None
```

---

### **方法二：使用 Python 调试器**

如果 VS Code 调试有问题，可以使用内置调试器：

#### **1. 在代码中添加断点**

在关键位置添加：

```python
import pdb; pdb.set_trace()
```

例如在 `app/api/v1/auth.py` 的第 86 行：

```python
logger.info(f"登入請求: email={credentials.email}")
import pdb; pdb.set_trace()  # 添加这行
```

#### **2. 启动服务器**

```powershell
python -m uvicorn app.main:app --reload
```

#### **3. 触发登入**

当代码执行到断点时，终端会进入 pdb 调试模式：

```
> d:\robert\ml\mongodb\ecommerce-api\app\api\v1\auth.py(87)login()
-> user_service = UserService(db)
(Pdb)
```

#### **4. 使用 pdb 命令**

| 命令 | 功能 |
|------|------|
| `n` (next) | 执行下一行 |
| `s` (step) | 进入函数 |
| `c` (continue) | 继续执行 |
| `p 变量名` | 打印变量值 |
| `pp 变量名` | 美化打印 |
| `l` (list) | 显示当前代码 |
| `w` (where) | 显示调用栈 |
| `q` (quit) | 退出调试 |

**示例：**

```python
(Pdb) p credentials.email
'rob19940528@gmail.com'

(Pdb) p credentials.password
'Robert0528@'

(Pdb) n
> d:\robert\ml\mongodb\ecommerce-api\app\services\user_service.py(236)authenticate_user()
-> user = await self.get_user_by_email(email)

(Pdb) n
> d:\robert\ml\mongodb\ecommerce-api\app\services\user_service.py(237)authenticate_user()
-> if user is None:

(Pdb) p user
<UserInDB object at 0x...>

(Pdb) pp user.email
'rob19940528@gmail.com'
```

---

## 🔍 调试检查清单

在每个断点检查以下内容：

### **✅ 断点 1（auth.py:86）**
- [ ] `credentials.email` 是否正确？
- [ ] `credentials.password` 是否正确？
- [ ] `db` 对象是否存在？

### **✅ 断点 2（user_service.py:236）**
- [ ] `email` 参数是否正确？
- [ ] `user` 查询结果是否为 None？
- [ ] 如果不是 None，`user.email` 是否匹配？
- [ ] `user.hashed_password` 是否存在？

### **✅ 断点 3（user_service.py:240）**
- [ ] `password` 是否是明文密码？
- [ ] `user.hashed_password` 是否以 `$2b$` 开头（bcrypt 格式）？
- [ ] 即将调用 `verify_password()`

### **✅ 断点 4（security.py:65）**
- [ ] `plain_password` 是否正确？
- [ ] `hashed_password` 格式是否正确？
- [ ] **查看返回值**：True（成功）或 False（失败）

### **✅ 断点 5（auth.py:96）**
- [ ] `user` 是否为 None？
- [ ] 如果是 None，认证失败
- [ ] 如果不是 None，继续检查 `user.is_active`

### **✅ 断点 6（auth.py:112）**
- [ ] `user.email` 是否正确？
- [ ] `user.role` 是什么角色？
- [ ] `access_token` 是否成功生成？

---

## 🐛 常见问题排查

### **问题 1：用户不存在**

**现象：**
- 在 `user_service.py:236` 处，`user` 为 `None`

**解决方案：**
```powershell
# 检查数据库
python check_database.py
```

确认用户是否存在，如果不存在，先注册。

---

### **问题 2：密码验证失败**

**现象：**
- 在 `security.py:65` 处，返回 `False`

**检查：**
1. 数据库中的 `hashed_password` 格式是否正确？
2. 前端传来的密码是否正确？
3. 密码是否超过 72 字节？

**测试：**
```python
# 在调试控制台执行
from app.utils.security import verify_password, hash_password

# 测试密码哈希
test_password = "Robert0528@"
test_hash = hash_password(test_password)
print(f"Hash: {test_hash}")

# 测试验证
result = verify_password(test_password, test_hash)
print(f"Verify: {result}")  # 应该是 True
```

---

### **问题 3：Token 创建失败**

**现象：**
- 在 `auth.py:112` 处出错

**检查：**
- `settings.SECRET_KEY` 是否配置？
- `user.email` 和 `user.role` 是否存在？

---

## 📊 调试信息示例

### **正常登入流程的变量值**

```python
# 断点 1: auth.py:86
credentials = UserLogin(
    email='rob19940528@gmail.com',
    password='Robert0528@'
)

# 断点 2: user_service.py:236
email = 'rob19940528@gmail.com'
user = UserInDB(
    id='690daf83e08b81db9bf42b62',
    email='rob19940528@gmail.com',
    hashed_password='$2b$12$...',
    full_name='Robert',
    is_active=True,
    role=UserRole.customer
)

# 断点 3: user_service.py:240
password = 'Robert0528@'
user.hashed_password = '$2b$12$abcdef...'

# 断点 4: security.py:65
plain_password = 'Robert0528@'
hashed_password = '$2b$12$abcdef...'
# 返回: True

# 断点 5: auth.py:96
user = UserInDB(...)  # 不是 None

# 断点 6: auth.py:112
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

---

## 🎓 学习建议

### **第一次调试：**
1. 只设置 **断点 1** 和 **断点 4**
2. 观察数据从路由到安全层的流动
3. 使用 `F10` (Step Over) 逐行执行

### **第二次调试：**
1. 设置所有断点
2. 使用 `F11` (Step Into) 进入每个函数
3. 观察完整的调用链

### **第三次调试：**
1. 尝试错误的密码
2. 观察验证失败的流程
3. 查看错误处理机制

---

## 🔗 相关文档

- [VS Code Python 调试](https://code.visualstudio.com/docs/python/debugging)
- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [bcrypt 密码哈希](https://en.wikipedia.org/wiki/Bcrypt)
- [JWT Token](https://jwt.io/)

---

## 💡 提示

1. **使用条件断点**：右键断点 → Edit Breakpoint → 添加条件
   ```python
   credentials.email == "rob19940528@gmail.com"
   ```

2. **使用日志断点**：右键断点 → Logpoint → 输出日志而不暂停
   ```python
   Received login request: {credentials.email}
   ```

3. **查看请求日志**：终端会显示每次 API 调用
   ```
   INFO | app.api.v1.auth | 登入請求: email=rob19940528@gmail.com
   ```

4. **使用 FastAPI Docs**：访问 `http://127.0.0.1:8000/docs` 测试 API

---

**祝调试顺利！** 🎉

有问题随时问我！

