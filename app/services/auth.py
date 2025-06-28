from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserCreate
from app.utils.security import verify_password, hash_password
from datetime import datetime, timedelta
from app.models.user import User
from fastapi import HTTPException
import random




def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def register_user(db: Session, user: UserCreate):
    from app.models.user import User
    from app.utils.security import hash_password

    db_user = User(
        email=user.email,
        password=hash_password(user.password),
        role_id=user.role_id,
        business_id=user.business_id,
        branch_id=user.branch_id,
        phone_number=user.phone_number,
        otp_code=user.otp_code,
        otp_expiry=user.otp_expiry,
        business_license=user.business_license
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_permissions(user):
    role_perms = [perm.name for perm in user.role.permissions] if user.role else []
    user_perms = [perm.name for perm in user.permissions]
    return list(set(role_perms + user_perms)) 

def authenticate_user(db, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and verify_password(password, user.password): 
        return user
    return None 

def generate_otp():
    return str(random.randint(100000, 999999))

def forgot_password(db, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.commit()
    db.refresh(user)
    return {"message": "OTP sent successfully", "otp": otp}  # return only for development

def verify_otp(db, email: str, otp: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    return {"message": "OTP verified"}

def reset_password(db, email: str, new_password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = hash_password(new_password)
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    return {"message": "Password reset successful"}
