# MongoDB 學習指南 (針對 MySQL 使用者)

## 前言

您好！很高興能協助您從 MySQL 的背景知識出發，系統性地學習 MongoDB。本指南旨在透過對比您熟悉的關聯式資料庫概念，幫助您快速掌握 MongoDB 的核心特性與應用。我們將從基礎概念、操作實務到進階應用，並提供豐富的程式實作範例，讓您能快速上手。

## 第一部分：概念對比與基礎入門 (從 MySQL 到 MongoDB)

### 1.1 什麼是 NoSQL？為什麼選擇 MongoDB？
*   **MySQL (RDBMS) 簡述**: 表格、行、列、Schema、ACID
*   **MongoDB (NoSQL Document Database) 簡述**: 文件、集合、BSON、彈性 Schema、CAP 定理 (BASE)
*   **優勢與適用場景**: 彈性、擴展性、效能、適用於非結構化/半結構化資料、大數據、即時應用等

### 1.2 核心概念對比

| MySQL 概念 | MongoDB 概念 | 說明 |
| :--------- | :----------- | :--- |
| Database   | Database     | 邏輯上的資料容器，與 MySQL 概念相似 |
| Table      | Collection   | 文件的集合，類似於 MySQL 的表格，但無固定 Schema |
| Row        | Document     | BSON 格式的資料，類似於 MySQL 的行，但可包含巢狀結構 |
| Column     | Field        | 文件中的鍵值對，類似於 MySQL 的列 |
| Primary Key| `_id` Field  | 每個 Document 唯一的識別符，MongoDB 自動生成或可自定義 |
| Index      | Index        | 提高查詢效率，概念與 MySQL 相似，但有更多類型 (如 Text, Geospatial) |
| Join       | Embedded Documents / Referencing | MongoDB 鼓勵內嵌文件 (Embedded Documents) 或手動引用 (Referencing) 來處理關聯 |
| Schema     | Dynamic Schema / Schema Validation | 彈性 Schema，文件結構可變；可選用 Schema Validation 進行約束 |

### 1.3 MongoDB 安裝與設定 (本地環境)
*   **安裝步驟**: 適用於 Windows/macOS/Linux
*   **啟動與停止服務**: `mongod` 命令
*   **連線工具**: `mongosh` (MongoDB Shell) 基礎使用

## 第二部分：基本操作與 CRUD (增、查、改、刪)

### 2.1 資料庫與集合操作
*   **建立/切換資料庫**: `use <database_name>`
*   **顯示資料庫**: `show dbs`
*   **建立集合**: `db.createCollection()` (通常不需顯式建立)
*   **顯示集合**: `show collections`
*   **刪除資料庫**: `db.dropDatabase()`
*   **刪除集合**: `db.<collection_name>.drop()`

### 2.2 文件操作 (CRUD)
*   **新增文件 (Create)**
    *   `insertOne()`: 插入單一文件
    *   `insertMany()`: 插入多個文件
*   **查詢文件 (Read)**
    *   `find()`: 查詢所有文件或符合條件的文件
    *   `findOne()`: 查詢符合條件的第一個文件
    *   **查詢條件 (Query Operators)**: `$eq`, `$gt`, `$lt`, `$gte`, `$lte`, `$ne`, `$in`, `$nin`, `$and`, `$or`, `$not`, `$nor`, `$exists`, `$type`, `$regex` 等
    *   **投影 (Projection)**: 選擇返回的欄位
    *   **排序 (Sort)**: `sort()`
    *   **限制 (Limit)**: `limit()`
    *   **跳過 (Skip)**: `skip()`
*   **更新文件 (Update)**
    *   `updateOne()`: 更新單一文件
    *   `updateMany()`: 更新多個文件
    *   `replaceOne()`: 替換單一文件
    *   **更新操作符 (Update Operators)**: `$set`, `$unset`, `$inc`, `$push`, `$pull`, `$addToSet` 等
*   **刪除文件 (Delete)**
    *   `deleteOne()`: 刪除單一文件
    *   `deleteMany()`: 刪除多個文件

### 2.3 索引 (Indexes)
*   **建立索引**: `createIndex()`
*   **查看索引**: `getIndexes()`
*   **刪除索引**: `dropIndex()`, `dropIndexes()`
*   **索引類型**: 單一欄位索引、複合索引、文字索引、地理空間索引

## 第三部分：進階概念與應用

### 3.1 聚合管道 (Aggregation Pipeline)
*   **概念**: 類似於 SQL 的 GROUP BY、JOIN、WHERE 等操作的組合
*   **常用階段 (Stages)**: `$match`, `$project`, `$group`, `$sort`, `$limit`, `$skip`, `$unwind`, `$lookup` (模擬 JOIN)
*   **實作範例**: 複雜資料統計與轉換

### 3.2 資料模型設計 (Data Modeling)
*   **內嵌 (Embedded Documents) vs. 引用 (Referencing)**
    *   優缺點與適用場景
    *   一對一、一對多、多對多關係的建模策略
*   **Schema Validation**:  enforcing data structure

### 3.3 事務 (Transactions)
*   **概念**: MongoDB 4.0+ 支援多文件事務
*   **應用場景**: 確保多文件操作的原子性
*   **實作範例**: 銀行轉帳情境

### 3.4 複製集 (Replica Sets) 與分片 (Sharding)
*   **複製集**: 高可用性與資料冗餘
*   **分片**: 水平擴展與處理大數據集

## 第四部分：程式實作 (Python 範例)

### 4.1 環境準備
*   **安裝 PyMongo**: `pip install pymongo`
*   **連線 MongoDB**: `MongoClient`

### 4.2 CRUD 操作實作
*   **新增**: `insert_one()`, `insert_many()`
*   **查詢**: `find()`, `find_one()` (搭配查詢條件、投影、排序、限制)
*   **更新**: `update_one()`, `update_many()`, `replace_one()`
*   **刪除**: `delete_one()`, `delete_many()`

### 4.3 聚合管道實作
*   使用 `aggregate()` 方法

### 4.4 實作題目

#### 題目一：電商訂單管理系統
*   **情境**: 模擬一個電商平台，包含用戶、商品和訂單。
*   **MongoDB 建模**: 設計用戶、商品、訂單的 Collection 結構，考慮內嵌與引用。
*   **實作功能**:
    1.  新增用戶、商品。
    2.  用戶下訂單 (包含多個商品，考慮庫存更新)。
    3.  查詢某用戶的所有訂單。
    4.  查詢某商品的所有銷售記錄。
    5.  統計每月銷售總額。
    6.  找出購買次數最多的前N名用戶。

#### 題目二：部落格系統
*   **情境**: 模擬一個部落格平台，包含文章、評論和標籤。
*   **MongoDB 建模**: 設計文章、評論的 Collection 結構，考慮文章與評論之間的關係。
*   **實作功能**:
    1.  新增文章 (包含標題、內容、作者、標籤列表、發布日期)。
    2.  為指定文章新增評論 (包含評論者、內容、評論日期)。
    3.  查詢某作者的所有文章。
    4.  查詢包含特定標籤的所有文章。
    5.  統計每篇文章的評論數量。
    6.  更新文章內容。
    7.  刪除文章及其所有相關評論。

## 結語

本指南提供了一個全面的學習路徑，從概念對比到實作練習，希望能幫助您快速掌握 MongoDB。在實作過程中，請多嘗試、多思考，並參考官方文件以獲得更深入的理解。祝您學習愉快！

