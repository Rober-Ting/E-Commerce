# 💻 MongoDB 示例代码

本目录包含 MongoDB 各种操作和场景的示例代码。

---

## 📁 文件列表

### [crud_operations.py](crud_operations.py) - CRUD 操作示例

**内容：**
- ✅ Create (创建) 操作
- ✅ Read (读取) 操作
- ✅ Update (更新) 操作
- ✅ Delete (删除) 操作

**学习重点：**
- `insert_one()`, `insert_many()` 的使用
- `find()`, `find_one()` 查询方法
- `update_one()`, `update_many()` 更新技巧
- `delete_one()`, `delete_many()` 删除操作
- 错误处理和异常捕获

**运行方式：**
```powershell
python examples/crud_operations.py
```

---

### [aggregation_pipeline.py](aggregation_pipeline.py) - 聚合管道示例

**内容：**
- ✅ `$match` - 数据过滤
- ✅ `$group` - 数据分组
- ✅ `$project` - 字段投影
- ✅ `$sort` - 排序
- ✅ `$limit` - 限制结果数量
- ✅ 复杂聚合查询示例

**学习重点：**
- 聚合管道的概念
- 各个聚合阶段的作用
- 如何组合多个聚合操作
- 数据分析和统计

**运行方式：**
```powershell
python examples/aggregation_pipeline.py
```

---

### [blog_system.py](blog_system.py) - 博客系统数据模型

**内容：**
- ✅ 用户（Users）集合设计
- ✅ 文章（Posts）集合设计
- ✅ 评论（Comments）集合设计
- ✅ 一对多关系处理
- ✅ 嵌入式文档 vs 引用

**学习重点：**
- 如何设计博客系统的数据模型
- 文章和评论的关系处理
- 用户和文章的关联
- 标签和分类的实现
- 查询优化策略

**应用场景：**
- 博客网站
- 新闻网站
- 论坛系统
- 内容管理系统（CMS）

**运行方式：**
```powershell
python examples/blog_system.py
```

---

### [ecommerce_system.py](ecommerce_system.py) - 电商系统数据模型

**内容：**
- ✅ 用户（Users）集合
- ✅ 商品（Products）集合
- ✅ 订单（Orders）集合
- ✅ 购物车（Cart）设计
- ✅ 商品分类和标签
- ✅ 订单状态管理

**学习重点：**
- 电商系统的数据模型设计
- 用户、商品、订单的关系
- 库存管理
- 订单状态流转
- 价格计算
- 索引优化

**应用场景：**
- 电商平台
- 订单管理系统
- 库存管理系统
- 本项目的实际应用！

**运行方式：**
```powershell
python examples/ecommerce_system.py
```

---

## 🚀 快速开始

### 前置条件

1. **MongoDB 运行中**
   ```powershell
   # 检查 MongoDB 是否运行
   mongo --eval "db.version()"
   ```

2. **Python 环境准备**
   ```powershell
   # 激活虚拟环境
   .\venv\Scripts\activate
   
   # 确保已安装 pymongo
   pip install pymongo
   ```

### 运行示例

```powershell
# 1. 从基础开始 - CRUD 操作
python examples/crud_operations.py

# 2. 进阶 - 聚合查询
python examples/aggregation_pipeline.py

# 3. 实战 - 博客系统
python examples/blog_system.py

# 4. 项目实践 - 电商系统
python examples/ecommerce_system.py
```

---

## 📚 学习路径

### 路径 1：从零开始学习 MongoDB

```
Step 1: crud_operations.py
   ↓ 学习基本的增删改查
   
Step 2: aggregation_pipeline.py
   ↓ 掌握数据分析和聚合
   
Step 3: blog_system.py
   ↓ 理解数据建模（简单场景）
   
Step 4: ecommerce_system.py
   ↓ 掌握复杂业务场景的建模
```

### 路径 2：针对电商项目学习

```
Step 1: ecommerce_system.py
   ↓ 直接了解项目的数据模型
   
Step 2: crud_operations.py
   ↓ 学习如何操作这些数据
   
Step 3: aggregation_pipeline.py
   ↓ 学习如何分析订单数据
```

---

## 💡 如何使用这些示例

### 方式 1：直接运行

```powershell
python examples/crud_operations.py
```

**优点：** 快速看到效果

**适合：** 快速了解功能

---

### 方式 2：阅读代码

打开文件，仔细阅读每一行代码和注释。

**优点：** 深入理解原理

**适合：** 想要深入学习

---

### 方式 3：修改实验

复制代码到新文件，尝试修改和实验。

```powershell
# 创建你的实验文件
copy examples\crud_operations.py my_experiment.py

# 修改并运行
python my_experiment.py
```

**优点：** 主动学习，印象深刻

**适合：** 想要深入掌握

---

### 方式 4：应用到项目

将示例代码的概念应用到实际项目中。

**优点：** 学以致用

**适合：** 开发实际功能

---

## 🎯 每个文件的学习目标

### crud_operations.py
**完成后你将能够：**
- ✅ 向 MongoDB 插入数据
- ✅ 查询和过滤数据
- ✅ 更新现有数据
- ✅ 删除不需要的数据
- ✅ 处理常见的错误

### aggregation_pipeline.py
**完成后你将能够：**
- ✅ 使用聚合管道分析数据
- ✅ 执行复杂的数据统计
- ✅ 生成报表数据
- ✅ 优化查询性能

### blog_system.py
**完成后你将能够：**
- ✅ 设计博客系统的数据模型
- ✅ 处理一对多关系
- ✅ 实现评论功能
- ✅ 设计标签系统

### ecommerce_system.py
**完成后你将能够：**
- ✅ 设计电商系统的完整数据模型
- ✅ 处理用户、商品、订单的关系
- ✅ 实现购物车功能
- ✅ 管理订单状态

---

## 📖 相关文档

- **MongoDB 学习指南**: [../docs/07-mongodb-learning/](../docs/07-mongodb-learning/)
- **数据模型设计**: [../docs/06-api-design/ecommerce_data_model_design.md](../docs/06-api-design/ecommerce_data_model_design.md)
- **API 文档**: [../docs/06-api-design/ecommerce_api_documentation.md](../docs/06-api-design/ecommerce_api_documentation.md)

---

## 🔧 故障排除

### 问题 1：ModuleNotFoundError: No module named 'pymongo'

**解决方案：**
```powershell
.\venv\Scripts\activate
pip install pymongo
```

### 问题 2：无法连接到 MongoDB

**解决方案：**
```powershell
# 检查 MongoDB 是否运行
mongo --eval "db.version()"

# 启动 MongoDB
net start MongoDB
```

### 问题 3：数据库已存在冲突

**解决方案：**
每个示例使用不同的数据库名称，不会互相干扰。如果需要清理：
```python
# 在 Python 中
client.drop_database('example_blog')
```

---

## ⚠️ 注意事项

1. **这些是示例代码**
   - 用于学习和演示
   - 不要直接用于生产环境
   - 缺少完整的错误处理和安全检查

2. **数据库名称**
   - 每个示例使用独立的数据库
   - 不会影响你的生产数据
   - 可以安全地运行和实验

3. **依赖关系**
   - 需要 MongoDB 运行
   - 需要 pymongo 库
   - 建议在虚拟环境中运行

---

## 🎓 进阶练习

完成这些示例后，尝试以下练习：

### 练习 1：扩展 CRUD 操作
- 添加批量更新功能
- 实现分页查询
- 添加事务处理

### 练习 2：复杂聚合
- 计算每月销售统计
- 分析用户行为
- 生成销售报表

### 练习 3：优化数据模型
- 为博客系统添加点赞功能
- 为电商系统添加优惠券
- 实现商品推荐算法

### 练习 4：整合到项目
- 将示例代码整合到 `app/` 中
- 添加 FastAPI 端点
- 编写测试用例

---

## 📊 示例代码统计

| 文件 | 行数 | 难度 | 预计学习时间 |
|------|------|------|--------------|
| crud_operations.py | ~100 | ⭐⭐ 入门 | 30 分钟 |
| aggregation_pipeline.py | ~80 | ⭐⭐⭐ 进阶 | 45 分钟 |
| blog_system.py | ~120 | ⭐⭐⭐ 进阶 | 1 小时 |
| ecommerce_system.py | ~150 | ⭐⭐⭐⭐ 高级 | 1.5 小时 |

---

**Happy Learning & Coding!** 💻✨

有问题可以参考 [故障排除文档](../docs/05-troubleshooting/) 或提出 Issue。

