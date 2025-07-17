from fastapi import FastAPI, UploadFile, File, Form, Request, Cookie
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from template_engine import templates
from starlette.requests import Request
import shutil, os, traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from file_parser import extract_text_from_file
from Huggingface_client import solve_with_openai
from mongodb_auth import router as auth_router, get_user_profile, update_user_profile_pic

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router)


MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "homeally")
openai_api_key = os.getenv('OPENAI_API_KEY')

print("✅ Using MongoDB authentication system")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request, user_email: str = Cookie(default=None)):
    if not user_email:
        return RedirectResponse("/login")
    
    # Get user profile from MongoDB
    user = get_user_profile(user_email)
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@app.post("/upload/")
async def handle_upload(request: Request, file: UploadFile = File(None), question_text: str = Form(""), user_email: str = Cookie(default=None)):
    if not user_email:
        return RedirectResponse("/login")
    try:
        question = ""

        if file and file.filename:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            question = extract_text_from_file(temp_path)
            os.remove(temp_path)

        elif question_text.strip():
            question = question_text.strip()

        else:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Please upload a file or type a question."
            })

        solution = solve_with_openai(question, openai_api_key)  # Pass the OpenAI API key

        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": question,
            "solution": solution
        })

    except Exception:
        print("⚠️ INTERNAL SERVER ERROR:")
        traceback.print_exc()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "An unexpected error occurred. Check your backend logs."
        })


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.png")


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user_email: str = Cookie(default=None)):
    """Display user profile page"""
    if not user_email:
        return RedirectResponse("/login")
    
    # Get user profile from MongoDB
    user = get_user_profile(user_email)
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )


@app.post("/profile/upload")
async def upload_profile_picture(
    request: Request,
    profile_pic: UploadFile = File(...),
    user_email: str = Cookie(default=None)
):
    """Handle profile picture upload"""
    if not user_email:
        return RedirectResponse("/login")
    
    try:
        # Validate file type
        if not profile_pic.content_type.startswith('image/'):
            user = get_user_profile(user_email)
            return templates.TemplateResponse(
                "profile.html",
                {"request": request, "user": user, "error": "Please upload a valid image file."}
            )
        
        # Create profile_pics directory if it doesn't exist
        profile_pics_dir = "static/profile_pics"
        try:
            os.makedirs(profile_pics_dir, exist_ok=True)
            
            # Save file with user's email as filename
            file_extension = profile_pic.filename.split('.')[-1] if '.' in profile_pic.filename else 'jpg'
            safe_email = user_email.replace('@', '_').replace('.', '_')
            filename = f"{safe_email}.{file_extension}"
            file_path = os.path.join(profile_pics_dir, filename)
            
            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_pic.file, buffer)
            
            # Update user profile in database
            profile_pic_url = f"/static/profile_pics/{filename}"
            update_user_profile_pic(user_email, profile_pic_url)
            
            # Get updated user profile
            user = get_user_profile(user_email)
            
            return templates.TemplateResponse(
                "profile.html",
                {"request": request, "user": user, "success": "Profile picture updated successfully!"}
            )
            
        except (OSError, PermissionError) as file_error:
            # In serverless environments like Vercel, file operations may fail
            user = get_user_profile(user_email)
            return templates.TemplateResponse(
                "profile.html",
                {"request": request, "user": user, "error": "Profile picture upload not supported in this environment. Please use local development."}
            )
        
    except Exception as e:
        print(f"Error uploading profile picture: {e}")
        user = get_user_profile(user_email)
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user": user, "error": "Failed to upload profile picture. Please try again."}
        )