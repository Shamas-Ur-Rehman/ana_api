from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth import AuthService
from app.schemas.user import (
    UserCreate, UserLogin, ForgotPasswordRequest,
    VerifyOtpRequest, ResetPasswordRequest
)

class AuthHandler:

    async def register(user: UserCreate, db: Session = Depends(get_db)):
        return AuthService(db).handle_registration(user)

    async def login(user: UserLogin, db: Session = Depends(get_db)):
        return AuthService(db).handle_login(user)

    async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
        return AuthService(db).forgot_password(data.email)

    async def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
        return AuthService(db).verify_otp(data.email, data.otp)

    async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
        return AuthService(db).reset_password(data.email, data.new_password)
