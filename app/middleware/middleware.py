# from fastapi import  HTTPException, Header
# from app.utils.security import decode_token

# def checkAuth(token: str = Header(...)):
#     payload = decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=403, detail="Invalid token Please Give me a valid token")
#     return payload["sub"]
from fastapi import HTTPException, Request, status

def checkAuth(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing or invalid format",
        )

    token = auth_header.split(" ")[1]
    
    from app.utils.security import decode_token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid token")

    return payload["sub"] 

