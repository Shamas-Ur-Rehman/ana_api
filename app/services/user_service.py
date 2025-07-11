from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserProfileUpdate  
from fastapi import status
from app.utils.response_helper import success_response, error_response
import logging

logger = logging.getLogger(__name__)

def get_user_profile(db: Session, user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        return success_response(
            message="User profile retrieved successfully",
            data={
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "name": user.name,
                "is_phone_verified": user.is_phone_verified,
                "role": user.role.name if user.role else None,
                "permissions": [perm.name for perm in user.permissions]
            }
        )
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return error_response("Failed to retrieve user", status.HTTP_500_INTERNAL_SERVER_ERROR)

def update_user_profile(db: Session, user_id: int, update_data: UserProfileUpdate):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found for update.")
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)

        logger.info(f"User {user_id} profile updated successfully.")
        return success_response(
            message="User profile updated successfully",
            data={
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "name": user.name,
                "is_phone_verified": user.is_phone_verified
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user {user_id}: {str(e)}")
        return error_response("Failed to update user profile", status.HTTP_500_INTERNAL_SERVER_ERROR)

def delete_user_account(db: Session, user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found for deletion.")
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        db.delete(user)
        db.commit()

        logger.info(f"User {user_id} deleted successfully.")
        return success_response(message="User profile deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return error_response("Failed to delete user", status.HTTP_500_INTERNAL_SERVER_ERROR)
