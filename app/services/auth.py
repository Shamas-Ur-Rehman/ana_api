from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserCreate
from app.utils.security import verify_password, hash_password

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def register_user(db: Session, user_data: UserCreate):
    hashed_pw = hash_password(user_data.password)

    role = db.query(models.Role).filter(models.Role.id == user_data.role_id).first() if user_data.role_id else None

    user = models.User(
        email=user_data.email,
        hashed_password=hashed_pw,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_permissions(user):
    role_perms = [perm.name for perm in user.role.permissions] if user.role else []
    user_perms = [perm.name for perm in user.permissions]
    return list(set(role_perms + user_perms))  
