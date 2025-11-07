# MongoDB 學習指南 (針對 MySQL 使用者)

## 前言

您好！很高興能協助您從 MySQL 的背景知識出發，系統性地學習 MongoDB。本指南旨在透過對比您熟悉的關聯式資料庫概念，幫助您快速掌握 MongoDB 的核心特性與應用。我們將從基礎概念、操作實務到進階應用，並提供豐富的程式實作範例，讓您能快速上手。

## 第一部分：概念對比與基礎入門 (從 MySQL 到 MongoDB)

### 1.1 什麼是 NoSQL？為什麼選擇 MongoDB？

在深入了解 MongoDB 之前，讓我們先回顧您所熟悉的 **MySQL**，它是一個典型的 **關聯式資料庫管理系統 (RDBMS)**。RDBMS 的核心特點是資料以表格（Table）的形式組織，每個表格由固定的行（Row）和列（Column）組成，並透過主鍵（Primary Key）和外鍵（Foreign Key）建立資料之間的關聯。這種嚴謹的結構確保了資料的完整性（Integrity）和一致性（Consistency），並遵循 ACID（原子性、一致性、隔離性、持久性）原則，非常適合處理結構化資料和需要複雜事務的應用場景。

然而，隨著網際網路應用和巨量資料（Big Data）的興起，傳統 RDBMS 在處理非結構化或半結構化資料、高併發讀寫、以及需要極致水平擴展的場景時，逐漸顯露出其局限性。為了解決這些問題，**NoSQL（Not only SQL）資料庫**應運而生。NoSQL 資料庫提供了一種更為彈性的資料儲存方式，不再嚴格遵循關聯模型，而是根據不同的資料模型（如文件、鍵值、列族、圖形）來設計，以滿足特定應用場景的需求。

**MongoDB** 便是 NoSQL 資料庫家族中的一員，它是一種領先的**文件導向資料庫 (Document Database)**。MongoDB 將資料儲存為 BSON（Binary JSON）格式的文件，這些文件被組織在集合（Collection）中。與 MySQL 嚴格的 Schema 不同，MongoDB 採用**彈性 Schema**（或稱為 Schema-less），這意味著同一集合中的文件可以擁有不同的欄位結構，極大地提高了開發的靈活性和迭代速度。MongoDB 在設計上更傾向於 BASE（基本可用性、軟狀態、最終一致性）原則，這使其在處理大規模分散式系統和需要高可用性的場景下表現出色 [1]。

選擇 MongoDB 的主要優勢包括：

*   **彈性 (Flexibility)**：彈性 Schema 允許資料結構隨應用需求變化，無需預先定義複雜的表格結構。
*   **擴展性 (Scalability)**：MongoDB 支援水平擴展（Sharding），可以輕鬆地將資料分散到多個伺服器上，以處理不斷增長的資料量和流量。
*   **效能 (Performance)**：對於大量讀寫操作和複雜的查詢，MongoDB 通常能提供優異的效能，特別是當資料模型設計得當時。
*   **適用場景 (Use Cases)**：非常適合處理非結構化/半結構化資料、大數據、即時分析、內容管理系統、行動應用後端等。

### 1.2 核心概念對比

為了幫助您更好地理解 MongoDB 的核心概念，以下表格將其與您熟悉的 MySQL 概念進行對比：

| MySQL 概念 | MongoDB 概念 | 說明 |
| :--------- | :----------- | :--- |
| Database   | Database     | 邏輯上的資料容器，與 MySQL 概念相似，用於組織集合 |
| Table      | Collection   | 文件的集合，類似於 MySQL 的表格，但無固定 Schema，可包含結構不同的文件 |
| Row        | Document     | BSON 格式的資料，類似於 MySQL 的行，但可包含巢狀結構（如陣列、子文件） |
| Column     | Field        | 文件中的鍵值對，類似於 MySQL 的列，但型別和數量可變 |
| Primary Key| `_id` Field  | 每個 Document 唯一的識別符，MongoDB 自動生成 ObjectId 或可自定義 |
| Index      | Index        | 提高查詢效率，概念與 MySQL 相似，但 MongoDB 提供更多類型（如 Text, Geospatial, Hashed） |
| Join       | Embedded Documents / Referencing | MongoDB 鼓勵透過**內嵌文件 (Embedded Documents)** 或**手動引用 (Referencing)** 來處理關聯，而非傳統的 JOIN 操作 |
| Schema     | Dynamic Schema / Schema Validation | 彈性 Schema，文件結構可變；可選用 Schema Validation 進行資料結構約束 |

### 1.3 MongoDB 安裝與設定 (本地環境)

在開始實作之前，我們需要先在您的本地環境中安裝 MongoDB 伺服器並設定連線工具。以下是基於 Ubuntu 系統的安裝步驟，其他作業系統可參考 MongoDB 官方文件 [2]：

1.  **導入 MongoDB 公鑰**：
    ```bash
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /etc/apt/keyrings/mongodb-server-7.0.gpg
    ```

2.  **添加 MongoDB APT 來源**：
    ```bash
    echo "deb [ arch=amd64,arm64 signed-by=/etc/apt/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    ```

3.  **更新 APT 軟體包列表並安裝 MongoDB**：
    ```bash
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    ```

4.  **啟動 MongoDB 服務**：
    ```bash
    sudo systemctl start mongod
    ```

5.  **檢查 MongoDB 服務狀態**：
    ```bash
    sudo systemctl status mongod
    ```
    如果服務正常運行，您將看到 `Active: active (running)` 的訊息。

6.  **連線工具 `mongosh`**：
    `mongosh` 是 MongoDB 的官方 Shell 工具，用於與 MongoDB 實例進行互動。安裝 `mongodb-org` 套件時會自動安裝 `mongosh`。您可以在終端機中直接輸入 `mongosh` 命令來連線到本地 MongoDB 伺服器：
    ```bash
    mongosh
    ```
    進入 `mongosh` 後，您可以執行基本的資料庫操作，例如 `show dbs` 查看所有資料庫。

## 第二部分：基本操作與 CRUD (增、查、改、刪)

### 2.1 資料庫與集合操作

在 MongoDB 中，資料庫（Database）是集合（Collection）的容器，而集合則是文件的容器。以下是常用的資料庫和集合操作：

*   **建立/切換資料庫**：在 `mongosh` 中，使用 `use <database_name>` 命令。如果指定的資料庫不存在，MongoDB 會在您第一次向其插入資料時自動建立它。
    ```javascript
    use mynewdatabase // 切換到 mynewdatabase，如果不存在則會建立
    ```
*   **顯示資料庫**：`show dbs` 命令會列出所有存在的資料庫。
    ```javascript
    show dbs
    ```
*   **建立集合**：通常情況下，當您第一次向一個不存在的集合插入文件時，MongoDB 會自動建立該集合。但您也可以使用 `db.createCollection()` 顯式建立，並可指定配置選項（如大小限制、驗證規則）。
    ```javascript
    db.createCollection("mycollection")
    ```
*   **顯示集合**：`show collections` 命令會列出當前資料庫中的所有集合。
    ```javascript
    show collections
    ```
*   **刪除資料庫**：`db.dropDatabase()` 會刪除當前所在的資料庫及其所有集合和文件。**請務必謹慎使用此命令。**
    ```javascript
    db.dropDatabase()
    ```
*   **刪除集合**：`db.<collection_name>.drop()` 會刪除指定的集合及其所有文件。
    ```javascript
    db.mycollection.drop()
    ```

### 2.2 文件操作 (CRUD)

MongoDB 的核心操作圍繞著文件的增（Create）、查（Read）、改（Update）、刪（Delete），即 CRUD 操作。我們將以 Python 的 PyMongo 驅動程式為例進行說明。請確保您已安裝 PyMongo (`pip install pymongo`)。

以下是 `crud_operations.py` 範例程式碼，展示了如何使用 PyMongo 執行基本的 CRUD 操作：

```python
from pymongo import MongoClient
from bson.objectid import ObjectId

# 連線到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # 建立或切換到 mydatabase 資料庫
my_collection = db["mycollection"] # 建立或切換到 mycollection 集合

print("--- MongoDB CRUD Operations Example ---")

# 1. 新增文件 (Create)
print("\n1. Inserting Documents:")
# insertOne
result_one = my_collection.insert_one({"name": "Alice", "age": 30, "city": "New York"})
print(f"Inserted one document with _id: {result_one.inserted_id}")

# insertMany
result_many = my_collection.insert_many([
    {"name": "Bob", "age": 24, "city": "London", "hobbies": ["reading", "sports"]},
    {"name": "Charlie", "age": 35, "city": "Paris", "hobbies": ["cooking", "travel"]},
    {"name": "David", "age": 29, "city": "New York", "hobbies": ["music"]}
])
print(f"Inserted multiple documents with _ids: {result_many.inserted_ids}")

# 2. 查詢文件 (Read)
print("\n2. Finding Documents:")
print("All documents:")
for doc in my_collection.find():
    print(doc)

print("\nDocuments with age > 25:")
for doc in my_collection.find({"age": {"$gt": 25}}):
    print(doc)

print("\nDocuments from New York, projecting only name and city:")
for doc in my_collection.find({"city": "New York"}, {"name": 1, "city": 1, "_id": 0}):
    print(doc)

print("\nDocuments sorted by age (descending) and limited to 2:")
for doc in my_collection.find().sort("age", -1).limit(2):
    print(doc)

# 3. 更新文件 (Update)
print("\n3. Updating Documents:")
# updateOne
update_result_one = my_collection.update_one(
    {"name": "Alice"},
    {"$set": {"age": 31, "status": "active"}}
)
print(f"Matched {update_result_one.matched_count} document(s) and modified {update_result_one.modified_count} document(s).")

# updateMany
update_result_many = my_collection.update_many(
    {"city": "New York"},
    {"$set": {"continent": "North America"}}
)
print(f"Matched {update_result_many.matched_count} document(s) and modified {update_result_many.modified_count} document(s).")

print("\nDocuments after update:")
for doc in my_collection.find():
    print(doc)

# Using update operators: $inc, $push
my_collection.update_one(
    {"name": "Bob"},
    {"$inc": {"age": 1}, "$push": {"hobbies": "photography"}}
)
print("\nBob's document after $inc and $push:")
print(my_collection.find_one({"name": "Bob"}))

# 4. 刪除文件 (Delete)
print("\n4. Deleting Documents:")
# deleteOne
delete_result_one = my_collection.delete_one({"name": "Charlie"})
print(f"Deleted {delete_result_one.deleted_count} document(s).")

# deleteMany
delete_result_many = my_collection.delete_many({"city": "London"})
print(f"Deleted {delete_result_many.deleted_count} document(s).")

print("\nDocuments after deletion:")
for doc in my_collection.find():
    print(doc)

# 清理：刪除集合
# my_collection.drop()
# print("\nCollection 'mycollection' dropped.")

# 清理：刪除資料庫 (慎用，會刪除整個資料庫)
# client.drop_database('mydatabase')
# print("\nDatabase 'mydatabase' dropped.")

client.close()
```

**1. 新增文件 (Create)**

*   `insert_one()`：用於向集合中插入單一文件。文件是一個字典（Python dict），MongoDB 會自動為其生成一個唯一的 `_id` 欄位，除非您手動指定。此操作會返回一個 `InsertOneResult` 物件，其中包含 `inserted_id` 屬性。
*   `insert_many()`：用於插入多個文件。它接受一個文件列表作為參數，並返回一個 `InsertManyResult` 物件，其中包含 `inserted_ids` 列表。

**2. 查詢文件 (Read)**

*   `find()`：這是最常用的查詢方法，用於查找集合中所有符合條件的文件。如果沒有傳遞任何參數，它將返回集合中的所有文件。`find()` 返回一個游標（Cursor）物件，您可以迭代它來獲取結果。
    *   **查詢條件 (Query Operators)**：MongoDB 提供豐富的查詢操作符，例如：
        *   `$eq`：等於（預設行為，無需顯式指定）
        *   `$gt`, `$lt`, `$gte`, `$lte`：大於、小於、大於等於、小於等於
        *   `$ne`：不等於
        *   `$in`, `$nin`：在指定值列表內、不在指定值列表內
        *   `$and`, `$or`, `$not`, `$nor`：邏輯操作符
        *   `$exists`：判斷欄位是否存在
        *   `$type`：按 BSON 類型查詢
        *   `$regex`：正則表達式查詢
    *   **投影 (Projection)**：透過在 `find()` 方法的第二個參數中指定欄位，您可以選擇只返回文件中的部分欄位，以減少網路傳輸量。`1` 表示包含該欄位，`0` 表示排除該欄位。`_id` 欄位預設包含，若要排除需顯式指定 `_id: 0`。
    *   **排序 (Sort)**：`sort()` 方法用於對查詢結果進行排序。它接受一個欄位名稱和排序方向（`1` 為升序，`-1` 為降序）。
    *   **限制 (Limit)**：`limit()` 方法用於限制返回文件的數量。
    *   **跳過 (Skip)**：`skip()` 方法用於跳過指定數量的文件，通常與 `sort()` 和 `limit()` 結合使用來實現分頁。
*   `find_one()`：用於查找集合中符合條件的第一個文件。如果找到，則返回一個字典；如果沒有找到，則返回 `None`。

**3. 更新文件 (Update)**

*   `update_one()`：更新集合中符合條件的第一個文件。它接受兩個主要參數：查詢條件和更新操作符。返回 `UpdateResult` 物件，包含 `matched_count` 和 `modified_count`。
*   `update_many()`：更新集合中所有符合條件的文件。用法與 `update_one()` 類似。
*   `replace_one()`：替換集合中符合條件的第一個文件。它會用新的文件完全替換舊文件，但保留 `_id`。請注意，替換操作不會自動保留舊文件的欄位，需要手動在新文件中包含所有必要的欄位。
*   **更新操作符 (Update Operators)**：MongoDB 提供多種更新操作符來精確修改文件內容：
    *   `$set`：設定欄位的值，如果欄位不存在則新增。
    *   `$unset`：刪除欄位。
    *   `$inc`：增加或減少數字欄位的值。
    *   `$push`：向陣列欄位追加元素。
    *   `$pull`：從陣列欄位中移除所有符合條件的元素。
    *   `$addToSet`：如果元素不在陣列中，則新增該元素。

**4. 刪除文件 (Delete)**

*   `delete_one()`：刪除集合中符合條件的第一個文件。返回 `DeleteResult` 物件，包含 `deleted_count`。
*   `delete_many()`：刪除集合中所有符合條件的文件。如果傳遞空查詢條件 `{}`，則會刪除集合中的所有文件。**請務必謹慎使用。**

### 2.3 索引 (Indexes)

索引在 MongoDB 中扮演著與 MySQL 類似的角色，它們可以顯著提高查詢效率。當您在一個或多個欄位上建立索引時，MongoDB 會為這些欄位創建一個特殊的資料結構，使得查詢可以更快地定位到目標文件，而無需掃描整個集合。以下是 PyMongo 中索引的常用操作：

*   **建立索引**：`create_index()` 方法用於在指定欄位上建立索引。您可以指定單一欄位或多個欄位（複合索引），並可選擇升序（`1`）或降序（`-1`）。
    ```python
    # 單一欄位索引
    my_collection.create_index("name")
    # 複合索引
    my_collection.create_index([("city", 1), ("age", -1)])
    # 唯一索引
    my_collection.create_index("email", unique=True)
    ```
*   **查看索引**：`list_indexes()` 方法會返回一個游標，迭代它可以查看集合中所有已建立的索引。
    ```python
    for index in my_collection.list_indexes():
        print(index)
    ```
*   **刪除索引**：`drop_index()` 方法用於刪除指定名稱的索引，`drop_indexes()` 則刪除集合中的所有索引（除了 `_id` 索引）。
    ```python
    my_collection.drop_index("name_1") # 索引名稱通常是欄位名和排序方向的組合
    # my_collection.drop_indexes()
    ```
*   **索引類型**：MongoDB 支援多種索引類型，以滿足不同的查詢需求，例如：
    *   **單一欄位索引 (Single Field Index)**：最基本的索引類型。
    *   **複合索引 (Compound Index)**：在多個欄位上建立的索引，查詢時會按照索引中欄位的順序進行匹配。
    *   **文字索引 (Text Index)**：支援對字串內容進行全文檢索。
    *   **地理空間索引 (Geospatial Index)**：支援地理位置相關的查詢，如查找附近的地點。
    *   **雜湊索引 (Hashed Index)**：對欄位的雜湊值進行索引，適用於分片鍵。

## 第三部分：進階概念與應用

### 3.1 聚合管道 (Aggregation Pipeline)

聚合管道是 MongoDB 中一個強大且靈活的資料處理框架，它允許您對集合中的文件執行一系列的資料轉換操作，以生成聚合結果。這類似於 SQL 中的 `GROUP BY`、`JOIN`（部分模擬）、`WHERE` 等操作的組合，但以管道（Pipeline）的形式串聯多個階段（Stage），每個階段的輸出作為下一個階段的輸入。這使得複雜的資料分析和報告生成變得高效且直觀。

以下是 `aggregation_pipeline.py` 範例程式碼，展示了如何使用 PyMongo 執行聚合管道：

```python
from pymongo import MongoClient

# 連線到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["sales_data"]
orders_collection = db["orders"]

print("--- MongoDB Aggregation Pipeline Example ---")

# 清理舊資料 (如果存在)
orders_collection.drop()

# 插入範例資料
orders_collection.insert_many([
    {"_id": 1, "item": "A", "price": 10, "quantity": 2, "date": "2025-01-10", "customer_id": 101},
    {"_id": 2, "item": "B", "price": 15, "quantity": 3, "date": "2025-01-10", "customer_id": 102},
    {"_id": 3, "item": "A", "price": 10, "quantity": 1, "date": "2025-01-11", "customer_id": 101},
    {"_id": 4, "item": "C", "price": 20, "quantity": 2, "date": "2025-01-11", "customer_id": 103},
    {"_id": 5, "item": "B", "price": 15, "quantity": 4, "date": "2025-02-12", "customer_id": 102},
    {"_id": 6, "item": "A", "price": 10, "quantity": 3, "date": "2025-02-12", "customer_id": 104},
    {"_id": 7, "item": "C", "price": 20, "quantity": 1, "date": "2025-02-13", "customer_id": 103},
    {"_id": 8, "item": "A", "price": 10, "quantity": 5, "date": "2025-03-15", "customer_id": 101}
])
print("Inserted sample order data.")

# 範例 1: 計算每個商品的總銷售數量和總收入
print("\n1. Total quantity and revenue per item:")
pipeline_1 = [
    {"$group": {"_id": "$item", "totalQuantity": {"$sum": "$quantity"}, "totalRevenue": {"$sum": {"$multiply": ["$price", "$quantity"]}}}},
    {"$sort": {"totalRevenue": -1}}
]
for doc in orders_collection.aggregate(pipeline_1):
    print(doc)

# 範例 2: 查詢 2025 年 2 月的訂單，並按客戶 ID 分組，計算每個客戶的總消費金額
print("\n2. Total spending per customer in February 2025:")
pipeline_2 = [
    {"$match": {"date": {"$regex": "^2025-02"}}},
    {"$group": {"_id": "$customer_id", "totalSpent": {"$sum": {"$multiply": ["$price", "$quantity"]}}}},
    {"$sort": {"totalSpent": -1}}
]
for doc in orders_collection.aggregate(pipeline_2):
    print(doc)

# 範例 3: 計算每月銷售總額
print("\n3. Monthly total revenue:")
pipeline_3 = [
    {"$project": {
        "month": {"$substr": ["$date", 5, 2]},
        "total": {"$multiply": ["$price", "$quantity"]}
    }},
    {"$group": {"_id": "$month", "monthlyRevenue": {"$sum": "$total"}}},
    {"$sort": {"_id": 1}}
]
for doc in orders_collection.aggregate(pipeline_3):
    print(doc)

client.close()
```

**常用階段 (Stages)**：

*   `$match`：用於過濾文件，只將符合條件的文件傳遞給下一個階段，類似於 SQL 的 `WHERE` 子句。
*   `$project`：用於選擇、重命名或新增欄位，以及計算新的欄位，類似於 SQL 的 `SELECT` 子句。
*   `$group`：用於將文件分組，並對每個組執行聚合操作（如 `$sum`, `$avg`, `$min`, `$max`），類似於 SQL 的 `GROUP BY` 子句。
*   `$sort`：用於對文件進行排序。
*   `$limit`：用於限制通過管道的文件數量。
*   `$skip`：用於跳過指定數量的文件。
*   `$unwind`：用於將陣列欄位中的每個元素解構成單獨的文件。
*   `$lookup`：用於執行左外連接（Left Outer Join），將來自另一個集合的文件合併到當前集合的文件中，這是 MongoDB 模擬關聯關係的一種方式。

### 3.2 資料模型設計 (Data Modeling)

資料模型設計是 MongoDB 應用開發中最關鍵的環節之一，它直接影響到資料庫的效能、可擴展性和查詢效率。與 MySQL 嚴格的關聯模型不同，MongoDB 提供了更大的彈性，主要透過兩種策略來處理資料關係：**內嵌文件 (Embedded Documents)** 和**引用 (Referencing)**。

*   **內嵌文件 (Embedded Documents)**：
    *   **概念**：將相關資料直接儲存在一個文件中，形成巢狀結構。例如，一個訂單文件可以直接包含其所有訂單項的詳細資訊。
    *   **優點**：單次查詢即可獲取所有相關資料，減少了資料庫查詢次數，提高了讀取效能。資料的原子性操作更簡單。
    *   **缺點**：如果內嵌文件過大或不斷增長，可能會影響效能；不適合多對多關係或需要頻繁更新內嵌資料的場景。
    *   **適用場景**：一對一或一對多關係，且「多」的部分不會無限增長，例如：用戶的地址資訊、訂單的商品列表。

*   **引用 (Referencing)**：
    *   **概念**：在一個文件中儲存另一個文件的 `_id`，類似於 MySQL 中的外鍵。當需要相關資料時，需要執行第二次查詢來獲取被引用的文件。
    *   **優點**：資料保持正規化，減少資料冗餘，適合多對多關係或被引用資料需要獨立管理和頻繁更新的場景。
    *   **缺點**：需要多次查詢才能獲取完整的相關資料，增加了應用程式的複雜性和資料庫的負擔。
    *   **適用場景**：一對多或多對多關係，且「多」的部分可能無限增長，例如：文章和評論、學生和課程。

**建模策略**：

*   **一對一關係**：通常使用內嵌，除非被關聯的資料非常大或需要獨立存取。
*   **一對多關係**：如果「多」的部分數量有限且不常單獨查詢，可考慮內嵌；如果數量可能無限增長或需要獨立存取，則使用引用。
*   **多對多關係**：通常使用引用，並在兩邊都儲存對方的 `_id` 陣列，或者建立一個中間集合來儲存關聯。

**Schema Validation**：
儘管 MongoDB 是彈性 Schema，但您仍然可以使用 **Schema Validation** 來強制執行資料結構的約束。這允許您為集合定義驗證規則，確保插入或更新的文件符合預期的 Schema。這在團隊開發或需要確保資料品質的場景中非常有用。

### 3.3 事務 (Transactions)

傳統的 RDBMS 以其對 ACID 事務的強大支援而聞名，確保了資料操作的原子性、一致性、隔離性和持久性。MongoDB 在早期版本中主要透過單文件原子性操作來處理事務。從 **MongoDB 4.0 版本開始，它引入了對多文件 ACID 事務的支援**，這使得在單一複製集內，以及從 MongoDB 4.2 開始在分片叢集內，可以執行跨多個文件和多個集合的原子性操作 [3]。

*   **概念**：事務允許將一系列操作視為一個單一的邏輯工作單元。要麼所有操作都成功提交，要麼所有操作都失敗回滾，確保資料的一致性。
*   **應用場景**：
    *   **銀行轉帳**：從一個帳戶扣款並向另一個帳戶存款，這兩個操作必須同時成功或同時失敗。
    *   **庫存管理**：更新商品庫存並記錄銷售訂單，確保庫存和訂單資料同步。
    *   **複雜的資料遷移**：需要一次性修改多個相關文件以保持資料一致性。

*   **實作範例**：以下是一個簡化的銀行轉帳情境，展示了如何使用 PyMongo 執行事務：
    ```python
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError

    client = MongoClient("mongodb://localhost:27017/")
    db = client["bank_db"]
    accounts = db["accounts"]

    # 清理並初始化帳戶
    accounts.drop()
    accounts.insert_many([
        {"_id": 1, "name": "Alice", "balance": 1000},
        {"_id": 2, "name": "Bob", "balance": 500}
    ])
    print("初始帳戶狀態:")
    for acc in accounts.find():
        print(acc)

    def transfer_funds(session, from_account_id, to_account_id, amount):
        # 扣款
        accounts.update_one(
            {"_id": from_account_id, "balance": {"$gte": amount}},
            {"$inc": {"balance": -amount}},
            session=session
        )
        # 檢查是否成功扣款
        if accounts.find_one({"_id": from_account_id}, session=session)["balance"] < 0:
            raise ValueError("餘額不足") # 模擬錯誤，觸發回滾

        # 存款
        accounts.update_one(
            {"_id": to_account_id},
            {"$inc": {"balance": amount}},
            session=session
        )

    # 執行事務
    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                transfer_funds(session, 1, 2, 200)
                session.commit_transaction()
                print("\n轉帳成功！")
            except Exception as e:
                session.abort_transaction()
                print(f"\n轉帳失敗，已回滾: {e}")
    except PyMongoError as e:
        print(f"MongoDB 事務錯誤: {e}")

    print("\n轉帳後帳戶狀態:")
    for acc in accounts.find():
        print(acc)

    client.close()
    ```

### 3.4 複製集 (Replica Sets) 與分片 (Sharding)

為了實現高可用性、資料冗餘和水平擴展，MongoDB 提供了複製集和分片兩種架構模式。

*   **複製集 (Replica Sets)**：
    *   **概念**：複製集是一組維護相同資料集的 MongoDB 伺服器。它包含一個主節點（Primary）和多個從節點（Secondary）。所有寫入操作都發送到主節點，然後資料會異步複製到所有從節點。從節點可以處理讀取操作，從而分擔主節點的讀取壓力，並提供資料冗餘。
    *   **優點**：
        *   **高可用性**：當主節點故障時，複製集會自動選舉一個新的主節點，確保服務不中斷。
        *   **資料冗餘**：資料儲存在多個節點上，防止單點故障導致資料丟失。
        *   **讀取擴展**：可以將讀取操作分散到從節點，提高讀取吞吐量。
    *   **適用場景**：任何需要高可用性和資料持久性的生產環境。

*   **分片 (Sharding)**：
    *   **概念**：分片是一種將資料分散到多個伺服器（分片）上的方法，以實現水平擴展。當資料量或讀寫負載超出單一伺服器或複製集的能力時，分片可以將資料集分割成更小的、更易於管理的塊，並將這些塊分佈到不同的分片上。每個分片本身通常是一個複製集。
    *   **優點**：
        *   **水平擴展**：可以處理非常龐大的資料集和高吞吐量的應用。
        *   **高容量**：允許儲存比單一伺服器更多的資料。
        *   **高併發**：將讀寫操作分散到多個伺服器，提高併發處理能力。
    *   **適用場景**：處理巨量資料和極高併發請求的應用，例如大型電商平台、社交媒體等。

## 第四部分：程式實作 (Python 範例)

本部分將提供兩個完整的實作題目，每個題目都包含情境描述、MongoDB 建模建議和具體的實作功能要求。您可以參考之前提供的 `crud_operations.py` 和 `aggregation_pipeline.py` 範例，並結合以下題目進行練習。

### 4.1 環境準備

在開始程式實作之前，請確保您的 Python 環境已準備就緒：

*   **安裝 PyMongo**：
    ```bash
    pip install pymongo
    ```
*   **連線 MongoDB**：使用 `pymongo.MongoClient` 類來建立與 MongoDB 伺服器的連線。預設情況下，MongoDB 運行在 `localhost:27017`。
    ```python
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    ```

### 4.2 CRUD 操作實作

請參考 `crud_operations.py` 範例，它詳細展示了 `insert_one()`, `insert_many()`, `find()`, `find_one()`, `update_one()`, `update_many()`, `delete_one()`, `delete_many()` 等方法的使用，以及查詢條件、投影、排序、限制等常用功能。

### 4.3 聚合管道實作

請參考 `aggregation_pipeline.py` 範例，它展示了如何使用 `aggregate()` 方法和 `$match`, `$group`, `$project`, `$sort` 等聚合管道階段來執行複雜的資料分析。

### 4.4 實作題目

#### 題目一：電商訂單管理系統

*   **情境**：模擬一個電商平台，包含用戶、商品和訂單。這是一個典型的應用場景，可以練習資料建模和多集合操作。
*   **MongoDB 建模**：
    *   **用戶 (Users)** 集合：儲存用戶基本資訊，如 `_id`, `name`, `email`。
    *   **商品 (Products)** 集合：儲存商品資訊，如 `_id`, `name`, `price`, `stock`。
    *   **訂單 (Orders)** 集合：儲存訂單資訊。考慮將訂單中的商品列表作為內嵌文件儲存（一對多關係，且商品列表相對穩定），包含 `user_id`（引用用戶）、`order_date`, `items` (內嵌商品 `product_id`, `product_name`, `quantity`, `price`), `total_amount`, `status`。
*   **實作功能**：
    1.  新增用戶、商品。
    2.  用戶下訂單 (包含多個商品，考慮庫存更新)。
    3.  查詢某用戶的所有訂單。
    4.  查詢某商品的所有銷售記錄。
    5.  統計每月銷售總額。
    6.  找出購買次數最多的前 5 名用戶。

以下是 `ecommerce_system.py` 範例程式碼，提供了上述功能的實作：

```python
from pymongo import MongoClient
from datetime import datetime

# 連線到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]

# 清理舊資料 (如果存在)
db.users.drop()
db.products.drop()
db.orders.drop()

print("--- 電商訂單管理系統實作範例 ---")

# 1. 新增用戶、商品
print("\n1. 新增用戶與商品:")
users = [
    {"_id": 1, "name": "Alice", "email": "alice@example.com"},
    {"_id": 2, "name": "Bob", "email": "bob@example.com"},
    {"_id": 3, "name": "Charlie", "email": "charlie@example.com"}
]
products = [
    {"_id": 101, "name": "Laptop", "price": 1200, "stock": 10},
    {"_id": 102, "name": "Mouse", "price": 25, "stock": 50},
    {"_id": 103, "name": "Keyboard", "price": 75, "stock": 20}
]
db.users.insert_many(users)
db.products.insert_many(products)
print("用戶與商品已新增。")

# 2. 用戶下訂單
print("\n2. 用戶下訂單:")
def place_order(user_id, items):
    order_items = []
    total_amount = 0
    for item in items:
        product = db.products.find_one({"_id": item["product_id"]})
        if not product or product["stock"] < item["quantity"]:
            print(f"商品 {item["product_id"]} 庫存不足或不存在。")
            return None
        
        order_items.append({
            "product_id": product["_id"],
            "product_name": product["name"],
            "quantity": item["quantity"],
            "price": product["price"]
        })
        total_amount += product["price"] * item["quantity"]
        
        # 更新庫存
        db.products.update_one({"_id": product["_id"]}, {"$inc": {"stock": -item["quantity"]}})

    order = {
        "user_id": user_id,
        "order_date": datetime.now(),
        "items": order_items,
        "total_amount": total_amount,
        "status": "completed"
    }
    result = db.orders.insert_one(order)
    print(f"用戶 {user_id} 訂單已建立，訂單 ID: {result.inserted_id}")
    return result.inserted_id

place_order(1, [{"product_id": 101, "quantity": 1}, {"product_id": 102, "quantity": 2}])
place_order(2, [{"product_id": 103, "quantity": 1}])
place_order(1, [{"product_id": 102, "quantity": 1}])
place_order(3, [{"product_id": 101, "quantity": 1}, {"product_id": 103, "quantity": 1}])

# 3. 查詢某用戶的所有訂單
print("\n3. 查詢用戶 1 的所有訂單:")
for order in db.orders.find({"user_id": 1}):
    print(order)

# 4. 查詢某商品的所有銷售記錄
print("\n4. 查詢商品 Laptop 的所有銷售記錄:")
for order in db.orders.find({"items.product_name": "Laptop"}):
    print(order)

# 5. 統計每月銷售總額
print("\n5. 統計每月銷售總額:")
pipeline_monthly_sales = [
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m", "date": "$order_date"}},
        "totalSales": {"$sum": "$total_amount"}
    }},
    {"$sort": {"_id": 1}}
]
for result in db.orders.aggregate(pipeline_monthly_sales):
    print(result)

# 6. 找出購買次數最多的前 5 名用戶 (這裡只有3個用戶，所以會顯示所有用戶)
print("\n6. 找出購買次數最多的前 5 名用戶:")
pipeline_top_customers = [
    {"$group": {"_id": "$user_id", "orderCount": {"$sum": 1}}},
    {"$sort": {"orderCount": -1}},
    {"$limit": 5},
    {"$lookup": {
        "from": "users",
        "localField": "_id",
        "foreignField": "_id",
        "as": "user_info"
    }},
    {"$unwind": "$user_info"},
    {"$project": {
        "_id": 0,
        "user_id": "$_id",
        "user_name": "$user_info.name",
        "orderCount": 1
    }}
]
for result in db.orders.aggregate(pipeline_top_customers):
    print(result)

client.close()
```

#### 題目二：部落格系統

*   **情境**：模擬一個部落格平台，包含文章、評論和標籤。這是一個練習一對多和多對多關係建模的良好機會。
*   **MongoDB 建模**：
    *   **文章 (Posts)** 集合：儲存文章資訊，如 `_id`, `title`, `content`, `author`, `tags` (陣列), `publish_date`, `comments_count` (用於儲存評論數量，避免每次查詢都計算)。
    *   **評論 (Comments)** 集合：儲存評論資訊，如 `_id`, `post_id` (引用文章), `commenter`, `content`, `comment_date`。
*   **實作功能**：
    1.  新增文章 (包含標題、內容、作者、標籤列表、發布日期)。
    2.  為指定文章新增評論 (包含評論者、內容、評論日期)。
    3.  查詢某作者的所有文章。
    4.  查詢包含特定標籤的所有文章。
    5.  統計每篇文章的評論數量。
    6.  更新文章內容。
    7.  刪除文章及其所有相關評論。

以下是 `blog_system.py` 範例程式碼，提供了上述功能的實作：

```python
from pymongo import MongoClient
from datetime import datetime

# 連線到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["blog_db"]

# 清理舊資料 (如果存在)
db.posts.drop()
db.comments.drop()

print("--- 部落格系統實作範例 ---")

# 1. 新增文章
print("\n1. 新增文章:")
def add_post(title, content, author, tags):
    post = {
        "title": title,
        "content": content,
        "author": author,
        "tags": tags,
        "publish_date": datetime.now(),
        "comments_count": 0 # 初始化評論計數
    }
    result = db.posts.insert_one(post)
    print(f"文章 <{title}> 已新增，ID: {result.inserted_id}")
    return result.inserted_id

post_id_1 = add_post("MongoDB 入門", "這是一篇關於 MongoDB 基礎的文章。", "Alice", ["MongoDB", "NoSQL", "Database"])
post_id_2 = add_post("Python 與 PyMongo", "介紹如何使用 Python 連接 MongoDB。", "Bob", ["Python", "PyMongo", "MongoDB"])
post_id_3 = add_post("資料庫設計模式", "探討 MongoDB 的資料模型設計。", "Alice", ["MongoDB", "Data Modeling"])

# 2. 為指定文章新增評論
print("\n2. 為文章新增評論:")
def add_comment(post_id, commenter, comment_content):
    comment = {
        "post_id": post_id,
        "commenter": commenter,
        "content": comment_content,
        "comment_date": datetime.now()
    }
    db.comments.insert_one(comment)
    # 更新文章的評論計數
    db.posts.update_one({"_id": post_id}, {"$inc": {"comments_count": 1}})
    print(f"文章 {post_id} 新增評論成功。")

add_comment(post_id_1, "Charlie", "很有用的文章！")
add_comment(post_id_1, "David", "學到了很多，謝謝！")
add_comment(post_id_2, "Charlie", "範例程式碼很清晰。")

# 3. 查詢某作者的所有文章
print("\n3. 查詢作者 Alice 的所有文章:")
for post in db.posts.find({"author": "Alice"}):
    print(post)

# 4. 查詢包含特定標籤的所有文章
print("\n4. 查詢包含標籤 'MongoDB' 的所有文章:")
for post in db.posts.find({"tags": "MongoDB"}):
    print(post)

# 5. 統計每篇文章的評論數量 (已在新增評論時更新 comments_count 欄位)
print("\n5. 每篇文章的評論數量:")
for post in db.posts.find({}, {"title": 1, "comments_count": 1, "_id": 0}):
    print(post)

# 6. 更新文章內容
print("\n6. 更新文章內容:")
db.posts.update_one(
    {"_id": post_id_1},
    {"$set": {"content": "這是一篇更新後的 MongoDB 基礎文章，增加了更多細節。"}}
)
print(f"文章 {post_id_1} 內容已更新。")
print(db.posts.find_one({"_id": post_id_1}))

# 7. 刪除文章及其所有相關評論
print("\n7. 刪除文章及其所有相關評論:")
def delete_post_and_comments(post_id):
    db.posts.delete_one({"_id": post_id})
    delete_result = db.comments.delete_many({"post_id": post_id})
    print(f"文章 {post_id} 已刪除，同時刪除了 {delete_result.deleted_count} 條相關評論。")

delete_post_and_comments(post_id_3)

print("\n刪除後剩餘的文章:")
for post in db.posts.find():
    print(post)

print("\n刪除後剩餘的評論:")
for comment in db.comments.find():
    print(comment)

client.close()
```

## 結語

本指南提供了一個全面的學習路徑，從概念對比到實作練習，希望能幫助您快速掌握 MongoDB。在實作過程中，請多嘗試、多思考，並參考官方文件以獲得更深入的理解。MongoDB 的彈性和強大功能將為您的應用開發帶來新的可能性。祝您學習愉快！

## 參考資料

[1] MongoDB. (n.d.). *What is MongoDB?*. Retrieved from https://www.mongodb.com/what-is-mongodb
[2] MongoDB. (n.d.). *Install MongoDB Community Edition*. Retrieved from https://www.mongodb.com/docs/manual/installation/
[3] MongoDB. (n.d.). *Transactions*. Retrieved from https://www.mongodb.com/docs/manual/core/transactions/
