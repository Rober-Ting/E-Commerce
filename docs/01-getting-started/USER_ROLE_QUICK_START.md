# 用戶角色註冊 - 快速開始

## 🎯 目標

本指南幫助你快速了解和使用新的用戶角色註冊功能。

---

## 🚀 快速開始（3 步驟）

### 步驟 1: 初始化管理員賬戶

首次使用前，必須創建管理員賬戶：

```powershell
.\init_users.ps1
```

**輸入提示**: 當詢問「是否同時創建測試用戶？」時，輸入 `y` 可同時創建測試的 vendor 和 customer 賬戶。

**創建的賬戶**:
```
🔐 管理員 (Admin):
   📧 admin@ecommerce.com
   🔒 Admin123!

🏪 測試商家 (Vendor):
   📧 vendor@test.com
   🔒 Vendor123!

👤 測試顧客 (Customer):
   📧 customer@test.com
   🔒 Customer123!
```

⚠️ **安全提示**: 首次登錄後請立即修改 admin 密碼！

---

### 步驟 2: 啟動服務

在兩個不同的終端中分別運行：

**終端 1 - 後端**:
```powershell
.\start_backend.ps1
```

**終端 2 - 前端**:
```powershell
.\start_frontend.ps1
```

---

### 步驟 3: 測試註冊功能

訪問: `http://localhost:8080/frontend_demo.html`

#### 註冊為顧客 (Customer):
1. 點擊「註冊」標籤
2. 填寫資料
3. 選擇「👤 顧客 (Customer)」
4. 點擊「註冊」

#### 註冊為商家 (Vendor):
1. 點擊「註冊」標籤
2. 填寫資料
3. 選擇「🏪 商家 (Vendor)」← **重點！**
4. 點擊「註冊」

---

## 🎭 角色對比

| 角色 | 註冊方式 | 主要功能 |
|------|----------|----------|
| **Customer** 👤 | ✅ 可註冊 (默認) | 購買商品、管理訂單 |
| **Vendor** 🏪 | ✅ 可註冊 (需選擇) | Customer 功能 + 上傳管理商品 |
| **Admin** 🔐 | ❌ 不可註冊 | 管理所有用戶和商品 |

---

## 🧪 快速測試

### 測試 1: 使用測試賬戶登錄

使用初始化時創建的測試賬戶：

1. **商家賬戶**:
   - Email: `vendor@test.com`
   - Password: `Vendor123!`
   - 登錄後可以上傳商品

2. **顧客賬戶**:
   - Email: `customer@test.com`
   - Password: `Customer123!`
   - 登錄後只能瀏覽商品

---

### 測試 2: 註冊新商家

1. 訪問前端 Demo
2. 點擊「註冊」
3. 填寫以下資料:
   ```
   📧 Email: myshop@example.com
   🔒 Password: MyShop123!
   👤 姓名: 我的小店
   📱 電話: 0912345678
   🎭 身份: 商家 (Vendor)  ← 選擇這個！
   ```
4. 點擊「註冊」
5. 註冊成功後，使用此賬戶登錄
6. 前往商品管理頁面測試上傳商品

---

### 測試 3: 嘗試註冊為 Admin (應該失敗)

使用 Swagger UI (`http://localhost:8000/docs`):

1. 找到 `POST /api/v1/auth/register`
2. 點擊「Try it out」
3. 輸入:
   ```json
   {
     "email": "hacker@example.com",
     "password": "Hacker123!",
     "full_name": "黑客",
     "phone": "0999999999",
     "role": "admin"
   }
   ```
4. 點擊「Execute」

**預期結果**: ❌ 收到錯誤訊息
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Cannot register as admin. Admin accounts must be created by system administrators."
  }
}
```

✅ 這證明了安全機制正常工作！

---

## 💡 實用場景

### 場景 1: 我想開一個網店賣商品
```
1. 註冊為 Vendor
2. 登錄後上傳商品
3. 設置價格、庫存、描述
4. 商品自動上架
```

### 場景 2: 我只想買東西
```
1. 註冊為 Customer (默認)
2. 瀏覽商品
3. 加入購物車
4. 下單購買
```

### 場景 3: 我是系統管理員
```
1. 運行 init_users.ps1 創建 Admin 賬戶
2. 使用 Admin 登錄
3. 立即修改密碼
4. 管理用戶和商品
```

---

## 🔧 密碼要求

註冊時密碼必須符合：
- ✅ 至少 8 個字符
- ✅ 至少 1 個大寫字母
- ✅ 至少 1 個小寫字母
- ✅ 至少 1 個數字

**有效密碼示例**:
- `MyPass123`
- `SecurePassword1`
- `Vendor123!`

**無效密碼示例**:
- `abc123` ❌ (太短，沒有大寫)
- `password` ❌ (沒有大寫，沒有數字)
- `PASSWORD123` ❌ (沒有小寫)

---

## ❓ 常見問題

**Q: 我註冊時忘記選擇 Vendor，現在只是 Customer，怎麼辦？**
A: 請聯繫管理員，管理員可以將你的角色升級為 Vendor。

**Q: 可以註冊多個 Vendor 賬戶嗎？**
A: 可以！每個商家都可以有自己的獨立賬戶。

**Q: Vendor 和 Customer 的主要區別是什麼？**
A: Vendor 可以上傳和管理商品，Customer 只能購買商品。

**Q: 如何成為 Admin？**
A: Admin 角色只能由系統管理員通過初始化腳本創建或由現有 Admin 升級。

---

## 📚 延伸閱讀

- 📖 [完整角色說明](USER_ROLE_REGISTRATION.md)
- 🧪 [API 測試指南](../05-troubleshooting/API_TESTING_GUIDE.md)
- 🎨 [前端 Demo 指南](PHASE3_FRONTEND_DEMO_GUIDE.md)

---

## ✅ 檢查清單

完成以下步驟，確保你已經掌握了用戶角色功能：

- [ ] 運行 `init_users.ps1` 創建管理員賬戶
- [ ] 啟動後端和前端服務
- [ ] 使用測試賬戶 (vendor@test.com) 登錄
- [ ] 註冊一個新的 Vendor 賬戶
- [ ] 註冊一個新的 Customer 賬戶
- [ ] 使用 Swagger UI 測試 API
- [ ] 嘗試註冊為 Admin (應該失敗)
- [ ] 修改 Admin 默認密碼

---

**最後更新**: 2025-11-13
**相關版本**: Phase 3

