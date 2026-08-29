from fastapi import FastAPI
from routes import chat
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.profile import router as profile_router
from routes.portfolio import router as portfolio_router
from database import Base, engine
from models import chat as chat_models
from models import user as user_models
from models import profile as profile_models
from models import portfolio as portfolio_models


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
app.include_router(profile_router, prefix="/profile", tags=["Profile"])
app.include_router(portfolio_router, prefix="/portfolios", tags=["Portfolios"])


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Chatbot backend running"}


