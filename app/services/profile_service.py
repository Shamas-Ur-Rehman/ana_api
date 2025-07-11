from sqlalchemy.orm import Session
from app.schemas.user import UserProfileUpdate
from app.repo.profile_repo import ProfileRepository
from app.utils.response_helper import success_response, error_response
import logging

logger = logging.getLogger(__name__)

class ProfileService:
    def __init__(self, db: Session):
        self.repo = ProfileRepository(db)

    def get_profile(self, user_id: int):
        try:
            user = self.repo.get_by_id(user_id)
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
            logger.error(f"Failed to fetch profile for user {user_id}: {str(e)}")
            return error_response("Failed to retrieve profile", 500)

    def update_profile(self, user_id: int, update_data: UserProfileUpdate):
        try:
            user = self.repo.update(user_id, update_data)
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
            logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            return error_response("Failed to update user profile", 500)

    def delete_profile(self, user_id: int):
        try:
            result = self.repo.delete(user_id)
            return success_response(message=result["message"])
        except Exception as e:
            logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
            return error_response("Failed to delete user", 500)
