# 🚀 前端快速启动指南

## ⚡ 最简单的方法

### 1. 启动后端（如果还没启动）
```powershell
uvicorn app.main:app --reload
```

### 2. 启动前端
```powershell
python -m http.server 8080
```

### 3. 在浏览器中打开
```
http://localhost:8080/frontend_demo.html
```

---

## 🎯 当前状态检查

### 检查后端是否运行
```powershell
curl http://127.0.0.1:8000/health
```
✅ 看到 `"status":"healthy"` 就是正常

### 检查前端是否运行
```powershell
curl http://localhost:8080/frontend_demo.html
```
✅ 看到 HTTP 200 就是正常

---

## 🔧 常见问题

### 问题：8080 端口被占用
```powershell
# 换个端口
python -m http.server 8081

# 浏览器访问
http://localhost:8081/frontend_demo.html
```

### 问题：8000 端口被占用
```powershell
# 换个端口
uvicorn app.main:app --reload --port 8001

# 需要修改 frontend_demo.html 中的 API_BASE_URL
```

### 问题：连接服务器失败
1. ❌ 不要直接双击打开 HTML 文件
2. ✅ 必须通过 HTTP 服务器访问
3. ✅ 确保后端在运行

---

## 📋 测试账号

### 你的账号
```
Email: rob19940528@gmail.com
Password: (你注册时的密码)
```

### 测试账号
```
Email: testuser_163011@example.com
Password: NewSecurePass456!
```

---

## 🎓 为什么需要 HTTP 服务器？

### ❌ 直接打开 HTML（file://）
```
file:///D:/Robert/ML/MongoDB/ecommerce-api/frontend_demo.html
  ↓ (CORS 错误)
http://127.0.0.1:8000/api/v1/auth/login ❌
```

### ✅ 通过 HTTP 服务器（http://）
```
http://localhost:8080/frontend_demo.html
  ↓ (CORS 允许)
http://127.0.0.1:8000/api/v1/auth/login ✅
```

---

## 💡 开发技巧

### 查看网络请求
浏览器按 `F12` → Network 标签

### 查看控制台
浏览器按 `F12` → Console 标签

### 查看数据库
```powershell
python check_database.py
```

---

## 🎯 完整开发环境

```powershell
# 终端 1: MongoDB (如果未启动)
mongod

# 终端 2: 后端
uvicorn app.main:app --reload

# 终端 3: 前端
python -m http.server 8080

# 浏览器
http://localhost:8080/frontend_demo.html
```

---

**更新**: 2025-11-07

