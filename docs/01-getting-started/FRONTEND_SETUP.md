# 🎨 前端页面使用指南

## ❌ 为什么直接打开 HTML 文件会失败？

当你直接双击 `frontend_demo.html` 打开时，浏览器使用 `file://` 协议：
```
file:///D:/Robert/ML/MongoDB/ecommerce-api/frontend_demo.html
```

这会触发浏览器的 **CORS（跨域资源共享）安全策略**，阻止向 `http://127.0.0.1:8000` 发送请求。

---

## ✅ 正确的使用方法

### 方法 1: 使用 HTTP 服务器（推荐）⭐

#### 步骤 1: 启动后端服务器
打开**第一个** PowerShell 窗口：
```powershell
.\start_backend.ps1
```
或者：
```powershell
uvicorn app.main:app --reload
```

**输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### 步骤 2: 启动前端服务器
打开**第二个** PowerShell 窗口：
```powershell
.\start_frontend.ps1
```
或者：
```powershell
python -m http.server 8080
```

**输出**：
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

#### 步骤 3: 在浏览器中访问
```
http://localhost:8080/frontend_demo.html
```

✅ **现在就可以正常登录注册了！**

---

### 方法 2: 使用 FastAPI /docs（更简单）

如果不想启动前端服务器，直接使用 FastAPI 自带的文档界面：

1. 启动后端：
```powershell
uvicorn app.main:app --reload
```

2. 浏览器打开：
```
http://127.0.0.1:8000/docs
```

3. 在界面中测试所有 API

---

## 🔍 故障排查

### 问题 1: "连接服务器失败"

**原因**: CORS 问题或后端未启动

**解决**:
```powershell
# 1. 检查后端是否运行
curl http://127.0.0.1:8000/health

# 2. 确保使用 HTTP 服务器访问前端
# ❌ 错误: file:///D:/Robert/...
# ✅ 正确: http://localhost:8080/frontend_demo.html
```

### 问题 2: "Failed to fetch"

**原因**: 端口冲突或服务器未启动

**解决**:
```powershell
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# 如果被占用，杀死进程或换端口
# 换后端端口:
uvicorn app.main:app --reload --port 8001

# 换前端端口:
python -m http.server 8081
```

### 问题 3: 浏览器控制台显示 CORS 错误

**原因**: CORS 配置未生效

**解决**:
1. 重启后端服务器
2. 确认 `app/config.py` 中 `DEBUG = True`
3. 清除浏览器缓存（Ctrl+Shift+Delete）

---

## 📊 端口说明

| 服务 | 端口 | 地址 | 用途 |
|------|------|------|------|
| 后端 API | 8000 | http://127.0.0.1:8000 | FastAPI 服务器 |
| 前端页面 | 8080 | http://localhost:8080 | 静态文件服务器 |
| API 文档 | 8000 | http://127.0.0.1:8000/docs | Swagger UI |
| MongoDB | 27017 | mongodb://localhost:27017 | 数据库 |

---

## 🎯 完整启动流程

### 开发环境

```powershell
# 终端 1: 启动 MongoDB（如果未启动）
mongod

# 终端 2: 启动后端
cd D:\Robert\ML\MongoDB\ecommerce-api
.\venv\Scripts\activate
uvicorn app.main:app --reload

# 终端 3: 启动前端（可选）
python -m http.server 8080

# 浏览器访问
# 前端: http://localhost:8080/frontend_demo.html
# API文档: http://127.0.0.1:8000/docs
```

---

## 💡 开发技巧

### 1. 查看网络请求
在浏览器中按 `F12` 打开开发者工具，切换到 "Network" 标签，可以看到：
- HTTP 请求详情
- 请求头和响应头
- CORS 相关信息
- 错误原因

### 2. 查看控制台日志
在 "Console" 标签中可以看到：
- JavaScript 错误
- 网络请求失败原因
- 自定义日志输出

### 3. 测试 CORS
在控制台中手动发送请求：
```javascript
fetch('http://127.0.0.1:8000/health')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error('错误:', err));
```

---

## 🚀 生产环境部署

### 前端部署选项
1. **Vercel** - 推荐用于静态站点
2. **Netlify** - 简单快速
3. **GitHub Pages** - 免费
4. **Nginx** - 自己的服务器

### 后端部署选项
1. **Railway** - 推荐用于 FastAPI
2. **Heroku** - 传统选择
3. **AWS EC2** - 完全控制
4. **Docker + VPS** - 最灵活

---

## 📚 相关文档

- [API 测试指南](API_TESTING_GUIDE.md)
- [CORS 测试指南](docs/02-development/TEST_CORS_GUIDE.md)
- [Phase 2 完成报告](docs/02-development/PHASE2_PROGRESS.md)

---

## 🆘 还是不行？

1. **查看后端日志**
   ```powershell
   # 后端终端会显示所有请求日志
   INFO:     127.0.0.1:52345 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
   ```

2. **检查数据库连接**
   ```powershell
   python check_database.py
   ```

3. **运行自动测试**
   ```powershell
   .\test_api_manual.ps1
   ```

4. **查看问题记录**
   - [Phase 2 疑难排解](docs/05-troubleshooting/PHASE2_TROUBLESHOOTING.md)
   - [通用疑难排解](docs/05-troubleshooting/TROUBLESHOOTING.md)

---

**最后更新**: 2025-11-07  
**作者**: AI Assistant + Robert

