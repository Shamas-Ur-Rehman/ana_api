from sqlalchemy.orm import Session
from app import models
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import verify_password, hash_password
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Login attempt failed. User with email {email} not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(password, user.password):
        logger.warning(f"Login attempt failed. Invalid password for email: {email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info(f"User {email} authenticated successfully.")
    return user


def register_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration failed. Email {user.email} is already registered.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
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
        logger.info(f"User {user.email} registered successfully.")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration of user {user.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registration failed")


def get_user_permissions(user: User):
    role_perms = [perm.name for perm in user.role.permissions] if user.role else []
    user_perms = [perm.name for perm in user.permissions]
    return list(set(role_perms + user_perms))


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        db.refresh(user)
        logger.info(f"OTP generated for email {email}: {otp}")
        return {"message": "OTP sent successfully", "otp": otp}  # Replace with SMS/Email in prod
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating OTP for email {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP")


def verify_otp(db: Session, email: str, otp: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"OTP verification failed. User not found for email: {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.otp_code != otp:
        logger.warning(f"OTP verification failed. Invalid OTP for email: {email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    if user.otp_expiry < datetime.utcnow():
        logger.warning(f"OTP verification failed. OTP expired for email: {email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    logger.info(f"OTP verified successfully for email: {email}")
    return {"message": "OTP verified"}


def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset failed. User not found for email: {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        db.commit()
        logger.info(f"Password reset successful for email: {email}")
        return {"message": "Password reset successful"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting password for email {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")
