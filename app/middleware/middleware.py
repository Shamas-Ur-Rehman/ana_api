from fastapi import  HTTPException, Header
from app.utils.security import decode_token

def checkAuth(token: str = Header(...)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid token")
    return payload["sub"]
