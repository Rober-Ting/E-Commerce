# ❌➡️✅ 修復 "No module named 'app'" 錯誤

## 🚨 你看到這個錯誤了嗎？

```
ModuleNotFoundError: No module named 'app'
```

**別擔心！這是新手最常見的錯誤，很容易解決！**

---

## ⚡ 超快速解決（30 秒）

### 步驟 1：在 PowerShell 中執行

```powershell
cd D:\Robert\ML\MongoDB\ecommerce-api
```

### 步驟 2：啟動虛擬環境

```powershell
.\venv\Scripts\Activate.ps1
```

看到 `(venv)` 出現了嗎？✅

### 步驟 3：正確啟動 API

```powershell
uvicorn app.main:app --reload --log-level debug
```

**完成！** 🎉

---

## 🎯 根本原因

你可能是這樣做的（錯誤）：

### ❌ 錯誤方式 1：直接按 F5

```
在 VSCode 中打開 app/main.py
按 F5
選擇 "Python: 當前檔案"  ← 錯誤！
```

**問題**：這會直接運行 Python 檔案，找不到 `app` 模組

### ❌ 錯誤方式 2：直接運行 Python

```powershell
python app/main.py  ❌
python app\main.py  ❌
cd app; python main.py  ❌
```

**問題**：工作目錄不正確，Python 找不到模組

---

## ✅ 正確方式

### 方式 A：使用終端機（推薦初學者）

```powershell
# 1. 確保在正確目錄
cd D:\Robert\ML\MongoDB\ecommerce-api

# 2. 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 3. 使用 uvicorn 啟動
uvicorn app.main:app --reload --log-level debug
```

### 方式 B：使用 VSCode Debug（推薦深入學習）

**步驟 1：確認開啟的資料夾**

看 VSCode 左上角：
```
ECOMMERCE-API  ← 應該是這個
```

如果不是，請：
1. `檔案` → `開啟資料夾`
2. 選擇 `D:\Robert\ML\MongoDB\ecommerce-api`

**步驟 2：選擇正確的 Debug 配置**

1. 按 `F5`
2. 在頂部下拉選單選擇：**「Debug FastAPI」**
3. 不要選「Python: 當前檔案」！

**步驟 3：啟動**

點擊綠色播放按鈕 ▶️

---

## 🔍 如何檢查問題

### 檢查 1：確認工作目錄

在 PowerShell 或 VSCode 終端機中：

```powershell
pwd
```

應該顯示：
```
Path
----
D:\Robert\ML\MongoDB\ecommerce-api  ✅
```

如果不是，執行：
```powershell
cd D:\Robert\ML\MongoDB\ecommerce-api
```

### 檢查 2：確認虛擬環境

看命令提示字元前面有沒有 `(venv)`：

```powershell
(venv) PS D:\Robert\ML\MongoDB\ecommerce-api>  ✅ 正確
PS D:\Robert\ML\MongoDB\ecommerce-api>         ❌ 沒啟動
```

如果沒有，執行：
```powershell
.\venv\Scripts\Activate.ps1
```

### 檢查 3：確認 uvicorn 安裝

```powershell
uvicorn --version
```

如果顯示「找不到命令」，安裝它：
```powershell
pip install uvicorn[standard]
```

---

## 📊 對比：錯誤 vs 正確

| 做法 | 命令 | 結果 |
|------|------|------|
| ❌ 錯誤 | `python app/main.py` | ModuleNotFoundError |
| ❌ 錯誤 | `python app\main.py` | ModuleNotFoundError |
| ❌ 錯誤 | `cd app; python main.py` | ModuleNotFoundError |
| ✅ 正確 | `uvicorn app.main:app --reload` | 成功啟動！ |

---

## 🎓 為什麼會這樣？

### 簡單解釋

當 `main.py` 裡有這行代碼：
```python
from app.database import connect_to_mongo
```

Python 需要找到一個叫 `app` 的資料夾。

**如果你直接運行** `python app/main.py`：
```
當前目錄變成: app/
Python 在 app/ 裡找 app/ 資料夾 ← 找不到！❌
```

**如果你使用** `uvicorn app.main:app`：
```
當前目錄是: ecommerce-api/
Python 在 ecommerce-api/ 裡找 app/ 資料夾 ← 找到了！✅
```

### 專案結構示意

```
ecommerce-api/              ← 你應該在這裡執行 uvicorn
├── app/                    ← Python 要找的 'app' 模組
│   ├── __init__.py
│   ├── main.py             ← 這個檔案需要導入 app.database
│   ├── database.py         ← 要被導入的檔案
│   └── config.py
├── venv/                   ← 虛擬環境
└── tests/
```

---

## ✅ 成功的標誌

當你正確啟動後，應該看到：

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

[... 更多日誌 ...]

✅ 成功連接到 MongoDB 資料庫: ecommerce_db
✅ 應用程式啟動完成
================================================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**然後打開瀏覽器**訪問：http://localhost:8000/docs

---

## 🎯 記住這個

### 永遠使用這個命令啟動 FastAPI：

```powershell
uvicorn app.main:app --reload
```

### 不要使用：

```powershell
python app/main.py  ❌
python main.py      ❌
```

---

## 📚 延伸閱讀

- 完整排錯指南：`TROUBLESHOOTING.md`
- Debug 模式教學：`DEBUG_GUIDE.md`
- 快速開始：`QUICK_START.md`

---

## 💡 專業提示

### 建立一個啟動腳本（進階）

創建 `start.ps1`：

```powershell
# start.ps1
Set-Location D:\Robert\ML\MongoDB\ecommerce-api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

以後只要執行：
```powershell
.\start.ps1
```

---

## 🆘 還是不行？

### 終極解決方案（從頭開始）

```powershell
# 1. 關閉所有 PowerShell 視窗和 VSCode

# 2. 開啟新的 PowerShell

# 3. 執行以下命令（一次一行）
cd D:\Robert\ML\MongoDB\ecommerce-api
.\venv\Scripts\Activate.ps1
pip list | Select-String "uvicorn"
uvicorn app.main:app --reload --log-level debug
```

**如果還是不行**，檢查：
1. MongoDB 是否運行？`Get-Service -Name MongoDB`
2. 虛擬環境是否正確？看到 `(venv)` 了嗎？
3. 目錄是否正確？`pwd` 確認位置

---

**現在試試看正確的方式！** 🚀

記住：**永遠使用 `uvicorn app.main:app`** ！

