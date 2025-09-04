# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from db import create_user, verify_user, SECURITY_QUESTIONS, find_user_by_username
# import bcrypt

# app = FastAPI()

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allow all origins for dev
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------------
# # Request Models
# # ------------------------
# class SignupRequest(BaseModel):
#     username: str
#     email: str
#     password: str
#     securityQuestion: int
#     securityAnswer: str

# class LoginRequest(BaseModel):
#     username: str
#     password: str

# class SecurityAnswerRequest(BaseModel):
#     username: str
#     securityAnswer: str

# # ------------------------
# # Routes
# # ------------------------
# @app.post("/signup")
# def signup(data: SignupRequest):
#     # Hash the password before saving
#     hashed_pw = bcrypt.hashpw(
#         data.password.strip().encode("utf-8"),
#         bcrypt.gensalt()
#     ).decode("utf-8")

#     result = create_user(
#         data.username.strip(),
#         data.email.strip(),
#         hashed_pw,
#         data.securityQuestion,
#         data.securityAnswer.strip()
#     )

#     if not result["success"]:
#         raise HTTPException(status_code=400, detail=result["message"])
#     return {"message": result["message"]}


# @app.post("/login")
# def login(data: LoginRequest):
#     if verify_user(data.username.strip(), data.password.strip()):
#         return {"message": "Login successful"}
#     else:
#         raise HTTPException(status_code=401, detail="Invalid username or password")


# @app.get("/get-security-question/{username}")
# def get_security_question(username: str):
#     user = find_user_by_username(username)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"securityQuestion": SECURITY_QUESTIONS.get(user["security_question_id"])}


# @app.post("/verify-security")
# def verify_security(data: SecurityAnswerRequest):
#     user = find_user_by_username(data.username.strip())
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user["security_answer"] == data.securityAnswer.strip().lower():
#         return {"message": "Security verification successful"}
#     else:
#         raise HTTPException(status_code=401, detail="Incorrect security answer")


# @app.get("/security-questions")
# def get_questions():
#     return {"questions": SECURITY_QUESTIONS}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import create_user, verify_user, SECURITY_QUESTIONS, find_user_by_username
import bcrypt

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Request Models
# ------------------------
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    securityQuestion: int
    securityAnswer: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SecurityAnswerRequest(BaseModel):
    username: str
    securityAnswer: str

# ------------------------
# Routes (FIXED)
# ------------------------
# @app.post("/signup")
# def signup(data: SignupRequest):
#     # Hash the password before saving
#     hashed_pw = bcrypt.hashpw(
#         data.password.strip().encode("utf-8"),
#         bcrypt.gensalt()
#     ).decode("utf-8")
    
#     # Store security answer in lowercase for consistent comparison
#     result = create_user(
#         data.username.strip(),
#         data.email.strip(),
#         hashed_pw,
#         data.securityQuestion,
#         data.securityAnswer.strip().lower()  # Store in lowercase
#     )
    
#     if not result["success"]:
#         raise HTTPException(status_code=400, detail=result["message"])
#     return {"message": result["message"]}

@app.post("/login")
def login(data: LoginRequest):
    username = data.username.strip()
    password = data.password.strip()
    
    # Check if user exists first
    user = find_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Username not found")
    
    # Verify password
    if verify_user(username, password):
        return {"message": "Login successful"}
    else:
        # User exists but wrong password - return 401 to trigger security question
        raise HTTPException(status_code=401, detail="Incorrect password")

@app.get("/get-security-question/{username}")
def get_security_question(username: str):
    user = find_user_by_username(username.strip())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the question text from SECURITY_QUESTIONS dictionary
    question_text = SECURITY_QUESTIONS.get(user["security_question_id"])
    if not question_text:
        raise HTTPException(status_code=500, detail="Security question not found")
    
    return {"securityQuestion": question_text}

@app.post("/verify-security")
def verify_security(data: SecurityAnswerRequest):
    user = find_user_by_username(data.username.strip())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Compare answers in lowercase for consistency
    user_answer = user["security_answer"].lower()
    provided_answer = data.securityAnswer.strip().lower()
    
    print(f"DEBUG: Stored answer: '{user_answer}', Provided answer: '{provided_answer}'")  # Debug line
    
    if user_answer == provided_answer:
        return {"message": "Security verification successful"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect security answer")

@app.get("/security-questions")
def get_questions():
    return {"questions": SECURITY_QUESTIONS}


# In main.py

@app.post("/signup")
def signup(data: SignupRequest):
    # --- THIS IS THE FIX ---
    # DO NOT HASH THE PASSWORD HERE. Pass the plain text password to the db layer.
    # The create_user function is already responsible for hashing.
    
    # Store security answer in lowercase for consistent comparison
    result = create_user(
        data.username.strip(),
        data.email.strip(),
        data.password.strip(),  # Pass the plain password
        data.securityQuestion,
        data.securityAnswer.strip().lower()
    )
    # --- END FIX ---
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}