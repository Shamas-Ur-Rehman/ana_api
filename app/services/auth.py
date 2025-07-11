from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import random
import logging

from app.repo.user_repo import UserRepository
from app.models.user import User
from app.models.role import Role
from app.schemas import user as user_schema
from app.utils.security import verify_password, hash_password, create_access_token
from app.utils.response_helper import success_response, error_response

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
        if not user.role_id:
            user.role_id = 22

        role = self.db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            return error_response("Invalid role_id", 400)

        if role.name.lower() == "vendor":
            if not user.business_license:
                return error_response("Business license is required for vendors", 400)
            if not user.phone_number:
                return error_response("Phone number is required for vendors", 400)

        if self.user_repo.get_by_email(user.email):
            return error_response("Email already registered", 400)

        # Generate OTP and expiry
        user.otp_code = self._generate_otp()
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

        # Save user
        db_user = self.user_repo.create(user)

        return success_response(
            message="User registered successfully",
            code=201,
            data={
                "id": db_user.id,
                "email": db_user.email,
                "phone_number": db_user.phone_number,
                "is_phone_verified": db_user.is_phone_verified,
                "role": role.name,
                "permissions": self._get_user_permissions(db_user),
                "business_license": db_user.business_license,
            }
        )

    def handle_login(self, user: user_schema.UserLogin):
        db_user = self.user_repo.get_by_email(user.email)
        if not db_user or not verify_password(user.password, db_user.password):
            logger.warning(f"Authentication failed for email: {user.email}")
            return error_response("Invalid credentials", 401)

        token = create_access_token({"sub": db_user.email})
        logger.info(f"User {user.email} authenticated successfully.")
        return success_response(
            message="Login successful",
            data={"access_token": token, "token_type": "bearer"}
        )

    def forgot_password(self, email: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return error_response("User not found", 404)

        otp = self._generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        self.user_repo.update_otp(user, otp, user.otp_expiry)

        logger.info(f"OTP generated for {email}: {otp}")
        return success_response(
            message="OTP sent successfully",
            data={"otp": otp} 
        )

    def verify_otp(self, email: str, otp: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return error_response("User not found", 404)

        if user.otp_code != otp:
            return error_response("Invalid OTP", 400)

        if user.otp_expiry < datetime.utcnow():
            return error_response("OTP expired", 400)

        logger.info(f"OTP verified successfully for {email}")
        return success_response(message="OTP verified")

    def reset_password(self, email: str, new_password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return error_response("User not found", 404)

        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        self.user_repo.update_otp(user, user.otp_code, user.otp_expiry)

        logger.info(f"Password reset successful for {email}")
        return success_response(message="Password reset successful")
