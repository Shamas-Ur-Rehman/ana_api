from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserProfileUpdate
from app.services.profile_service import ProfileService
from app.models.user import User
from app.dependencies import get_current_user

class UserHandler:

    @staticmethod
    async def read_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return ProfileService(db).get_profile(current_user.id)

    @staticmethod
    async def edit_profile(
        data: UserProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return ProfileService(db).update_profile(current_user.id, data)

    @staticmethod
    async def remove_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return ProfileService(db).delete_profile(current_user.id)
