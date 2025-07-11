from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas import user as user_schema
from app.utils.security import hash_password
from datetime import datetime
from typing import Optional
from sqlalchemy import func


class UserRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(func.lower(User.email) == email.lower()).first()


    def create(self, user: user_schema.UserCreate) -> User:
        db_user = User(
            email=user.email,
            password=hash_password(user.password),
            role_id=user.role_id,
            business_license=user.business_license,
            phone_number=user.phone_number,
            otp_code=user.otp_code,
            otp_expiry=user.otp_expiry,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_otp(self, user: User, otp_code: str, expiry: datetime):
        user.otp_code = otp_code
        user.otp_expiry = expiry
        self.db.commit()
        self.db.refresh(user)

    def reset_password(self, user: User, new_password: str):
        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        self.db.commit()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()
