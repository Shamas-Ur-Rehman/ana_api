from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services import auth
from app.db import get_db
from app.schemas import user as user_schema
from app.schemas.user import ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=user_schema.UserResponse)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return auth.handle_registration(user, db)
@router.post("/login", response_model=user_schema.Token)
def login(user: user_schema.UserLogin, db: Session = Depends(get_db)):
    return auth.handle_login(user, db)
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth.forgot_password(db, data.email)
@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    return auth.verify_otp(db, data.email, data.otp)
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth.reset_password(db, data.email, data.new_password)