# 🧪 CORS 跨域測試指南

## 快速開始

### 步驟 1：啟動你的 FastAPI 服務器
```powershell
# 在專案目錄下
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 步驟 2：在不同端口打開測試頁面

打開**新的 PowerShell 視窗**，執行以下命令：

#### 測試場景 1：端口 3000 (模擬前端應用)
```powershell
# 在專案目錄下
python -m http.server 3000
```

然後在瀏覽器打開：
- http://localhost:3000/test_cors.html

#### 測試場景 2：端口 5000 (模擬另一個應用)
```powershell
# 再開一個 PowerShell 視窗
python -m http.server 5000
```

然後在瀏覽器打開：
- http://localhost:5000/test_cors.html

#### 測試場景 3：直接打開文件（file:// 協議）
```powershell
# 在 Windows 檔案總管中，雙擊 test_cors.html
# 或者直接拖到瀏覽器
```

## 理解測試結果

### ✅ 成功情況（CORS 允許）

如果你看到綠色的成功訊息：
```
✅ 請求成功！
狀態碼: 200
響應數據: {...}
```

**這表示：**
- CORS 中介軟體正確配置
- 當前來源被允許訪問 API
- 伺服器返回了正確的 CORS 標頭

### ❌ 失敗情況（CORS 阻止）

如果你看到紅色的錯誤訊息：
```
❌ 請求失敗！
錯誤訊息: Failed to fetch
CORS policy: No 'Access-Control-Allow-Origin' header
```

**這表示：**
- 當前來源沒有被允許
- 需要修改 FastAPI 的 CORS 配置

## 測試不同 CORS 配置

### 配置 1：允許所有來源（開發模式）
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**測試結果：**
- ✅ http://localhost:3000 → 成功
- ✅ http://localhost:5000 → 成功  
- ✅ http://127.0.0.1:3000 → 成功
- ⚠️ file:///... → 可能失敗（某些瀏覽器不支援）

### 配置 2：只允許特定來源（生產模式）
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://myapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**測試結果：**
- ✅ http://localhost:3000 → 成功（在允許清單中）
- ❌ http://localhost:5000 → 失敗（不在允許清單中）
- ❌ http://127.0.0.1:3000 → 失敗（localhost ≠ 127.0.0.1）

### 配置 3：不允許帶認證 + 萬用字元
```python
# ⚠️ 這是錯誤配置！
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # ❌ 不能同時使用！
)
```

**測試結果：**
- ❌ 所有帶 `credentials: 'include'` 的請求都會失敗

## 進階測試技巧

### 1. 使用瀏覽器開發者工具

在測試頁面按 `F12` 打開開發者工具，查看：

**Network 標籤頁：**
```
Request Headers:
  Origin: http://localhost:3000
  
Response Headers:
  Access-Control-Allow-Origin: http://localhost:3000
  Access-Control-Allow-Credentials: true
  Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

**Console 標籤頁：**
```
如果有 CORS 錯誤，會顯示詳細的錯誤訊息
```

### 2. 測試 OPTIONS 預檢請求

對於某些請求（例如 POST、PUT、自定義標頭），瀏覽器會先發送 OPTIONS 請求：

```javascript
// 在測試頁面的 Console 中執行
fetch('http://127.0.0.1:8000/health', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Custom-Header': 'test'  // 自定義標頭會觸發預檢
    }
});
```

你會在 Network 看到兩個請求：
1. **OPTIONS** /health ← 預檢請求
2. **POST** /health ← 實際請求

### 3. 測試不同的 HTTP 方法

```javascript
// DELETE 請求
fetch('http://127.0.0.1:8000/api/test', {
    method: 'DELETE'
});

// PUT 請求
fetch('http://127.0.0.1:8000/api/test', {
    method: 'PUT',
    body: JSON.stringify({data: 'test'})
});
```

## 常見問題

### Q1: localhost 和 127.0.0.1 有什麼區別？
**A:** 對於 CORS 來說，它們是**不同的來源**！

```
http://localhost:3000    ← 不同來源
http://127.0.0.1:3000    ← 不同來源
```

如果要兩者都允許：
```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

### Q2: 為什麼 Postman 不會有 CORS 問題？
**A:** 因為 Postman 不是瀏覽器，不受**同源政策**限制。

CORS 只影響：
- ✅ 瀏覽器中的 JavaScript fetch/XMLHttpRequest
- ❌ 不影響 Postman、curl、Python requests

### Q3: file:// 協議能測試 CORS 嗎？
**A:** 不建議。大多數瀏覽器對 `file://` 有特殊限制。

使用 `python -m http.server` 更可靠。

### Q4: 如何在實際前端專案中測試？

**React 範例：**
```javascript
// src/App.js
useEffect(() => {
    fetch('http://127.0.0.1:8000/health')
        .then(res => res.json())
        .then(data => console.log(data))
        .catch(err => console.error('CORS error:', err));
}, []);
```

**Vue 範例：**
```javascript
// src/components/Test.vue
mounted() {
    fetch('http://127.0.0.1:8000/health')
        .then(res => res.json())
        .then(data => console.log(data));
}
```

## 檢查清單

在測試前確認：

- [ ] FastAPI 伺服器正在運行（http://127.0.0.1:8000）
- [ ] 可以訪問 http://127.0.0.1:8000/docs（應該看到 Swagger UI）
- [ ] 測試伺服器在不同端口運行（3000、5000 等）
- [ ] 瀏覽器開發者工具已打開（F12）
- [ ] 檢查 Console 和 Network 標籤頁

## 快速命令參考

```powershell
# 終端 1：FastAPI 伺服器
uvicorn app.main:app --reload --port 8000

# 終端 2：測試伺服器端口 3000
python -m http.server 3000

# 終端 3：測試伺服器端口 5000
python -m http.server 5000
```

然後訪問：
- 測試工具 1: http://localhost:3000/test_cors.html
- 測試工具 2: http://localhost:5000/test_cors.html
- API 文檔: http://127.0.0.1:8000/docs

---

Happy Testing! 🎉

