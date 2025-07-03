from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client
from passlib.context import CryptContext
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return request.app.templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    profile_pic: UploadFile = File(None)
):
    hashed_pw = hash_password(password)
    profile_pic_url = None

    if profile_pic:
        # Save to static/profile_pics/ and generate URL
        os.makedirs("static/profile_pics", exist_ok=True)
        file_location = f"static/profile_pics/{email}_{profile_pic.filename}"
        with open(file_location, "wb") as f:
            f.write(await profile_pic.read())
        profile_pic_url = f"/static/profile_pics/{email}_{profile_pic.filename}"

    result = supabase.table("users").insert({
        "email": email,
        "password": hashed_pw,
        "profile_pic": profile_pic_url
    }).execute()
    if result.data:
        return RedirectResponse("/", status_code=303)
    return request.app.templates.TemplateResponse("signup.html", {"request": request, "error": "Sign up failed. Email may already exist."})

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return request.app.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = supabase.table("users").select("*").eq("email", email).single().execute()
    if user.data and verify_password(password, user.data["password"]):
        # For demo: set a session cookie or similar here
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("user_email", email)  # Not secure, just for demo!
        return response
    return request.app.templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})

@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_email")
    return response