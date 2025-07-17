"""
Local authentication bypass for development when Supabase is not available
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from template_engine import templates

router = APIRouter()

# Simple in-memory storage for development
local_users = {
    "test@example.com": {
        "password": "password123",
        "profile_pic": None
    },
    "demo@test.com": {
        "password": "demo123", 
        "profile_pic": None
    }
}

@router.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {
            "request": request, 
            "error": "Passwords do not match."
        })
    
    if email in local_users:
        return templates.TemplateResponse("signup.html", {
            "request": request, 
            "error": "Email already exists."
        })
    
    # Add user to local storage
    local_users[email] = {
        "password": password,
        "profile_pic": None
    }
    
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("user_email", email)
    return response

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = local_users.get(email)
        if user and user["password"] == password:
            response = RedirectResponse("/", status_code=303)
            response.set_cookie("user_email", email)
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request, 
                "error": "Invalid email or password."
            })
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Login failed. Please try again."
        })

@router.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("user_email")
    return response
