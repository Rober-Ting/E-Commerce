
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

