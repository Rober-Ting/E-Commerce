# 🔧 常見問題排除

## ❌ 問題：ModuleNotFoundError: No module named 'app'

### 錯誤訊息
```
Exception has occurred: ModuleNotFoundError
No module named 'app'
  File "D:\Robert\ML\MongoDB\ecommerce-api\app\main.py", line 9, in <module>
    from app.database import connect_to_mongo, close_mongo_connection
```

### 🔍 原因分析

這個錯誤發生是因為：
1. 你可能**直接運行了** `app/main.py` 檔案（按 F5 時選錯配置）
2. Python 無法找到 `app` 模組
3. 工作目錄不正確

### ✅ 解決方案

#### 方案 1：使用正確的 VSCode Debug 配置（推薦）

**步驟 1：確認 VSCode 打開的是正確的資料夾**

確保你在 VSCode 中打開的是 `ecommerce-api` 資料夾，而不是 `MongoDB` 或其他資料夾。

檢查方法：
- 看 VSCode 左上角的資料夾名稱，應該是 `ECOMMERCE-API`
- 左側檔案樹的根目錄應該是 `ecommerce-api`

**如果不對，重新打開**：
```
檔案 → 開啟資料夾 → 選擇 D:\Robert\ML\MongoDB\ecommerce-api
```

**步驟 2：選擇正確的 Debug 配置**

1. 打開 `app/main.py`
2. 按 `F5` 或點擊左側的「執行和偵錯」圖標
3. 在頂部下拉選單中選擇 **「Debug FastAPI」**（不是「Python: 當前檔案」）
4. 點擊綠色播放按鈕

![Debug 配置選擇](https://i.imgur.com/example.png)

**步驟 3：設為預設配置**

在 `.vscode/launch.json` 中，確保 "Debug FastAPI" 是第一個配置。

---

#### 方案 2：使用終端機運行（最簡單）

**不要直接運行 Python 檔案**，而是使用 uvicorn：

```powershell
# 1. 切換到 ecommerce-api 目錄
cd D:\Robert\ML\MongoDB\ecommerce-api

# 2. 啟動虛擬環境（如果還沒啟動）
.\venv\Scripts\Activate.ps1

# 3. 使用 uvicorn 啟動（正確方式）
uvicorn app.main:app --reload --log-level debug
```

**千萬不要這樣做**：
```powershell
# ❌ 錯誤：直接運行 Python 檔案
python app/main.py  # 這會導致 ModuleNotFoundError

# ❌ 錯誤：在錯誤的目錄運行
cd app
python main.py  # 這也會出錯
```

---

#### 方案 3：檢查 VSCode 設定

**步驟 1：確認 Python 直譯器**

1. 按 `Ctrl+Shift+P`
2. 輸入 "Python: Select Interpreter"
3. 選擇 `.\venv\Scripts\python.exe`（虛擬環境中的 Python）

**步驟 2：確認工作目錄**

在 VSCode 終端機中執行：
```powershell
pwd
```

應該顯示：
```
Path
----
D:\Robert\ML\MongoDB\ecommerce-api
```

如果不是，請：
```powershell
cd D:\Robert\ML\MongoDB\ecommerce-api
```

---

## 🎯 快速修復（複製貼上）

如果上述方法太複雜，**最快的方法**：

### 1. 關閉所有 VSCode 視窗

### 2. 重新打開專案

```powershell
# 在 PowerShell 中執行
cd D:\Robert\ML\MongoDB\ecommerce-api
code .
```

### 3. 在 VSCode 終端機中運行

按 <kbd>Ctrl</kbd> + <kbd>`</kbd> 打開終端機，然後：

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

**完成！** 🎉

---

## 🔍 理解問題

### 為什麼會有這個問題？

Python 的模組導入系統需要知道從哪裡尋找模組。當你：

```python
from app.database import connect_to_mongo
```

Python 會在 `sys.path` 中尋找名為 `app` 的資料夾。

**如果你直接運行** `python app/main.py`：
- 當前目錄變成 `app/`
- Python 在 `app/` 裡找不到 `app` 資料夾
- 導致 `ModuleNotFoundError`

**如果你使用** `uvicorn app.main:app`：
- uvicorn 知道從專案根目錄尋找
- Python 可以找到 `app/` 資料夾
- 一切正常運作 ✅

---

## 📚 相關概念學習

### Python 模組導入原理

```
專案結構：
ecommerce-api/          ← 這是工作目錄
├── app/                ← Python 要找的 'app' 模組
│   ├── __init__.py
│   ├── main.py         ← 這個檔案在導入
│   └── database.py     ← 要被導入的檔案
└── venv/

執行指令：
uvicorn app.main:app
         ↑    ↑    ↑
         │    │    └─ FastAPI 實例的名稱
         │    └────── main.py 檔案
         └─────────── app 模組（資料夾）
```

### 為什麼 uvicorn 可以正確運作？

```python
# uvicorn 的運作方式：
# 1. 在當前目錄尋找 'app' 資料夾 ✓
# 2. 在 'app' 資料夾中尋找 'main.py' ✓
# 3. 在 'main.py' 中尋找 'app' 變數 ✓
```

---

## ✅ 驗證修復

運行成功後，你應該看到：

```
================================================================================
開始載入 FastAPI 應用模組
當前設定 - DEBUG: True
當前設定 - PROJECT_NAME: E-Commerce API
當前設定 - MONGODB_URL: mongodb://localhost:27017
當前設定 - MONGODB_DB_NAME: ecommerce_db
================================================================================
正在建立 FastAPI 應用實例...
✅ FastAPI 應用實例建立完成: E-Commerce API v1.0.0
...
✅ 應用程式啟動完成
```

---

## 🐛 其他常見錯誤

### 錯誤 1：找不到 uvicorn

```
uvicorn : 無法辨識 'uvicorn' 詞彙
```

**解決**：
```powershell
# 確認虛擬環境已啟動
.\venv\Scripts\Activate.ps1

# 重新安裝（如果需要）
pip install uvicorn[standard]
```

---

### 錯誤 2：埠號被佔用

```
ERROR: [Errno 10048] Only one usage of each socket address
```

**解決**：
```powershell
# 使用不同埠號
uvicorn app.main:app --reload --port 8001
```

---

### 錯誤 3：找不到 .env

```
WARNING: .env file not found
```

**解決**：
```powershell
# 執行設置腳本
.\scripts\setup_env.ps1

# 或手動建立
Copy-Item .env.example .env
notepad .env
```

---

## 📝 最佳實踐

### ✅ 正確的運行方式

```powershell
# 方式 1：終端機（推薦給初學者）
cd ecommerce-api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug

# 方式 2：VSCode Debug（推薦給深入學習）
# 1. 在 VSCode 中打開 ecommerce-api 資料夾
# 2. 選擇 "Debug FastAPI" 配置
# 3. 按 F5
```

### ❌ 錯誤的運行方式

```powershell
# ❌ 不要直接運行 Python 檔案
python app/main.py
python app\main.py
python -m app.main

# ❌ 不要在錯誤的目錄運行
cd app
python main.py
```

---

## 🎓 學習要點

透過這個錯誤，你學到了：

1. **Python 模組系統**
   - 模組如何被尋找
   - 工作目錄的重要性
   - `sys.path` 的作用

2. **專案結構**
   - 為什麼要有 `__init__.py`
   - 相對導入 vs 絕對導入
   - 包（package）的概念

3. **FastAPI 運行方式**
   - 為什麼要用 uvicorn
   - ASGI 伺服器的作用
   - 模組字串的格式（`app.main:app`）

4. **開發工具使用**
   - VSCode Debug 配置
   - 工作目錄設定
   - Python 直譯器選擇

---

## 📞 還是不行？

如果上述所有方法都試過了還是不行：

### 檢查清單

- [ ] VSCode 打開的是 `ecommerce-api` 資料夾（不是 `MongoDB`）
- [ ] 虛擬環境已啟動（看到 `(venv)` 前綴）
- [ ] 在終端機中 `pwd` 顯示正確的目錄
- [ ] Python 直譯器指向 `.\venv\Scripts\python.exe`
- [ ] 使用 `uvicorn app.main:app` 而不是 `python app/main.py`

### 終極解決方案

```powershell
# 1. 完全重新開始
cd D:\Robert\ML\MongoDB\ecommerce-api

# 2. 停用並重新啟動虛擬環境
deactivate  # 如果已啟動
.\venv\Scripts\Activate.ps1

# 3. 確認安裝
pip list | Select-String "uvicorn"

# 4. 運行
uvicorn app.main:app --reload
```

---

**記住**：永遠使用 `uvicorn app.main:app` 來啟動 FastAPI 應用！

這是標準且正確的方式！✅

