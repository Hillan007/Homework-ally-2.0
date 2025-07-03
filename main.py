from fastapi import FastAPI, UploadFile, File, Form, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import shutil, os, traceback

from file_parser import extract_text_from_file
from Huggingface_client import solve_with_openai  # <-- update this import
from auth import router as auth_router
from supabase import create_client

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request, user_email: str = Cookie(default=None)):
    user = None
    if user_email:
        result = supabase.table("users").select("profile_pic").eq("email", user_email).single().execute()
        user = result.data if result.data else None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@app.post("/upload/")
async def handle_upload(request: Request, file: UploadFile = File(None), question_text: str = Form("")):
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

        solution = solve_with_openai(question)  # <-- update this line

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