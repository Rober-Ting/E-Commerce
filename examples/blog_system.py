
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

