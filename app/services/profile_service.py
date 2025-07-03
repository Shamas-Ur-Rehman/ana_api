
from sqlalchemy.orm import Session
from app.schemas.user import UserProfileUpdate
from app.repo.profile_repo import ProfileRepository

class ProfileService:
    def __init__(self, db: Session):
        self.repo = ProfileRepository(db)

    def get_profile(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def update_profile(self, user_id: int, update_data: UserProfileUpdate):
        return self.repo.update(user_id, update_data)

    def delete_profile(self, user_id: int):
        return self.repo.delete(user_id)
