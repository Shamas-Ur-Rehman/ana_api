from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import  get_db
from app.services import user_service
from app.schemas.user import UserProfile, UserProfileUpdate 
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile", response_model=UserProfile)
def read_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.get_user_profile(db, current_user.id)

@router.put("/profile", response_model=UserProfile)
def edit_profile(data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.update_user_profile(db, current_user.id, data)

@router.delete("/profile")
def remove_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.delete_user_account(db, current_user.id)
