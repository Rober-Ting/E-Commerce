# 📚 文档组织指南

## 📁 文档目录结构

```
docs/
├── 01-getting-started/      # 快速开始和设置指南
├── 02-development/          # 开发相关文档
├── 03-testing/              # 测试指南
├── 04-debugging/            # 调试指南
├── 05-troubleshooting/      # 故障排查
├── 06-api-design/           # API 设计和架构
└── 07-mongodb-learning/     # MongoDB 学习资源
```

---

## 📋 文档分类规则

### 📂 01-getting-started/ - 快速开始

**用途：** 帮助新用户快速启动项目

**包含文档：**
- ✅ `HOW_TO_RUN.md` - 如何运行项目
- ✅ `QUICK_START.md` - 快速开始指南
- ✅ `QUICK_START_FRONTEND.md` - 前端快速启动
- ✅ `FRONTEND_SETUP.md` - 前端详细设置

**适合放置：**
- 环境配置指南
- 首次运行教程
- 依赖安装说明
- 端口配置说明
- CORS 设置说明

---

### 📂 02-development/ - 开发文档

**用途：** 开发过程中的技术文档和进度记录

**包含文档：**
- ✅ `DAY1_SUMMARY.md` - 第一天开发总结
- ✅ `DAY2-3_COMPLETE.md` - 第2-3天完成报告
- ✅ `DAY4-5_COMPLETE.md` - 第4-5天完成报告
- ✅ `PHASE1_PROGRESS.md` - Phase 1 进度
- ✅ `PHASE2_PROGRESS.md` - Phase 2 进度
- ✅ `PHASE2_COMPLETE.md` - Phase 2 完成报告
- ✅ `ERROR_HANDLING_EXPLAINED.md` - 错误处理机制详解
- ✅ `EXCEPTION_USAGE_GUIDE.md` - 异常使用指南
- ✅ `TEST_CORS_GUIDE.md` - CORS 测试指南
- ✅ `DAY2-3_LEARNING_GUIDE.md` - 学习指南

**适合放置：**
- 开发进度报告
- 阶段完成总结
- 技术实现详解
- 代码架构说明
- 最佳实践指南
- 错误处理机制
- 认证授权实现
- 数据模型设计

---

### 📂 03-testing/ - 测试文档

**用途：** 所有测试相关的指南和文档

**包含文档：**
- ✅ `PYTEST_GUIDE.md` - Pytest 使用指南
- ✅ `TESTING_QUICK_START.md` - 测试快速开始
- ✅ `COVERAGE_GUIDE.md` - 代码覆盖率指南
- ✅ `COVERAGE_QUICK_START.md` - 覆盖率快速开始
- ✅ `API_TESTING_GUIDE.md` - API 测试指南

**适合放置：**
- 单元测试指南
- 集成测试指南
- API 测试教程
- 测试工具使用
- 代码覆盖率报告
- 测试最佳实践
- Mock 和 Fixture 使用
- 性能测试指南

---

### 📂 04-debugging/ - 调试文档

**用途：** 调试工具和技巧

**包含文档：**
- ✅ `DEBUG_GUIDE.md` - 调试总指南
- ✅ `DEBUG_QUICK_START.md` - 调试快速开始
- ✅ `DEBUG_LOGIN_GUIDE.md` - 登入功能调试指南
- ✅ `VSCODE_DEBUG_GUIDE.md` - VS Code 调试指南
- ✅ `DEBUG_COMPARISON.md` - 调试方法对比
- ✅ `🎉_DEBUG_MODE_READY.md` - 调试模式就绪

**适合放置：**
- VS Code 调试配置
- 断点使用技巧
- 日志调试方法
- pdb 使用指南
- 特定功能调试教程
- 调试工具对比
- 远程调试指南

---

### 📂 05-troubleshooting/ - 故障排查

**用途：** 常见问题和解决方案

**包含文档：**
- ✅ `TROUBLESHOOTING.md` - 通用故障排查
- ✅ `PHASE2_TROUBLESHOOTING.md` - Phase 2 疑难排解
- ✅ `❌_FIX_MODULE_ERROR.md` - 模块错误修复

**适合放置：**
- 常见错误和解决方案
- 环境问题排查
- 依赖冲突解决
- 数据库连接问题
- CORS 问题解决
- 部署问题排查
- 性能问题诊断

---

### 📂 06-api-design/ - API 设计

**用途：** API 架构和设计文档

**包含文档：**
- ✅ `ecommerce_api_documentation.md` - API 文档
- ✅ `ecommerce_data_model_design.md` - 数据模型设计
- ✅ `ecommerce_development_roadmap.md` - 开发路线图
- ✅ `ecommerce_project_requirements.md` - 项目需求
- ✅ `ecommerce_technical_architecture.md` - 技术架构
- ✅ `PROJECT_SUMMARY.md` - 项目总结
- ✅ `QUICK_REFERENCE.md` - 快速参考
- ✅ `README.md` - API 设计说明

**适合放置：**
- API 端点文档
- 数据模型设计
- 系统架构图
- 技术选型说明
- 项目需求文档
- 开发路线图
- 接口规范

---

### 📂 07-mongodb-learning/ - MongoDB 学习

**用途：** MongoDB 相关学习资源

**包含文档：**
- ✅ `mongodb_learning_guide.md` - MongoDB 学习指南
- ✅ `mongodb_learning_guide_outline.md` - 学习大纲
- ✅ `README.md` - 学习资源说明

**适合放置：**
- MongoDB 基础教程
- 聚合管道示例
- 索引优化指南
- 查询技巧
- 复制集配置
- 备份恢复方案
- 性能优化

---

## 🎯 文档命名规范

### 通用规范
- ✅ 使用 `UPPER_CASE` 或 `PascalCase`
- ✅ 使用下划线 `_` 连接单词
- ✅ 使用 `.md` 扩展名
- ✅ 文件名要描述性强

### 特殊前缀
- `QUICK_START_` - 快速开始类文档
- `DEBUG_` - 调试类文档
- `PHASE*_` - 阶段性文档
- `DAY*_` - 每日总结
- `TEST_` - 测试相关

### 示例
```
✅ GOOD:
- API_TESTING_GUIDE.md
- DEBUG_LOGIN_GUIDE.md
- PHASE2_PROGRESS.md
- ERROR_HANDLING_EXPLAINED.md

❌ BAD:
- guide.md
- test.md
- doc1.md
- untitled.md
```

---

## 📝 创建新文档时的检查清单

### 步骤 1: 确定文档类型
- [ ] 是快速开始指南吗？ → `01-getting-started/`
- [ ] 是开发过程文档吗？ → `02-development/`
- [ ] 是测试相关文档吗？ → `03-testing/`
- [ ] 是调试指南吗？ → `04-debugging/`
- [ ] 是故障排查吗？ → `05-troubleshooting/`
- [ ] 是 API 设计文档吗？ → `06-api-design/`
- [ ] 是 MongoDB 学习资源吗？ → `07-mongodb-learning/`

### 步骤 2: 选择合适的文件名
```markdown
# 格式：
[类型]_[主题]_[详细说明].md

# 示例：
DEBUG_LOGIN_GUIDE.md
API_TESTING_GUIDE.md
PHASE2_PROGRESS.md
ERROR_HANDLING_EXPLAINED.md
```

### 步骤 3: 添加文档头部
```markdown
# 📚 [文档标题]

> 简短描述文档用途

## 📌 关键信息
- **目标读者**: [开发者/测试者/新手]
- **前置条件**: [需要了解的内容]
- **相关文档**: [链接到相关文档]

---

## 📖 目录
[如果文档较长，添加目录]

---

## 内容...
```

### 步骤 4: 更新索引文档
在对应目录的 `README.md` 中添加新文档的链接。

---

## 🔄 文档移动命令

### PowerShell 命令
```powershell
# 移动文档到对应目录
Move-Item -Path "DOCUMENT_NAME.md" -Destination "docs\[目录]\DOCUMENT_NAME.md" -Force

# 示例：
Move-Item -Path "DEBUG_LOGIN_GUIDE.md" -Destination "docs\04-debugging\DEBUG_LOGIN_GUIDE.md" -Force
Move-Item -Path "API_TESTING_GUIDE.md" -Destination "docs\03-testing\API_TESTING_GUIDE.md" -Force
```

### Bash 命令（Linux/Mac）
```bash
# 移动文档到对应目录
mv DOCUMENT_NAME.md docs/[目录]/DOCUMENT_NAME.md

# 示例：
mv DEBUG_LOGIN_GUIDE.md docs/04-debugging/DEBUG_LOGIN_GUIDE.md
mv API_TESTING_GUIDE.md docs/03-testing/API_TESTING_GUIDE.md
```

---

## 📊 当前文档统计

### 01-getting-started/ (4 个文档)
- HOW_TO_RUN.md
- QUICK_START.md
- QUICK_START_FRONTEND.md
- FRONTEND_SETUP.md

### 02-development/ (10 个文档)
- DAY1_SUMMARY.md
- DAY2-3_COMPLETE.md
- DAY2-3_LEARNING_GUIDE.md
- DAY4-5_COMPLETE.md
- PHASE1_PROGRESS.md
- PHASE2_PROGRESS.md
- PHASE2_COMPLETE.md
- ERROR_HANDLING_EXPLAINED.md
- EXCEPTION_USAGE_GUIDE.md
- TEST_CORS_GUIDE.md

### 03-testing/ (5 个文档)
- PYTEST_GUIDE.md
- TESTING_QUICK_START.md
- COVERAGE_GUIDE.md
- COVERAGE_QUICK_START.md
- API_TESTING_GUIDE.md

### 04-debugging/ (6 个文档)
- DEBUG_GUIDE.md
- DEBUG_QUICK_START.md
- DEBUG_LOGIN_GUIDE.md
- VSCODE_DEBUG_GUIDE.md
- DEBUG_COMPARISON.md
- 🎉_DEBUG_MODE_READY.md

### 05-troubleshooting/ (3 个文档)
- TROUBLESHOOTING.md
- PHASE2_TROUBLESHOOTING.md
- ❌_FIX_MODULE_ERROR.md

### 06-api-design/ (8 个文档)
- ecommerce_api_documentation.md
- ecommerce_data_model_design.md
- ecommerce_development_roadmap.md
- ecommerce_project_requirements.md
- ecommerce_technical_architecture.md
- PROJECT_SUMMARY.md
- QUICK_REFERENCE.md
- README.md

### 07-mongodb-learning/ (3 个文档)
- mongodb_learning_guide.md
- mongodb_learning_guide_outline.md
- README.md

**总计: 39 个文档**

---

## 💡 最佳实践

### 1. 保持文档更新
- ✅ 代码更改时，同步更新相关文档
- ✅ 定期审查文档的准确性
- ✅ 添加最后更新日期

### 2. 使用清晰的标题
```markdown
✅ GOOD:
# 🐛 登入功能调试完整指南

❌ BAD:
# 调试
```

### 3. 提供代码示例
```markdown
✅ GOOD:
```python
# 示例代码
def example():
    return "示例"
```

❌ BAD:
（只有文字描述，没有代码）
```

### 4. 添加目录和导航
```markdown
## 📖 目录
- [快速开始](#快速开始)
- [详细说明](#详细说明)
- [常见问题](#常见问题)

[返回顶部](#)
```

### 5. 使用 Emoji 增强可读性
```markdown
✅ 成功
❌ 错误
⚠️ 警告
💡 提示
📚 文档
🔧 配置
🐛 调试
```

---

## 🔗 相关资源

- [Markdown 语法指南](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [文档写作最佳实践](https://www.writethedocs.org/guide/)

---

## 📝 文档审查清单

在提交文档前检查：

- [ ] 文档放在正确的目录下
- [ ] 文件名符合命名规范
- [ ] 包含清晰的标题和描述
- [ ] 有目录（如果文档较长）
- [ ] 代码示例可以正常运行
- [ ] 链接都是有效的
- [ ] 格式一致（标题层级、代码块、列表）
- [ ] 添加了必要的 Emoji 标记
- [ ] 包含最后更新日期
- [ ] 相关文档已更新索引

---

**最后更新**: 2025-11-11  
**维护者**: AI Assistant + Robert

**注意**: 此指南会随项目发展持续更新。

