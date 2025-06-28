from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.services import auth
from app.schemas import user as user_schema
from app.utils.security import create_access_token
from app.db import get_db

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=user_schema.UserResponse)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.register_user(db, user)
    return {
        "email": db_user.email,
        "role": db_user.role.name if db_user.role else None,
        "permissions": auth.get_user_permissions(db_user)
    }

@router.post("/login", response_model=user_schema.Token)
def login(user: user_schema.UserLogin, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
