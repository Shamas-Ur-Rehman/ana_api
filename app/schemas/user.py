
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str
    role_id: Optional[int]

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    role: Optional[str]
    permissions: List[str]

    class Config:
        from_attributes = True 

class Token(BaseModel):
    access_token: str
    token_type: str
