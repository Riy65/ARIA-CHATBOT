from fastapi import FastAPI
from routes import chat
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router


app = FastAPI(
    title="Aria Chatbot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aria-chatbot-git-openai-version-riy65s-projects.vercel.app","http://127.0.0.1:5500",
        "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(chat.router, prefix="/chat")

@app.get("/")
def root():
    return {"message": "Chatbot backend running"}


