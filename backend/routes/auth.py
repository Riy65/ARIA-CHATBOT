from fastapi import APIRouter, HTTPException , Depends

from models.user import UserCreate , UserLogin

from utils.auth import hash_password
from utils.auth import (
    verify_password,
    create_access_token
)

from database import db

router = APIRouter()

users_collection = db["users"]


@router.post("/signup")
def signup(user: UserCreate):
    

    existing_user = users_collection.find_one(
        {"email": user.email}
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        user.password
    )

    users_collection.insert_one(
        {
            "email": user.email,
            "password": hashed_password
        }
    )

    return {
        "message": "User created successfully"
    }


@router.post("/login")
def login(user: UserLogin):

    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
        
    if not verify_password(
        user.password,
        existing_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_access_token(
        {
            "email": existing_user["email"]
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
@router.get("/me")
def get_me(current_user=Depends(get_current_user)):

    return {
        "email": current_user["email"]
    }