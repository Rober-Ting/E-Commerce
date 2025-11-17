# PHASE 3: 商品管理 - 开发进度

## 📅 开发时间
**开始日期**: 2025-11-11  
**预计完成**: Week 3 (3-5 天)  
**当前状态**: 🚀 准备开始

---

## 🎯 阶段目标

实现完整的商品管理功能，包括：
- ✅ 商品 CRUD 操作
- ✅ 商品搜索与筛选
- ✅ 分类管理
- ✅ 库存管理
- ✅ 分页查询
- ✅ 权限控制（管理员/店家可管理，所有人可查看）

---

## 📋 任务清单

### Day 1: 商品数据模型 (预计 4-6 小时)

#### ✅ 任务 1.1: 创建 Pydantic 模型
**文件**: `app/models/product.py`

**需要创建的模型**:
```python
1. ProductBase        # 基础模型
2. ProductCreate      # 创建商品
3. ProductUpdate      # 更新商品
4. ProductResponse    # API 响应
5. ProductInDB        # 数据库存储
6. ProductListFilter  # 列表筛选参数
7. ProductStatus      # 商品状态枚举
```

**关键特性**:
- [ ] 使用 Decimal/float 处理价格（避免浮点误差）
- [ ] 支持多图片（List[str]）
- [ ] 支持标签系统（List[str]）
- [ ] 支持可选属性（Dict[str, Any]）
- [ ] 软删除机制（is_deleted）
- [ ] 库存数量验证（>= 0）
- [ ] 价格验证（> 0）

**验收标准**:
- [ ] 所有模型定义完成
- [ ] 字段验证规则正确
- [ ] 类型注解完整
- [ ] 文档字符串清晰

---

### Day 1-2: 商品服务层 (预计 6-8 小时)

#### ✅ 任务 2.1: 创建 ProductService
**文件**: `app/services/product_service.py`

**需要实现的方法**:
```python
1. create_product()           # 创建商品
2. get_product_by_id()        # 获取单个商品
3. get_products()             # 获取商品列表（分页、筛选、搜索）
4. update_product()           # 更新商品
5. delete_product()           # 软删除商品
6. update_stock()             # 更新库存
7. search_products()          # 搜索商品（文本搜索）
8. get_products_by_category() # 按分类获取
9. check_stock_available()    # 检查库存是否足够
```

**关键功能**:
- [ ] 商品搜索（name, description, tags）
- [ ] 商品筛选（category, price_range, status）
- [ ] 分页查询（skip, limit）
- [ ] 库存管理（扣减、增加）
- [ ] 软删除（is_deleted = True）
- [ ] 自动更新 updated_at 时间戳

**性能优化**:
- [ ] 使用投影（projection）减少数据传输
- [ ] 合理使用索引
- [ ] 限制返回字段

**验收标准**:
- [ ] 所有方法实现完成
- [ ] 错误处理完善
- [ ] 使用自定义异常
- [ ] 日志记录完整

---

### Day 2-3: 商品 API 端点 (预计 4-6 小时)

#### ✅ 任务 3.1: 创建 API 路由
**文件**: `app/api/v1/products.py`

**需要实现的端点**:

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/api/v1/products` | 获取商品列表 | 所有人 |
| GET | `/api/v1/products/{product_id}` | 获取商品详情 | 所有人 |
| POST | `/api/v1/products` | 创建商品 | admin/vendor |
| PUT | `/api/v1/products/{product_id}` | 更新商品 | admin/vendor |
| DELETE | `/api/v1/products/{product_id}` | 删除商品 | admin/vendor |
| GET | `/api/v1/products/search` | 搜索商品 | 所有人 |
| GET | `/api/v1/products/category/{category}` | 按分类获取 | 所有人 |

**查询参数支持**:
- [ ] `page`: 页码（默认 1）
- [ ] `page_size`: 每页数量（默认 10，最大 100）
- [ ] `search`: 搜索关键词
- [ ] `category`: 商品分类
- [ ] `min_price`: 最低价格
- [ ] `max_price`: 最高价格
- [ ] `status`: 商品状态（active, inactive, out_of_stock）
- [ ] `sort_by`: 排序字段（price, created_at, sales_count）
- [ ] `order`: 排序方向（asc, desc）

**响应格式**:
```python
# 列表响应
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  },
  "error": null,
  "timestamp": "2025-11-11T12:00:00Z"
}

# 单个商品响应
{
  "success": true,
  "data": {
    "id": "...",
    "name": "...",
    ...
  },
  "error": null,
  "timestamp": "2025-11-11T12:00:00Z"
}
```

**验收标准**:
- [ ] 所有端点实现完成
- [ ] 权限控制正确
- [ ] 参数验证完善
- [ ] 错误响应统一
- [ ] 使用自定义异常
- [ ] Swagger 文档完整

---

### Day 3: 数据库索引 (预计 1-2 小时)

#### ✅ 任务 4.1: 创建索引脚本
**文件**: `scripts/create_product_indexes.py`

**需要创建的索引**:
```javascript
1. name (单字段索引) - 商品名称查询
2. category (单字段索引) - 分类筛选
3. status (单字段索引) - 状态筛选
4. tags (单字段索引) - 标签查询
5. price (单字段索引) - 价格排序
6. {name, description, tags} (文本索引) - 全文搜索
7. {category, status, price} (复合索引) - 常用组合查询
8. {is_deleted, status} (复合索引) - 有效商品查询
9. slug (唯一索引) - URL 友好标识
```

**验收标准**:
- [ ] 索引创建脚本完成
- [ ] 索引策略合理
- [ ] 支持全文搜索
- [ ] 可重复执行（幂等性）

---

### Day 3: 集成与测试 (预计 2-3 小时)

#### ✅ 任务 5.1: 注册路由
**文件**: `app/main.py`

```python
from app.api.v1 import products

app.include_router(products.router, prefix="/api/v1", tags=["Products"])
```

#### ✅ 任务 5.2: 创建测试文件
**文件**: `tests/test_phase3_products.py`

**测试场景**:
- [ ] 测试创建商品（管理员）
- [ ] 测试创建商品（普通用户，应该失败）
- [ ] 测试获取商品列表
- [ ] 测试获取单个商品
- [ ] 测试更新商品
- [ ] 测试删除商品（软删除）
- [ ] 测试商品搜索
- [ ] 测试商品筛选
- [ ] 测试分页功能
- [ ] 测试库存不足场景

#### ✅ 任务 5.3: 手动测试
- [ ] 使用 Swagger UI 测试所有端点
- [ ] 测试权限控制
- [ ] 测试搜索功能
- [ ] 测试分页功能
- [ ] 测试性能（响应时间 < 200ms）

---

## 📊 数据模型设计

### MongoDB Collection: `products`

```javascript
{
  _id: ObjectId,                    // MongoDB 自动生成
  name: String,                     // 商品名称 *
  description: String,              // 商品描述
  price: Decimal128,                // 商品价格 *
  stock: Number,                    // 库存数量 *
  category: String,                 // 商品分类 *
  tags: [String],                   // 标签数组
  images: [String],                 // 图片 URL 数组
  
  // 可选属性（不同商品有不同属性）
  attributes: {
    color: String,
    size: String,
    brand: String,
    weight: String,
    // ... 其他属性
  },
  
  // 商品状态
  status: String,                   // "active", "inactive", "out_of_stock" *
  slug: String,                     // URL 友好标识（唯一）
  
  // 统计数据
  views: Number,                    // 浏览次数
  sales_count: Number,              // 销售数量
  rating: Number,                   // 平均评分
  
  // 元数据
  is_deleted: Boolean,              // 软删除标记 *
  created_at: ISODate,              // 创建时间 *
  updated_at: ISODate,              // 更新时间 *
  created_by: ObjectId,             // 创建者 ID
  updated_by: ObjectId              // 最后更新者 ID
}
```

**注**: `*` 标记为必需字段

---

## 🔑 关键技术点

### 1. 商品搜索实现

```python
# 文本搜索（使用 MongoDB 文本索引）
{
    "$text": {
        "$search": "MacBook Pro M3"
    }
}

# 正则表达式搜索（备选方案）
{
    "$or": [
        {"name": {"$regex": keyword, "$options": "i"}},
        {"description": {"$regex": keyword, "$options": "i"}},
        {"tags": {"$regex": keyword, "$options": "i"}}
    ]
}
```

### 2. 价格区间筛选

```python
filter_dict = {}
if min_price:
    filter_dict["price"] = {"$gte": min_price}
if max_price:
    if "price" in filter_dict:
        filter_dict["price"]["$lte"] = max_price
    else:
        filter_dict["price"] = {"$lte": max_price}
```

### 3. 分页查询

```python
skip = (page - 1) * page_size
products = await db.products.find(filter_dict)\
    .skip(skip)\
    .limit(page_size)\
    .sort(sort_field, sort_direction)\
    .to_list(length=page_size)

total = await db.products.count_documents(filter_dict)
```

### 4. 软删除

```python
# 删除商品（标记为已删除）
await db.products.update_one(
    {"_id": ObjectId(product_id)},
    {
        "$set": {
            "is_deleted": True,
            "updated_at": datetime.utcnow()
        }
    }
)

# 查询时排除已删除商品
filter_dict = {"is_deleted": False}
```

---

## 🛡️ 权限控制

### 访问规则

| 操作 | 普通用户 | 店家 (vendor) | 管理员 (admin) |
|------|----------|---------------|----------------|
| 查看商品列表 | ✅ | ✅ | ✅ |
| 查看商品详情 | ✅ | ✅ | ✅ |
| 搜索商品 | ✅ | ✅ | ✅ |
| 创建商品 | ❌ | ✅ | ✅ |
| 更新商品 | ❌ | ✅（自己的） | ✅（所有） |
| 删除商品 | ❌ | ✅（自己的） | ✅（所有） |

### 实现方式

```python
from app.utils.dependencies import (
    get_current_active_user,
    require_vendor_or_admin
)

# 只读端点：所有人可访问（可选认证）
@router.get("/products")
async def list_products():
    pass

# 写操作端点：需要 vendor 或 admin 权限
@router.post("/products")
async def create_product(
    current_user: UserInDB = Depends(require_vendor_or_admin())
):
    pass
```

---

## 🧪 验收标准

### 功能验收
- [ ] 管理员可以新增、编辑、删除商品
- [ ] 店家可以管理自己的商品
- [ ] 所有用户可以浏览商品列表
- [ ] 商品搜索功能正常（支持名称、描述、标签）
- [ ] 商品筛选功能正常（分类、价格区间、状态）
- [ ] 分页查询功能正常
- [ ] 软删除功能正常（不影响数据完整性）

### 性能验收
- [ ] 商品列表查询响应时间 < 200ms
- [ ] 商品搜索响应时间 < 300ms
- [ ] 单个商品查询响应时间 < 100ms

### 代码质量
- [ ] 所有代码通过 Linter 检查
- [ ] 使用自定义异常（不使用 HTTPException）
- [ ] 日志记录完整
- [ ] 错误处理完善
- [ ] API 文档完整（Swagger UI）

### 测试覆盖
- [ ] 单元测试覆盖核心服务层
- [ ] 集成测试覆盖所有 API 端点
- [ ] 权限测试完整

---

## 📝 开发注意事项

### 1. 数据类型
```python
# ⚠️ MongoDB 的 Decimal128 需要特殊处理
from bson import Decimal128

# 存储
price_decimal = Decimal128(str(price))

# 读取
price_float = float(product_data["price"].to_decimal())
```

### 2. ObjectId 处理
```python
from bson import ObjectId

# 验证
if not ObjectId.is_valid(product_id):
    raise ValidationException(message="Invalid product ID format")

# 转换
product_data["_id"] = ObjectId(product_id)
product_data["id"] = str(product_data.pop("_id"))
```

### 3. 软删除
```python
# 始终在查询中排除已删除的商品
filter_dict = {"is_deleted": False}

# 或者在 Service 层统一处理
async def get_active_products_filter(self):
    return {"is_deleted": False, "status": {"$ne": "inactive"}}
```

### 4. 库存管理
```python
# 检查库存
if product.stock < quantity:
    raise ValidationException(
        message="Insufficient stock",
        details={"available": product.stock, "requested": quantity}
    )

# 扣减库存（后续在订单模块实现事务）
await db.products.update_one(
    {"_id": ObjectId(product_id)},
    {"$inc": {"stock": -quantity}}
)
```

---

## 🐛 常见问题与解决方案

### 问题 1: 价格精度问题
**现象**: 使用 float 导致计算误差  
**解决**: 使用 Decimal128 或 Decimal

### 问题 2: 搜索性能慢
**现象**: 文本搜索响应时间过长  
**解决**: 创建文本索引，使用 `$text` 操作符

### 问题 3: 分页查询不准确
**现象**: 总数计算错误  
**解决**: 使用 `count_documents()` 配合相同的 filter

### 问题 4: 图片 URL 验证
**现象**: 无效的图片 URL  
**解决**: 使用 Pydantic 的 HttpUrl 类型

---

## 📚 相关文档

- [开发路线图](../06-api-design/ecommerce_development_roadmap.md)
- [数据模型设计](../06-api-design/ecommerce_data_model_design.md)
- [API 文档](../06-api-design/ecommerce_api_documentation.md)
- [异常处理指南](./EXCEPTION_USAGE_GUIDE.md)
- [依赖注入说明](./DEPENDENCIES_REFACTORING_SUMMARY.md)

---

## 🎯 下一步（PHASE 4）

完成 PHASE 3 后，将进入 PHASE 4：订单管理

**PHASE 4 主要内容**:
- 订单创建（含事务处理）
- 库存自动扣减
- 订单状态管理
- 订单历史查询

---

**开发状态**: 🚀 准备开始  
**预计完成时间**: 3-5 天  
**最后更新**: 2025-11-11

