from fastapi import Depends, HTTPException, status, Request
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.models.user import User
from app.db import get_db
from app.utils.security import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from app.utils.security import decode_token
from sqlalchemy.orm import joinedload
from app.models import User, Role 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    user = (
        db.query(User)
        .options(
            joinedload(User.permissions),
            joinedload(User.role).joinedload(Role.permissions)
        )
        .filter(User.email == email.lower())  
        .first()
    )
    
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> int:
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

async def get_current_user_optional(request: Request) -> Optional[User]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    db: Session = next(get_db())

    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            return None

        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        return None
    finally:
        db.close()