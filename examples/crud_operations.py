
from pymongo import MongoClient
from bson.objectid import ObjectId

# 連線到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']  # 建立或切換到 mydatabase 資料庫
my_collection = db['mycollection'] # 建立或切換到 mycollection 集合

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

