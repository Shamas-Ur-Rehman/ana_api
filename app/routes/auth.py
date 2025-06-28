from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.services import auth
from app.schemas import user as user_schema
from app.utils.security import create_access_token
from app.db import get_db
from app.schemas.user import ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=user_schema.UserResponse)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    from app.models.role import Role 
    
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if role and role.name.lower() == "vendor" and not user.business_license:
        raise HTTPException(status_code=400, detail="Business license required for vendors")

    from random import randint
    from datetime import datetime, timedelta

    otp = str(randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    user.otp_code = otp
    user.otp_expiry = otp_expiry

    db_user = auth.register_user(db, user)

    return {
        "id": db_user.id,
        "email": db_user.email,
        "phone_number": db_user.phone_number,
        "is_phone_verified": db_user.is_phone_verified,
        "role": db_user.role.name if db_user.role else None,
        "permissions": auth.get_user_permissions(db_user),
        "business_id": db_user.business_id,
        "branch_id": db_user.branch_id,
        "business_license": db_user.business_license,
        "otp": otp  
    }


@router.post("/login", response_model=user_schema.Token)
def login(user: user_schema.UserLogin, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth.forgot_password(db, data.email)

@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    return auth.verify_otp(db, data.email, data.otp)

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth.reset_password(db, data.email, data.new_password)