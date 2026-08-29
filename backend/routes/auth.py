from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserCreate, UserLogin
from utils.auth import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter()


@router.post("/signup", status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    email = str(user.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    db.add(User(email=email, password_hash=hash_password(user.password)))
    db.commit()
    return {"message": "User created successfully"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    email = str(user.email).lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if not existing_user or not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(existing_user.id), "email": existing_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {"email": current_user["email"]}
