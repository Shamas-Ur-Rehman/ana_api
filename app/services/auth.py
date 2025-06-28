from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import random
import logging

from app.models.user import User
from app.models.role import Role
from app.schemas import user as user_schema
from app.utils.security import verify_password, hash_password, create_access_token

logger = logging.getLogger(__name__)


# -----------------------
# Helper/Internal Methods
# -----------------------

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Login failed. User with email {email} not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(password, user.password):
        logger.warning(f"Login failed. Incorrect password for {email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info(f"User {email} authenticated successfully.")
    return user


def register_user(db: Session, user: user_schema.UserCreate):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration failed. Email {user.email} already exists.")
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
        logger.error(f"Error during registration for {user.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registration failed")


def get_user_permissions(user: User):
    role_perms = [perm.name for perm in user.role.permissions] if user.role else []
    user_perms = [perm.name for perm in user.permissions]
    return list(set(role_perms + user_perms))


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


# -----------------------
# Public Methods for Routes
# -----------------------

def handle_registration(user: user_schema.UserCreate, db: Session):
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    # if user.business_id:
    #     from app.models.business import Business
    #     business = db.query(Business).filter(Business.id == user.business_id).first()
    #     if not business:
    #         raise HTTPException(status_code=400, detail="Invalid business_id")

    # if user.branch_id:
    #     from app.models.branch import Branch
    #     branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
    #     if not branch:
    #         raise HTTPException(status_code=400, detail="Invalid branch_id")

    if role.name.lower() == "vendor" and not user.business_license:
        raise HTTPException(status_code=400, detail="Business license required for vendors")

    user.otp_code = generate_otp()
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db_user = register_user(db, user)

    return {
        "id": db_user.id,
        "email": db_user.email,
        "phone_number": db_user.phone_number,
        "is_phone_verified": db_user.is_phone_verified,
        "role": role.name,
        "permissions": get_user_permissions(db_user),
        "business_id": db_user.business_id,
        "branch_id": db_user.branch_id,
        "business_license": db_user.business_license,
        "otp": db_user.otp_code
    }

def handle_login(user: user_schema.UserLogin, db: Session):
    db_user = authenticate_user(db, user.email, user.password)
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset requested for unknown email: {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        db.refresh(user)
        logger.info(f"OTP generated for {email}: {otp}")
        return {"message": "OTP sent successfully", "otp": otp}  # Replace with SMS/Email later
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to generate OTP for {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP")


def verify_otp(db: Session, email: str, otp: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"OTP verification failed. User not found for {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.otp_code != otp:
        logger.warning(f"OTP verification failed. Invalid OTP for {email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    if user.otp_expiry < datetime.utcnow():
        logger.warning(f"OTP expired for {email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    logger.info(f"OTP verified successfully for {email}")
    return {"message": "OTP verified"}


def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset failed. User not found for {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        db.commit()
        logger.info(f"Password reset successful for {email}")
        return {"message": "Password reset successful"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting password for {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")
