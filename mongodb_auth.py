"""
MongoDB Authentication System for Home Ally
"""
from fastapi import APIRouter, Form, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime
import os
import shutil
from bson import ObjectId

from template_engine import templates

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "homeally")

# Initialize MongoDB client with fallback
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client[DATABASE_NAME]
    users_collection = db.users
    print("✅ MongoDB connected successfully")
    
    # Create index on email for better performance
    users_collection.create_index("email", unique=True)
    print("✅ Database indexes created")
    
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("🔄 Falling back to file-based storage")
    client = None
    db = None
    users_collection = None
    
    # Import file-based fallback
    from simple_db import file_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(email: str, password: str, profile_pic: str = None):
    """Create a new user in MongoDB or fallback storage"""
    if users_collection is not None:
        # Use MongoDB
        try:
            # Check if user already exists
            if users_collection.find_one({"email": email}):
                return None
            
            user_data = {
                "email": email,
                "password": hash_password(password),
                "profile_pic": profile_pic,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = users_collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"MongoDB create_user error: {e}")
            return None
    else:
        # Use file-based fallback
        return file_db.create_user(email, password, profile_pic)

def get_user_by_email(email: str):
    """Get user by email from MongoDB or fallback storage"""
    if users_collection is not None:
        # Use MongoDB
        try:
            return users_collection.find_one({"email": email})
        except Exception as e:
            print(f"MongoDB get_user error: {e}")
            return None
    else:
        # Use file-based fallback
        return file_db.get_user_by_email(email)

def update_user_profile_pic(email: str, profile_pic_path: str):
    """Update user's profile picture in MongoDB or fallback storage"""
    if users_collection is not None:
        # Use MongoDB
        try:
            result = users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "profile_pic": profile_pic_path,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"MongoDB update_user error: {e}")
            return False
    else:
        # Use file-based fallback
        return file_db.update_user_profile_pic(email, profile_pic_path)

@router.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(None),
    profile_pic: UploadFile = File(None)
):
    try:
        # Validate passwords match (if confirm_password is provided)
        if confirm_password and password != confirm_password:
            return templates.TemplateResponse("signup.html", {
                "request": request, 
                "error": "Passwords do not match."
            })
        
        # If confirm_password is not provided, skip validation (for backward compatibility)
        if not confirm_password:
            confirm_password = password  # Set it to password for processing
        
        # Handle profile picture upload
        profile_pic_path = None
        if profile_pic and profile_pic.filename:
            # Create profile pics directory if it doesn't exist
            os.makedirs("static/profile_pics", exist_ok=True)
            
            # Save profile picture
            profile_pic_path = f"static/profile_pics/{email}_{profile_pic.filename}"
            with open(profile_pic_path, "wb") as buffer:
                shutil.copyfileobj(profile_pic.file, buffer)
            
            # Store relative path for web access
            profile_pic_path = f"/static/profile_pics/{email}_{profile_pic.filename}"
        
        # Create user
        user_id = create_user(email, password, profile_pic_path)
        
        if user_id:
            response = RedirectResponse("/", status_code=303)
            response.set_cookie("user_email", email)
            return response
        else:
            return templates.TemplateResponse("signup.html", {
                "request": request, 
                "error": "Sign up failed. Email may already exist."
            })
            
    except Exception as e:
        print(f"Signup error: {e}")
        return templates.TemplateResponse("signup.html", {
            "request": request, 
            "error": f"Sign up failed: {str(e)}"
        })

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = get_user_by_email(email)
        
        if user:
            # For MongoDB, use our verify_password function
            # For file_db, use the file_db's verify_password method
            if users_collection is not None:
                password_valid = verify_password(password, user["password"])
            else:
                password_valid = file_db.verify_password(password, user["password"])
            
            if password_valid:
                response = RedirectResponse("/", status_code=303)
                response.set_cookie("user_email", email)
                return response
        
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid email or password."
        })
            
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Login failed. Please check your connection and try again."
        })

@router.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("user_email")
    return response

# Helper function to get user profile
def get_user_profile(email: str):
    """Get user profile for display purposes"""
    user = get_user_by_email(email)
    if user:
        return {
            "email": user["email"],
            "profile_pic": user.get("profile_pic"),
            "created_at": user.get("created_at")
        }
    return None
