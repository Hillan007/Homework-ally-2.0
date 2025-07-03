# Home-ally 2.0

# Homework Ally Assistant

**Homework Ally** is a friendly AI-powered web assistant designed to help students with their homework questions. It allows users to either upload a file (PDF, Word, or Text) containing their question or simply type their question directly. The assistant then uses advanced AI to provide helpful answers, making learning fun and interactive—especially for kids!

---

## ✨ Features

- **Ask by File or Text:** Upload your homework file or type your question.
- **AI-Powered Answers:** Uses OpenAI's GPT models to generate clear, helpful responses.
- **User Accounts:** Sign up, log in, and log out securely.
- **Profile Pictures:** Upload a profile picture during sign-up for a personalized experience.
- **Kid-Friendly Interface:** Colorful, playful, and easy to use for all ages.

---

## 🟢 Live Demo

Try Homework Ally live:  
👉 [https://homework-ally-2-0.vercel.app/](https://homework-ally-2-0.vercel.app/)

---

## 🛠️ Tools & Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/):** High-performance Python web framework for the backend.
- **[Jinja2](https://jinja.palletsprojects.com/):** For dynamic HTML templating.
- **[OpenAI API](https://platform.openai.com/):** For generating AI-powered answers.
- **[Supabase](https://supabase.com/):** PostgreSQL-based backend for user authentication and data storage.
- **[Passlib](https://passlib.readthedocs.io/):** For secure password hashing.
- **[Uvicorn](https://www.uvicorn.org/):** Lightning-fast ASGI server for running FastAPI.
- **HTML/CSS:** Custom, colorful, and responsive user interface.
- **File Uploads:** Supports PDF, DOC, DOCX, and TXT files.

---

## 🚀 Getting Started

1. **Clone the repository** and install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. **Set up your `.env` file** with your API keys and Supabase credentials:
    ```
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    OPENAI_API_KEY=your_openai_key
    ```

3. **Run the app:**
    ```
    uvicorn main:app --reload
    ```

4. **Open your browser** and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 👦👧 Who is it for?

- Students of all ages who want quick, friendly homework help.
- Parents and teachers looking for a safe, easy-to-use AI assistant for kids.

---

## 📦 Folder Structure

```
Home-ally/
├── main.py
├── auth.py
├── openai_client.py
├── file_parser.py
├── supabase.py
├── templates/
│   ├── index.html
│   ├── signup.html
│   └── login.html
├── static/
│   ├── styles.css
│   └── mascot.png
├── .env
└── Readme.txt
```

---

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/)
- [Supabase](https://supabase.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Homework Ally** makes homework less stressful and more fun. Happy learning!
