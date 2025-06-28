
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError
from app.utils.security import decode_token

router = APIRouter(prefix="/protected")

def get_current_user(token: str = Header(...)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid token")
    return payload["sub"]

@router.get("/me")
def protected_data(user_email: str = Depends(get_current_user)):
    return {"message": f"Hello, {user_email}"}
