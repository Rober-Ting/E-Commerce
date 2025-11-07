# 🐛 Phase 2 問題記錄與解決方案

> **日期**: 2025-11-07  
> **階段**: Phase 2 - 認證與用戶管理  
> **目的**: 記錄開發過程中遇到的問題，避免未來重複踩坑

---

## 📋 目錄
1. [問題 1: ModuleNotFoundError - email_validator](#問題-1-modulenotfounderror---email_validator)
2. [問題 2: ValueError - bcrypt 密碼長度限制](#問題-2-valueerror---bcrypt-密碼長度限制)
3. [問題 3: AttributeError - bcrypt 版本不兼容](#問題-3-attributeerror---bcrypt-版本不兼容)
4. [問題 4: TypeError - get_database() 誤用 await](#問題-4-typeerror---get_database-誤用-await)
5. [問題 5: 測試環境未激活虛擬環境](#問題-5-測試環境未激活虛擬環境)
6. [問題 6: pytest.ini 配置導致參數錯誤](#問題-6-pytestini-配置導致參數錯誤)

---

## 問題 1: ModuleNotFoundError - email_validator

### ❌ 錯誤訊息
```
ModuleNotFoundError: No module named 'email_validator'
```

### 🔍 錯誤原因
當使用 Pydantic 的 `EmailStr` 類型時，需要額外安裝 `email-validator` 包：

```python
# app/models/user.py
from pydantic import EmailStr  # ❌ 需要 email-validator

class UserBase(BaseModel):
    email: EmailStr  # 這會觸發錯誤
```

### 💡 原理說明
- Pydantic v2 將一些驗證器分離為可選依賴
- `EmailStr` 需要 `email-validator` 來驗證郵箱格式
- 這是 Pydantic 的設計選擇，讓核心包更輕量

### ✅ 解決方案

**步驟 1: 安裝依賴**
```bash
pip install email-validator==2.3.0
```

**步驟 2: 更新 requirements.txt**
```txt
# Testing dependencies
email-validator==2.3.0  # Pydantic EmailStr 需要
```

**步驟 3: 驗證安裝**
```bash
python -c "from pydantic import EmailStr; print('✅ EmailStr 可用')"
```

### 📚 參考資料
- [Pydantic Email Validation](https://docs.pydantic.dev/latest/api/networks/#pydantic.networks.EmailStr)
- [email-validator PyPI](https://pypi.org/project/email-validator/)

---

## 問題 2: ValueError - bcrypt 密碼長度限制

### ❌ 錯誤訊息
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])
```

### 🔍 錯誤原因
bcrypt 算法有一個硬性限制：**最多只能處理 72 字節的密碼**。

當測試數據或用戶輸入超過這個長度時，會導致錯誤：
```python
# ❌ 錯誤示例
password = "a" * 100  # 100 字節
hashed = pwd_context.hash(password)  # ValueError!
```

### 💡 原理說明
- bcrypt 內部使用 Blowfish 算法
- Blowfish 的密鑰長度限制為 72 字節
- 這是算法層面的限制，無法繞過
- UTF-8 編碼的字符可能占用多個字節（中文 3 字節/字符）

### ✅ 解決方案

**方案 1: 在 hash 前自動截斷（推薦）**
```python
# app/utils/security.py
def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密碼
    
    Note:
        bcrypt 限制密碼最多 72 字節，如果超過會自動截斷
    """
    # bcrypt 限制：最多 72 字節
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)
```

**方案 2: 在 verify 時也要截斷**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼是否匹配"""
    # bcrypt 限制：最多 72 字節，需要與 hash_password 保持一致
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)
```

**方案 3: 在前端限制（額外保護）**
```javascript
// 前端驗證
if (password.length > 72) {
    alert('密碼太長，最多 72 個字符');
}
```

### 🎯 最佳實踐
1. **服務端**：自動截斷（防止崩潰）
2. **前端**：限制輸入（提升用戶體驗）
3. **API 文檔**：明確說明限制
4. **測試數據**：不要超過 72 字節

### ⚠️ 注意事項
- UTF-8 字符可能占用多個字節
- 中文字符通常占 3 字節
- 如 "你好世界" = 12 字節（4 字符 × 3）

---

## 問題 3: AttributeError - bcrypt 版本不兼容

### ❌ 錯誤訊息
```
WARNING  passlib.handlers.bcrypt | (trapped) error reading bcrypt version
Traceback (most recent call last):
  File "venv\Lib\site-packages\passlib\handlers\bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
AttributeError: module 'bcrypt' has no attribute '__about__'
```

### 🔍 錯誤原因
**bcrypt 5.0.0** 改變了內部結構，移除了 `__about__` 模組，導致 `passlib` 無法讀取版本信息：

```python
# bcrypt < 5.0.0 ✅
import bcrypt
print(bcrypt.__about__.__version__)  # 可用

# bcrypt >= 5.0.0 ❌
import bcrypt
print(bcrypt.__about__.__version__)  # AttributeError
```

### 💡 原理說明
- `passlib` 依賴 `bcrypt` 進行實際的密碼哈希
- `passlib` 會嘗試讀取 `bcrypt` 版本來選擇最佳後端
- bcrypt 5.0.0 重構了代碼，改變了版本信息的存儲位置
- 這導致 `passlib` 的版本檢測邏輯失效

### ✅ 解決方案

**步驟 1: 降級 bcrypt**
```bash
pip install "bcrypt==4.1.3"
```

**步驟 2: 更新 requirements.txt**
```txt
# 將 bcrypt==5.0.0 改為
bcrypt==4.1.3  # passlib 兼容版本
```

**步驟 3: 驗證安裝**
```bash
python -c "from passlib.hash import bcrypt; print(bcrypt.hash('test'))"
```

### 📊 版本兼容性表

| bcrypt 版本 | passlib 兼容性 | 推薦使用 |
|------------|---------------|---------|
| 5.0.0+     | ❌ 不兼容      | ❌      |
| 4.1.x      | ✅ 完全兼容    | ✅ 推薦  |
| 4.0.x      | ✅ 兼容        | ✅      |
| 3.x.x      | ✅ 兼容        | ⚠️ 舊版本 |

### 🔮 未來展望
- 等待 `passlib` 更新以支持 bcrypt 5.x
- 或考慮遷移到其他密碼哈希庫（如 `argon2-cffi`）
- 追蹤 GitHub issue: [passlib/issues](https://github.com/pyca/bcrypt/issues)

### 📚 參考資料
- [passlib GitHub Issues](https://github.com/pyca/bcrypt/issues)
- [bcrypt Changelog](https://github.com/pyca/bcrypt/blob/main/CHANGELOG.rst)

---

## 問題 4: TypeError - get_database() 誤用 await

### ❌ 錯誤訊息
```
TypeError: object AsyncIOMotorDatabase can't be used in 'await' expression
  File "app\utils\dependencies.py", line 61, in get_current_user
    db = await get_database()
         ^^^^^^^^^^^^^^^^^^^^
```

### 🔍 錯誤原因
錯誤地對**非異步函數**使用了 `await`：

```python
# app/database.py
def get_database() -> AsyncIOMotorDatabase:  # ← 普通函數，不是 async
    """獲取資料庫實例"""
    return db.db

# app/utils/dependencies.py
async def get_current_user(...):
    db = await get_database()  # ❌ 錯誤！不能 await 普通函數
```

### 💡 原理說明

#### Python 異步函數的兩種類型

**1. 普通函數（Sync Function）**
```python
def get_database() -> Database:
    return db.db  # 直接返回對象

# 調用方式
database = get_database()  # 直接調用
```

**2. 異步函數（Async Function / Coroutine）**
```python
async def fetch_data() -> dict:
    return await some_async_operation()  # 返回 coroutine

# 調用方式
data = await fetch_data()  # 需要 await
```

#### 為什麼 `get_database()` 不需要 async？
- `AsyncIOMotorDatabase` 對象本身已經是異步的
- `get_database()` 只是**返回這個對象的引用**
- 真正的異步操作發生在**使用**這個對象時

```python
# ✅ 正確用法
database = get_database()           # 獲取對象（普通調用）
result = await database.users.find_one(...)  # 使用對象（異步操作）
```

### ✅ 解決方案

**錯誤代碼**
```python
# ❌ app/utils/dependencies.py
async def get_current_user(...):
    db = await get_database()  # 錯誤：await 普通函數
    user_data = await db.users.find_one(...)
```

**修正代碼**
```python
# ✅ app/utils/dependencies.py
async def get_current_user(...):
    database = get_database()  # 正確：直接調用
    user_data = await database.users.find_one(...)  # await 異步操作
```

### 🎯 判斷是否需要 await 的方法

| 情況 | 是否需要 await | 示例 |
|-----|--------------|------|
| 函數定義為 `async def` | ✅ 需要 | `await async_function()` |
| 函數定義為 `def` | ❌ 不需要 | `regular_function()` |
| 對象方法是異步的 | ✅ 需要 | `await obj.async_method()` |
| 獲取異步對象的引用 | ❌ 不需要 | `obj = get_async_obj()` |

### 📝 最佳實踐

**1. 明確標註類型**
```python
def get_database() -> AsyncIOMotorDatabase:  # 返回類型清晰
    """獲取資料庫實例（非異步函數）"""
    return db.db
```

**2. 添加文檔說明**
```python
def get_database() -> AsyncIOMotorDatabase:
    """
    獲取資料庫實例
    
    Note:
        這是一個普通函數，不需要 await
        但返回的對象是異步的，使用時需要 await
        
    Returns:
        AsyncIOMotorDatabase: 資料庫實例
        
    Example:
        >>> database = get_database()  # 無需 await
        >>> user = await database.users.find_one(...)  # 需要 await
    """
    return db.db
```

**3. 使用 IDE 檢查**
- VS Code 會對錯誤的 await 使用發出警告
- PyCharm 會在代碼審查時提示

---

## 問題 5: 測試環境未激活虛擬環境

### ❌ 錯誤訊息
```
platform win32 -- Python 3.12.9, pytest-8.3.4, pluggy-1.5.0 
-- C:\Users\ROBERT.TING\AppData\Local\miniconda3\python.exe
                                 ^^^^^^^^^^^^^^^^ 使用了系統 Python

ModuleNotFoundError: No module named 'motor'
```

### 🔍 錯誤原因
在終端運行測試時，使用的是**系統 Python**（conda base），而不是**項目虛擬環境**：

```powershell
# ❌ 在 (base) 環境運行
(base) PS D:\...\ecommerce-api> python -m pytest tests/
# 使用: C:\...\miniconda3\python.exe (無項目依賴)

# ✅ 在虛擬環境運行
(venv) PS D:\...\ecommerce-api> python -m pytest tests/
# 使用: D:\...\ecommerce-api\venv\Scripts\python.exe (有所有依賴)
```

### 💡 原理說明

#### 虛擬環境的工作原理
1. **隔離依賴**：每個項目有獨立的包安裝目錄
2. **PATH 修改**：激活時將 `venv/Scripts/` 加入 PATH 最前面
3. **python 命令**：優先使用虛擬環境中的 Python

```
未激活虛擬環境:
└── python → C:\miniconda3\python.exe (系統 Python)

激活虛擬環境:
└── python → D:\...\venv\Scripts\python.exe (項目 Python)
```

### ✅ 解決方案

**Windows PowerShell**
```powershell
# 激活虛擬環境
.\venv\Scripts\activate

# 確認環境
(venv) PS D:\...\ecommerce-api> python --version
(venv) PS D:\...\ecommerce-api> which python
D:\Robert\ML\MongoDB\ecommerce-api\venv\Scripts\python.exe  # ✅ 正確

# 運行測試
(venv) PS D:\...\ecommerce-api> python -m pytest tests/
```

**Windows CMD**
```cmd
venv\Scripts\activate.bat
```

**Git Bash / Linux / macOS**
```bash
source venv/bin/activate
```

### 🎯 如何避免此問題

**方法 1: 使用 VS Code 集成終端（推薦）**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true  // 自動激活
}
```

**方法 2: 使用啟動腳本**
```powershell
# run_tests.ps1
.\venv\Scripts\activate
python -m pytest tests/ -v
```

**方法 3: 使用絕對路徑**
```powershell
# 不推薦，但可用
.\venv\Scripts\python.exe -m pytest tests/
```

### 📝 檢查清單

運行測試前檢查：
- [ ] 終端提示符顯示 `(venv)`
- [ ] `which python` 指向項目 venv
- [ ] `pip list` 顯示項目依賴（如 fastapi, motor）

---

## 問題 6: pytest.ini 配置導致參數錯誤

### ❌ 錯誤訊息
```
ERROR: usage: __main__.py [options] [file_or_dir] [file_or_dir] [...]
__main__.py: error: unrecognized arguments: --cov=app --cov-branch --cov-report=html
```

### 🔍 錯誤原因
`pytest.ini` 中配置的 `--cov` 參數會**自動添加**到每次測試運行中：

```ini
# pytest.ini
[pytest]
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=app          # ← 這些會自動加入
    --cov-branch
    --cov-report=html
```

當使用 `python -m pytest` 時，如果沒有安裝 `pytest-cov`，會報錯。

### 💡 原理說明

#### pytest 配置加載順序
1. **命令行參數**：最高優先級
2. **pytest.ini**：項目配置
3. **內置默認值**：最低優先級

```bash
# 實際執行的命令
python -m pytest tests/test_phase2_auth.py -v
# ↓ pytest 自動展開為
python -m pytest tests/test_phase2_auth.py -v --strict-markers --tb=short --cov=app --cov-branch --cov-report=html
```

#### 為什麼會報錯？
- `pytest-cov` 未安裝 → `--cov` 參數無法識別
- 或者在特定情況下不想運行覆蓋率測試

### ✅ 解決方案

**方案 1: 安裝 pytest-cov（推薦）**
```bash
pip install pytest-cov==7.0.0
```

**方案 2: 臨時禁用覆蓋率**
```ini
# pytest.ini
[pytest]
addopts = 
    -v
    --strict-markers
    --tb=short
    # 覆蓋率選項（暫時禁用以快速測試）
    # --cov=app
    # --cov-branch
    # --cov-report=html
```

**方案 3: 使用命令行覆蓋**
```bash
# 覆蓋 pytest.ini 配置，不使用覆蓋率
python -m pytest tests/ -v --override-ini="addopts=-v --strict-markers --tb=short"
```

**方案 4: 使用 -p no:cov**
```bash
# 禁用 pytest-cov 插件
python -m pytest tests/ -p no:cov
```

### 🎯 最佳實踐

**開發階段配置**
```ini
# pytest.ini（開發時快速測試）
[pytest]
addopts = 
    -v
    --strict-markers
    --tb=short
    # --cov=app  # 開發時註釋掉
```

**CI/CD 配置**
```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=app --cov-report=xml --cov-report=html
```

**個人配置文件**
```ini
# pytest.ini
[pytest]
addopts = 
    -v
    --strict-markers
    --tb=short

# 如需覆蓋率，手動添加
# pytest tests/ --cov=app
```

### 📝 配置文件優先級

```
命令行 > pytest.ini > pyproject.toml > setup.cfg > 默認值
```

---

## 📚 總結與最佳實踐

### ✅ 開發前檢查清單
- [ ] 虛擬環境已激活 `(venv)`
- [ ] 所有依賴已安裝 `pip install -r requirements.txt`
- [ ] MongoDB 服務已啟動
- [ ] VS Code 使用正確的 Python 解釋器

### 🎯 依賴管理最佳實踐

1. **固定版本號**
```txt
# ✅ 推薦
fastapi==0.115.6
bcrypt==4.1.3

# ❌ 避免
fastapi>=0.115.0  # 可能引入不兼容更新
bcrypt  # 無版本控制
```

2. **測試依賴分離**
```txt
# 核心依賴
fastapi==0.115.6
motor==3.7.1

# 測試依賴
pytest==8.3.4
pytest-asyncio==0.25.2
pytest-cov==7.0.0
```

3. **定期更新檢查**
```bash
pip list --outdated
```

### 🔍 測試前檢查

```bash
# 1. 確認環境
which python  # 應指向 venv
pip list | grep fastapi  # 確認依賴

# 2. 確認服務
# MongoDB 應在運行

# 3. 運行測試
python -m pytest tests/ -v

# 4. 帶覆蓋率
python -m pytest tests/ --cov=app --cov-report=html
```

### 📖 相關文檔
- [完整測試指南](../03-testing/PYTEST_GUIDE.md)
- [覆蓋率指南](../03-testing/COVERAGE_GUIDE.md)
- [調試指南](../04-debugging/VSCODE_DEBUG_GUIDE.md)
- [通用問題排除](./TROUBLESHOOTING.md)

---

## 🤝 貢獻

如果你遇到新的問題並找到解決方案，請：
1. 記錄問題和解決方案
2. 更新此文檔
3. 提交 Pull Request

**文檔格式**：
```markdown
## 問題 X: 簡短描述

### ❌ 錯誤訊息
```
錯誤輸出
```

### 🔍 錯誤原因
詳細說明

### ✅ 解決方案
步驟說明
```

---

**最後更新**: 2025-11-07  
**版本**: Phase 2 Complete  
**作者**: AI Assistant + Robert

