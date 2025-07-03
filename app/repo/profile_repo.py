from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserProfileUpdate
import logging

logger = logging.getLogger(__name__)

class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update(self, user_id: int, update_data: UserProfileUpdate) -> User:
        user = self.get_by_id(user_id)
        try:
            for key, value in update_data.dict(exclude_unset=True).items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        logger.info(f"User {user_id} profile updated successfully.")
        return user

    def delete(self, user_id: int) -> dict:
        user = self.get_by_id(user_id)
        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        logger.info(f"User {user_id} deleted successfully.")
        return {"message": "User profile deleted successfully"}
