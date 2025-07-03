from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client, Client
from passlib.context import CryptContext
import os

from template_engine import templates

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
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    profile_pic: UploadFile = File(None)
):
    hashed_pw = hash_password(password)
    profile_pic_url = None

    if profile_pic and profile_pic.filename:
        os.makedirs("static/profile_pics", exist_ok=True)
        file_location = f"static/profile_pics/{email}_{profile_pic.filename}"
        with open(file_location, "wb") as f:
            f.write(await profile_pic.read())
        profile_pic_url = f"/static/profile_pics/{email}_{profile_pic.filename}"

    try:
        result = supabase.table("users").insert({
            "email": email,
            "password": hashed_pw,
            "profile_pic": profile_pic_url
        }).execute()
        if result.data:
            return RedirectResponse("/", status_code=303)
        else:
            return templates.TemplateResponse("signup.html", {"request": request, "error": "Sign up failed. Email may already exist."})
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": f"Sign up failed: {e}"})

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    result = supabase.table("users").select("*").eq("email", email).single().execute()
    user = result.data
    if user and verify_password(password, user["password"]):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("user_email", email)
        return response
    # If user is None or password is wrong, show error
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})

@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_email")
    return response