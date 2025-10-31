# E-Commerce API - MongoDB 電商訂單管理系統

> 基於 FastAPI + MongoDB 的現代化電商訂單管理系統

## 📋 專案簡介

本專案是一個功能完整的電商訂單管理系統後端 API，採用 FastAPI 框架和 MongoDB 資料庫，提供用戶管理、商品管理、訂單處理和數據分析等功能。

## 🚀 技術棧

- **後端框架**: FastAPI
- **資料庫**: MongoDB 8.2+
- **資料庫驅動**: Motor (異步 PyMongo)
- **認證**: JWT (JSON Web Tokens)
- **密碼加密**: bcrypt
- **資料驗證**: Pydantic
- **Python 版本**: 3.10+

## 📁 專案結構

```
ecommerce-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # MongoDB 連線
│   ├── models/              # Pydantic 資料模型
│   ├── api/                 # API 路由
│   │   └── v1/              # API v1 版本
│   ├── services/            # 業務邏輯層
│   ├── utils/               # 工具函數
│   └── middleware/          # 中介軟體
├── tests/                   # 測試
├── scripts/                 # 腳本
├── .env                     # 環境變數（不提交）
├── .env.example             # 環境變數範例
├── .gitignore
├── requirements.txt         # Python 依賴
└── README.md               # 本文件
```

## ⚙️ 環境設定

### 先決條件

- Python 3.10 或更高版本
- MongoDB 6.0 或更高版本
- Git

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/Rober-Ting/E-Commerce.git
   cd E-Commerce
   ```

2. **建立虛擬環境**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   # 複製環境變數範例檔案
   copy .env.example .env
   
   # 編輯 .env 檔案，設定您的配置
   # 特別注意要修改 SECRET_KEY
   ```

5. **啟動 MongoDB**
   ```bash
   # Windows
   mongod --dbpath "C:\data\db"
   
   # 或使用 MongoDB 服務
   ```

6. **運行應用程式**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **訪問 API 文檔**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔧 開發指令

```bash
# 啟動開發伺服器（熱重載）
uvicorn app.main:app --reload

# 運行測試
pytest

# 測試覆蓋率
pytest --cov=app tests/

# 格式化程式碼
black app/

# 檢查程式碼品質
pylint app/
```

## 📚 API 端點

### 認證
- `POST /api/v1/auth/register` - 用戶註冊
- `POST /api/v1/auth/login` - 用戶登入
- `GET /api/v1/auth/me` - 獲取當前用戶

### 用戶管理
- `GET /api/v1/users` - 用戶列表（管理員）
- `GET /api/v1/users/{id}` - 用戶詳情
- `PUT /api/v1/users/{id}` - 更新用戶

### 商品管理
- `GET /api/v1/products` - 商品列表
- `GET /api/v1/products/{id}` - 商品詳情
- `POST /api/v1/products` - 新增商品（管理員）
- `PUT /api/v1/products/{id}` - 更新商品（管理員）
- `DELETE /api/v1/products/{id}` - 刪除商品（管理員）

### 訂單管理
- `GET /api/v1/orders` - 訂單列表
- `GET /api/v1/orders/{id}` - 訂單詳情
- `POST /api/v1/orders` - 建立訂單
- `PATCH /api/v1/orders/{id}/status` - 更新訂單狀態（管理員）

### 數據分析
- `GET /api/v1/analytics/sales/summary` - 銷售總覽
- `GET /api/v1/analytics/products/top-selling` - 最暢銷商品

詳細 API 文檔請參考 Swagger UI。

## 🧪 測試

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_auth.py

# 查看測試覆蓋率
pytest --cov=app --cov-report=html tests/
```

## 📖 文檔

完整的專案文檔位於 `Documents/` 目錄：

- [專案總覽](../Documents/PROJECT_SUMMARY.md)
- [開發路線圖](../Documents/ecommerce_development_roadmap.md)
- [技術架構](../Documents/ecommerce_technical_architecture.md)
- [API 文檔](../Documents/ecommerce_api_documentation.md)
- [資料模型](../Documents/ecommerce_data_model_design.md)

## 🔐 安全性

- 密碼使用 bcrypt 加密
- JWT Token 認證
- 輸入資料驗證
- CORS 設定
- 敏感資訊不寫入日誌

## 🚢 部署

### Docker

```bash
# 建立映像
docker build -t ecommerce-api .

# 運行容器
docker run -p 8000:8000 ecommerce-api

# 使用 Docker Compose
docker-compose up -d
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 👨‍💻 作者

開發團隊

---

**專案狀態**: ✅ Phase 1 完成 - 基礎架構已搭建

**當前版本**: v0.1.0 (Phase 1)

**最後更新**: 2025-10-31

**GitHub**: https://github.com/Rober-Ting/E-Commerce

### 開發進度

- ✅ **Phase 1**: 基礎架構設置（完成）
  - FastAPI 應用搭建
  - MongoDB 數據庫連接
  - 環境配置管理
  - CORS 中介軟體
  - 健康檢查端點
  - 完整日誌系統

- 📝 **Phase 2**: 用戶認證系統（規劃中）
- 📝 **Phase 3**: 商品管理（規劃中）
- 📝 **Phase 4**: 訂單系統（規劃中）
- 📝 **Phase 5**: 數據分析（規劃中）

