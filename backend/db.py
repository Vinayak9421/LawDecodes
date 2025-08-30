import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]

# Security Questions (static mapping)
SECURITY_QUESTIONS = {
    1: "What is your favourite colour?",
    2: "In which city were you born?",
    3: "What was the name of your first pet?",
    4: "What is your mother's maiden name?",
    5: "What was your first car?"
}

def create_user(username, email, password, security_question_id, security_answer):
    """Insert new user into MongoDB with hashed password"""
    # Check duplicate username or email
    if users_col.find_one({"username": username}):
        return {"success": False, "message": "Username already exists"}
    if users_col.find_one({"email": email}):
        return {"success": False, "message": "Email already registered"}

    # Hash ONLY the password, keep security answer as plain text
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user_doc = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "security_question_id": security_question_id,
        "security_answer": security_answer.lower(),  # Store as plain text
        "created_at": datetime.now(timezone.utc)
    }

    users_col.insert_one(user_doc)
    return {"success": True, "message": "User created successfully"}



def find_user_by_username(username):
    """Find user by username with case-insensitive search"""
    user = users_col.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})
    return user

def verify_user(username, password):
    """Verify user login using bcrypt with debugging"""
    user = find_user_by_username(username)
    if not user:
        print(f"DEBUG: User '{username}' not found")
        return False
    
    stored_password = user["password"]
    print(f"DEBUG: Password type: {type(stored_password)}")
    
    try:
        # Handle different password storage formats
        if isinstance(stored_password, bytes):
            stored_hash = stored_password
        elif isinstance(stored_password, str):
            stored_hash = stored_password.encode('utf-8')
        else:
            # Handle MongoDB Binary type
            stored_hash = bytes(stored_password)
        
        result = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        print(f"DEBUG: Password verification result: {result}")
        return result
        
    except Exception as e:
        print(f"DEBUG: Password verification failed with error: {e}")
        return False



def verify_security_answer(username, answer):
    """Verify user's security question answer (plain text comparison)"""
    user = find_user_by_username(username)
    if not user:
        return False

    stored_answer = user.get('security_answer', '').lower()
    provided_answer = answer.lower()
    print(f"DEBUG: Comparing security answers - Stored: '{stored_answer}', Provided: '{provided_answer}'")
    
    return stored_answer == provided_answer
