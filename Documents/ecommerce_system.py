
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

