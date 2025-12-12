# 调试 "Failed to fetch" 错误

## 🐛 错误信息
```
TypeError: Failed to fetch
at HTMLFormElement.<anonymous> (http://localhost:8080/frontend_orders_demo.html:1045:40)
```

## 🔍 可能的原因

### 1. 后端虽然运行，但代码有错误（最可能）
后端在处理请求时抛出异常，导致连接中断。

### 2. CORS 跨域问题
浏览器阻止了跨域请求。

### 3. Token 格式错误
Authorization header 格式不正确。

### 4. 网络问题
防火墙或代理阻止了请求。

---

## 🔧 调试步骤

### 步骤 1：检查浏览器控制台的详细信息

1. **打开开发者工具** (F12)

2. **切换到 Console 标签**
   查看是否有其他错误信息，特别是：
   - CORS 相关错误
   - 网络错误
   - 其他 JavaScript 错误

3. **查看 "订单数据" 日志**
   在控制台中应该能看到：
   ```javascript
   订单数据: {
       items: [...],
       shipping_address: {...},
       payment_method: "..."
   }
   ```
   
   **请检查这个对象是否完整？**

4. **切换到 Network 标签**
   - 点击 "确认下单" 按钮
   - 查找 `orders` 请求
   - 检查请求状态：
     - **如果显示红色**：请求失败
     - **如果没有出现**：请求未发送
     - **如果是灰色**：请求被取消

5. **查看请求详情**（如果请求出现）
   - 点击 `orders` 请求
   - 查看 Headers 标签
   - 查看 Payload 标签
   - 查看 Response 标签（如果有响应）

---

### 步骤 2：检查后端日志

在后端运行的终端窗口中，查看是否有错误信息。

**常见错误**：
```python
# 可能的错误 1：KeyError
KeyError: 'id'

# 可能的错误 2：AttributeError
AttributeError: 'dict' object has no attribute 'get'

# 可能的错误 3：ValidationError
pydantic.error_wrappers.ValidationError: ...
```

---

### 步骤 3：测试简单请求

在浏览器控制台中直接执行：

```javascript
// 1. 检查 API_BASE_URL
console.log('API_BASE_URL:', API_BASE_URL);

// 2. 检查 Token
console.log('Token:', currentToken);

// 3. 测试简单的 GET 请求
fetch(`${API_BASE_URL}/api/v1/products?page_size=1`)
  .then(r => r.json())
  .then(d => console.log('Products:', d))
  .catch(e => console.error('Error:', e));

// 4. 测试登录状态
fetch(`${API_BASE_URL}/api/v1/users/me`, {
  headers: {
    'Authorization': `Bearer ${currentToken}`
  }
})
  .then(r => r.json())
  .then(d => console.log('Current User:', d))
  .catch(e => console.error('Error:', e));
```

---

### 步骤 4：使用 curl 测试 API

在终端中执行：

```powershell
# 1. 先登录获取 Token
$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"vendor@test.com","password":"Vendor123!"}'

$token = $loginResponse.data.access_token
Write-Host "Token: $token"

# 2. 测试创建订单（需要先准备商品ID）
$orderData = @{
    items = @(
        @{
            product_id = "你的商品ID"
            product_name = "测试商品"
            price = 100.0
            quantity = 1
            subtotal = 100.0
        }
    )
    shipping_address = @{
        recipient = "测试用户"
        phone = "0912345678"
        address_line1 = "测试地址"
        city = "台北市"
        postal_code = "100"
        country = "Taiwan"
    }
    payment_method = "credit_card"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/orders" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -ContentType "application/json" `
  -Body $orderData
```

---

## 🚨 常见问题修复

### 问题 1：后端代码有错误

**检查方法**：
查看后端终端是否有错误堆栈信息

**可能的错误**：
```python
# 如果看到类似这样的错误
TypeError: 'NoneType' object is not subscriptable
# 或
KeyError: 'id'
```

**解决方案**：
后端代码可能需要进一步调整。

---

### 问题 2：CORS 错误

**症状**：
浏览器控制台显示：
```
Access to fetch at 'http://127.0.0.1:8000/api/v1/orders' from origin 
'http://localhost:8080' has been blocked by CORS policy
```

**解决方案**：
检查 `app/main.py` 中的 CORS 配置：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 问题 3：Token 无效

**症状**：
- Token 是 null 或 undefined
- Token 格式不正确

**检查方法**：
```javascript
console.log('Current Token:', currentToken);
console.log('Token length:', currentToken?.length);
```

**解决方案**：
重新登录获取新 Token

---

### 问题 4：后端崩溃

**症状**：
- 后端终端显示错误后停止
- 无法访问 http://127.0.0.1:8000/docs

**解决方案**：
```powershell
# 重启后端
# 先按 Ctrl+C 停止
# 然后重新启动
.\start_backend.ps1
```

---

## 🔍 深度调试

### 方法 1：添加详细日志

修改前端代码，添加更多日志：

```javascript
document.getElementById('checkoutForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    console.log('=== 开始创建订单 ===');
    console.log('1. API_BASE_URL:', API_BASE_URL);
    console.log('2. currentToken:', currentToken);
    console.log('3. currentToken length:', currentToken?.length);
    
    // ... 构建订单数据 ...
    
    console.log('4. 订单数据:', orderData);
    console.log('5. 订单数据 JSON:', JSON.stringify(orderData, null, 2));
    
    try {
        console.log('6. 开始发送请求...');
        const response = await fetch(`${API_BASE_URL}/api/v1/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(orderData)
        });
        
        console.log('7. 收到响应:', response);
        console.log('8. 响应状态:', response.status);
        console.log('9. 响应 OK:', response.ok);
        
        const data = await response.json();
        console.log('10. 响应数据:', data);
        
        // ... 处理响应 ...
    } catch (error) {
        console.error('11. 捕获错误:', error);
        console.error('12. 错误名称:', error.name);
        console.error('13. 错误消息:', error.message);
        console.error('14. 错误堆栈:', error.stack);
    }
});
```

### 方法 2：检查后端端点

访问 Swagger UI 测试：
```
http://127.0.0.1:8000/docs
```

1. 找到 `POST /api/v1/orders`
2. 点击 "Try it out"
3. 点击右上角 🔒 Authorize
4. 输入 Token（从登录获取）
5. 填写订单数据
6. 点击 Execute

**如果 Swagger UI 也失败**：说明后端代码有问题
**如果 Swagger UI 成功**：说明前端请求有问题

---

## 📋 检查清单

完成以下检查并告诉我结果：

### 浏览器控制台
- [ ] Console 中是否有 CORS 错误？
- [ ] Console 中"订单数据"日志是否完整？
- [ ] Network 中是否看到 `orders` 请求？
- [ ] 请求状态码是什么？
- [ ] Token 是否有效？（不是 null/undefined）

### 后端日志
- [ ] 后端终端是否有错误信息？
- [ ] 后端是否仍在运行？
- [ ] 能否访问 http://127.0.0.1:8000/docs ？

### 简单测试
- [ ] 执行控制台中的测试脚本，产品查询是否成功？
- [ ] 用户信息查询是否成功？

---

## 🆘 下一步

请按照以上步骤检查，然后告诉我：

1. **浏览器 Console 中的完整错误信息**
   - 截图或复制文本
   
2. **浏览器 Network 标签的情况**
   - 是否看到 `orders` 请求？
   - 如果看到，状态码是什么？
   
3. **后端终端的输出**
   - 是否有错误信息？
   - 最后几行日志是什么？

4. **"订单数据" 日志的内容**
   - 数据结构是否完整？

提供这些信息后，我可以精准定位问题！😊

