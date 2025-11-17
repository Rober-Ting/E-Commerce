# Phase 3 商品管理前端 Demo 使用指南

## 📋 概述

`frontend_products_demo.html` 是一个完整的商品管理前端演示页面，用于测试 Phase 3 的所有商品管理功能。

---

## 🚀 快速开始

### 1. 启动后端服务器

```bash
# 方法 1: 使用脚本
.\start_backend.ps1

# 方法 2: 直接运行
uvicorn app.main:app --reload
```

### 2. 启动前端服务器

```bash
# 方法 1: 使用脚本
.\start_frontend.ps1

# 方法 2: 使用 Python HTTP 服务器
python -m http.server 8080
```

### 3. 访问 Demo 页面

打开浏览器，访问：
```
http://localhost:8080/frontend_products_demo.html
```

---

## 👤 测试用户

### 管理员账户（推荐）
- **邮箱**: `admin@test.com`
- **密码**: `Admin123!`
- **权限**: 可以创建、编辑、删除所有商品

### 普通用户账户
- **邮箱**: `customer@test.com`
- **密码**: `Customer123!`
- **权限**: 只能查看商品

### 创建新用户
如果测试账户不存在，可以：
1. 先访问 `frontend_demo.html` 注册账户
2. 或使用 Swagger UI (`http://localhost:8000/docs`) 创建账户

---

## 🧪 功能测试清单

### ✅ Test 1: 商品创建功能

**测试步骤**:
1. 使用管理员账户登录
2. 点击右上角 "➕ 创建商品" 按钮
3. 填写商品信息：
   - 名称：MacBook Pro 14 吋 M3
   - 描述：全新 Apple M3 晶片
   - 价格：59900
   - 库存：10
   - 分类：筆記型電腦
   - 标签：Apple, MacBook, M3
4. 点击 "保存"

**预期结果**:
- ✅ 商品创建成功提示
- ✅ 商品出现在列表中
- ✅ 统计数据更新

**对应测试**: `TestProductCreation::test_create_product_as_admin`

---

### ✅ Test 2: 权限控制测试

**测试步骤**:
1. 登出管理员账户
2. 使用普通用户登录 (`customer@test.com`)
3. 观察界面变化

**预期结果**:
- ✅ "创建商品" 按钮不可见
- ✅ 商品卡片上没有 "编辑" 和 "删除" 按钮
- ✅ 只能查看商品详情

**对应测试**: 
- `TestProductCreation::test_create_product_as_customer`
- `TestProductCreation::test_create_product_without_auth`

---

### ✅ Test 3: 商品列表查询

**测试步骤**:
1. 使用管理员账户登录
2. 创建多个商品（至少 3 个）
3. 观察商品列表展示

**预期结果**:
- ✅ 所有商品正确显示
- ✅ 商品信息完整（名称、价格、库存、分类）
- ✅ 统计卡片显示正确数量

**对应测试**: `TestProductRetrieval::test_get_product_list`

---

### ✅ Test 4: 商品详情查询

**测试步骤**:
1. 点击任意商品的 "查看" 按钮
2. 查看弹出的详情对话框

**预期结果**:
- ✅ 显示商品完整信息
- ✅ 包含浏览次数、销售次数等统计数据
- ✅ 浏览次数自动增加

**对应测试**: `TestProductRetrieval::test_get_product_by_id`

---

### ✅ Test 5: 商品更新功能

**测试步骤**:
1. 点击任意商品的 "编辑" 按钮
2. 修改商品信息（如价格、库存）
3. 点击 "保存"

**预期结果**:
- ✅ 商品更新成功提示
- ✅ 列表中的商品信息自动更新
- ✅ 未修改的字段保持原值

**对应测试**: `TestProductUpdate::test_update_product`

---

### ✅ Test 6: 商品删除功能（软删除）

**测试步骤**:
1. 点击任意商品的 "删除" 按钮
2. 确认删除操作
3. 刷新页面

**预期结果**:
- ✅ 商品删除成功提示
- ✅ 商品从列表中消失
- ✅ 统计数量减少
- ✅ 再次访问该商品返回 404

**对应测试**: `TestProductDeletion::test_delete_product`

---

### ✅ Test 7: 商品搜索功能

**测试步骤**:
1. 创建以下测试商品：
   - MacBook Pro (Apple laptop)
   - iPhone 15 (Apple smartphone)
   - Dell XPS (Windows laptop)
2. 在左侧 "搜索关键词" 输入 "Apple"
3. 点击 "应用筛选"

**预期结果**:
- ✅ 只显示包含 "Apple" 的商品
- ✅ MacBook Pro 和 iPhone 15 显示
- ✅ Dell XPS 不显示

**对应测试**: `TestProductSearch::test_search_products`

---

### ✅ Test 8: 按分类筛选

**测试步骤**:
1. 创建不同分类的商品（如：笔记本电脑、手机）
2. 在左侧 "商品分类" 下拉框选择一个分类
3. 点击 "应用筛选"

**预期结果**:
- ✅ 只显示该分类的商品
- ✅ 其他分类的商品不显示

**对应测试**: `TestProductFiltering::test_filter_by_category`

---

### ✅ Test 9: 按价格区间筛选

**测试步骤**:
1. 创建不同价格的商品：
   - Product 1: ¥100
   - Product 2: ¥200
   - Product 3: ¥300
   - Product 4: ¥400
   - Product 5: ¥500
2. 在左侧设置价格区间：
   - 最低价格：200
   - 最高价格：400
3. 点击 "应用筛选"

**预期结果**:
- ✅ 只显示价格在 ¥200-¥400 的商品
- ✅ Product 2, 3, 4 显示
- ✅ Product 1 和 5 不显示

**对应测试**: `TestProductFiltering::test_filter_by_price_range`

---

### ✅ Test 10: 分页查询功能

**测试步骤**:
1. 创建至少 25 个商品
2. 观察分页控件
3. 点击 "下一页" 按钮
4. 观察页码变化

**预期结果**:
- ✅ 第一页显示 12 个商品
- ✅ 页码正确显示（如：第 1 页 / 共 3 页）
- ✅ 点击下一页后显示第二页商品
- ✅ 在最后一页时 "下一页" 按钮禁用

**对应测试**: `TestProductPagination::test_pagination`

---

### ✅ Test 11: 排序功能

**测试步骤**:
1. 在左侧 "排序方式" 选择不同选项：
   - 价格
   - 创建时间
   - 销量
   - 浏览量
2. 在 "排序方向" 选择：
   - 升序 (低→高)
   - 降序 (高→低)
3. 点击 "应用筛选"

**预期结果**:
- ✅ 商品按选定字段排序
- ✅ 排序方向正确
- ✅ 数据顺序符合预期

---

### ✅ Test 12: 快速搜索功能

**测试步骤**:
1. 在顶部搜索框输入关键词
2. 按 Enter 或点击 "搜索" 按钮

**预期结果**:
- ✅ 搜索结果即时显示
- ✅ 左侧筛选框同步更新
- ✅ 页码重置为第 1 页

---

### ✅ Test 13: 重置筛选功能

**测试步骤**:
1. 应用多个筛选条件
2. 点击 "重置" 按钮

**预期结果**:
- ✅ 所有筛选条件清空
- ✅ 显示全部商品
- ✅ 页码重置为第 1 页

---

## 🎨 界面功能说明

### 头部区域
- **标题**: 显示应用名称
- **用户信息**: 显示当前登录用户和角色
- **登出按钮**: 退出当前账户

### 统计卡片
- **总商品数**: 数据库中的商品总数
- **分类数**: 商品分类的数量
- **当前页**: 当前浏览的页码

### 左侧边栏（筛选区）
- **搜索关键词**: 在商品名称、描述、标签中搜索
- **商品分类**: 按分类筛选
- **价格区间**: 设置最低和最高价格
- **商品状态**: 筛选上架中/已下架/缺货商品
- **排序方式**: 选择排序字段
- **排序方向**: 升序或降序
- **应用筛选**: 执行筛选
- **重置**: 清除所有筛选条件

### 主内容区
- **快速搜索**: 顶部快速搜索框
- **创建商品**: 创建新商品（仅管理员/vendor）
- **商品列表**: 网格展示所有商品
- **分页控件**: 上一页/下一页，页码显示

### 商品卡片
- **商品图标**: 根据分类显示不同图标
- **商品名称**: 商品标题
- **商品描述**: 简短描述（最多 50 字符）
- **标签**: 最多显示 3 个标签
- **价格**: 以元为单位
- **统计**: 库存、销量、浏览量
- **操作按钮**: 查看/编辑/删除

---

## 🐛 常见问题

### Q1: 无法登录？
**A**: 确保：
1. 后端服务器正在运行（`http://localhost:8000`）
2. 使用正确的测试账户
3. 先在 `frontend_demo.html` 注册账户

### Q2: 创建商品按钮不可见？
**A**: 检查当前用户角色：
- 只有 `admin` 和 `vendor` 角色可以创建商品
- `customer` 角色只能查看商品

### Q3: 商品列表为空？
**A**: 
1. 检查是否有应用筛选条件
2. 点击 "重置" 按钮清除筛选
3. 创建一些测试商品

### Q4: 分页不工作？
**A**: 
1. 确保商品数量超过每页显示数量（12 个）
2. 刷新页面重新加载

### Q5: 搜索无结果？
**A**: 
1. 检查搜索关键词是否正确
2. 搜索是大小写不敏感的
3. 搜索范围：商品名称、描述、标签

---

## 💡 开发调试

### 打开浏览器开发者工具
- **Windows**: `F12` 或 `Ctrl + Shift + I`
- **Mac**: `Cmd + Option + I`

### 查看控制台日志
所有 API 请求和响应都会记录在控制台中，便于调试。

### 网络请求监控
在 "Network" 标签页可以查看：
- API 请求 URL
- 请求参数
- 响应数据
- HTTP 状态码

---

## 🎯 学习要点

### 1. JWT Token 管理
```javascript
// Token 存储在全局变量中
let currentToken = null;

// 每次 API 请求都携带 Token
headers: {
    'Authorization': `Bearer ${currentToken}`
}
```

### 2. 分页查询实现
```javascript
// 构建查询参数
const params = new URLSearchParams({
    page: currentPage,
    page_size: pageSize
});

// 发送请求
const response = await fetch(`${API_BASE_URL}/api/v1/products?${params}`);
```

### 3. 动态筛选
```javascript
// 收集筛选条件
const filters = {
    search: document.getElementById('searchKeyword').value,
    category: document.getElementById('filterCategory').value,
    min_price: document.getElementById('filterMinPrice').value,
    max_price: document.getElementById('filterMaxPrice').value
};

// 应用筛选
await loadProducts(filters);
```

### 4. 权限控制
```javascript
// 根据用户角色显示/隐藏功能
if (currentUser.role === 'customer') {
    document.getElementById('btnCreate').style.display = 'none';
}
```

### 5. CRUD 操作
```javascript
// CREATE (POST)
await fetch(`${API_BASE_URL}/api/v1/products`, {
    method: 'POST',
    body: JSON.stringify(productData)
});

// READ (GET)
await fetch(`${API_BASE_URL}/api/v1/products/${id}`);

// UPDATE (PUT)
await fetch(`${API_BASE_URL}/api/v1/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updateData)
});

// DELETE (DELETE)
await fetch(`${API_BASE_URL}/api/v1/products/${id}`, {
    method: 'DELETE'
});
```

---

## 📚 相关文档

- [PHASE3 进度文档](../02-development/PHASE3_PROGRESS.md)
- [PHASE3 完成总结](../02-development/PHASE3_COMPLETE.md)
- [API 测试指南](../03-testing/API_TESTING_GUIDE.md)
- [前端设置指南](./FRONTEND_SETUP.md)

---

## 🎉 总结

这个 Demo 提供了完整的商品管理功能测试界面，涵盖了 Phase 3 的所有测试用例：

✅ **12+ 个测试场景**  
✅ **完整的 CRUD 操作**  
✅ **搜索与筛选功能**  
✅ **分页查询**  
✅ **权限控制**  
✅ **实时数据更新**  

通过这个 Demo，你可以：
1. 🔍 **直观地看到 API 的工作原理**
2. 📖 **学习前后端如何交互**
3. 🧪 **验证所有商品管理功能**
4. 💻 **研究实际的代码实现**

---

**开始探索吧！** 🚀

如有任何问题，欢迎查看文档或提问！😊

