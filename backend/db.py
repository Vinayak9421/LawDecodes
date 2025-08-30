import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

print("MONGO_URI:", MONGO_URI)   # Debug check
print("DB_NAME:", DB_NAME)       # Debug check

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
print("✅ Connected to MongoDB:", client.list_database_names())

db = client[DB_NAME]

# Collections
users = db["User_info"]
pdfs = db["Uploaded_pdf"]
chats = db["Chat_history"]

def insert_test_data():
    user_doc = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "hashed_password_here",
        "created_at": datetime.utcnow()
    }
    user_id = users.insert_one(user_doc).inserted_id

    pdf_doc = {
        "user_id": str(user_id),
        "filename": "sample.pdf",
        "file_path": "/uploads/sample.pdf",
        "uploaded_at": datetime.utcnow()
    }
    pdf_id = pdfs.insert_one(pdf_doc).inserted_id

    chat_doc = {
        "user_id": str(user_id),
        "pdf_id": str(pdf_id),
        "question": "What is inside this PDF?",
        "answer": "This is just a test entry.",
        "timestamp": datetime.utcnow()
    }
    chat_id = chats.insert_one(chat_doc).inserted_id

    print("✅ Test data inserted successfully!")
    print(f"User ID: {user_id}")
    print(f"PDF ID: {pdf_id}")
    print(f"Chat ID: {chat_id}")

if __name__ == "__main__":
    insert_test_data()
