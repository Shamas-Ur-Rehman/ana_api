from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import random
import logging

from app.repo.user_repo import UserRepository
from app.models.user import User
from app.models.role import Role
from app.schemas import user as user_schema
from app.utils.security import verify_password, hash_password, create_access_token

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def _get_user_permissions(self, user: User):
        role_perms = [perm.name for perm in user.role.permissions] if user.role else []
        user_perms = [perm.name for perm in user.permissions]
        return list(set(role_perms + user_perms))

    def _generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    def handle_registration(self, user: user_schema.UserCreate):
        role = self.db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id")

        if role.name.lower() == "vendor" and not user.business_license:
            raise HTTPException(status_code=400, detail="Business license required for vendors")

        if self.user_repo.get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user.otp_code = self._generate_otp()
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

        db_user = self.user_repo.create_user(user)

        return {
            "id": db_user.id,
            "email": db_user.email,
            "phone_number": db_user.phone_number,
            "is_phone_verified": db_user.is_phone_verified,
            "role": role.name,
            "permissions": self._get_user_permissions(db_user),
            "business_id": db_user.business_id,
            "branch_id": db_user.branch_id,
            "business_license": db_user.business_license,
            "otp": db_user.otp_code
        }

    def handle_login(self, user: user_schema.UserLogin):
        db_user = self.user_repo.get_by_email(user.email)
        if not db_user or not verify_password(user.password, db_user.password):
            logger.warning(f"Authentication failed for email: {user.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = create_access_token({"sub": db_user.email})
        logger.info(f"User {user.email} authenticated successfully.")
        return {"access_token": token, "token_type": "bearer"}

    def forgot_password(self, email: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        otp = self._generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        self.user_repo.update_user(user)

        logger.info(f"OTP generated for {email}: {otp}")
        return {"message": "OTP sent successfully", "otp": otp}

    def verify_otp(self, email: str, otp: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.otp_code != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        if user.otp_expiry < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP expired")

        logger.info(f"OTP verified successfully for {email}")
        return {"message": "OTP verified"}

    def reset_password(self, email: str, new_password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        self.user_repo.update_user(user)

        logger.info(f"Password reset successful for {email}")
        return {"message": "Password reset successful"}
