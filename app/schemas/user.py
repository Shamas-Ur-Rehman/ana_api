from pydantic import BaseModel, EmailStr, constr ,validator
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    role_id: Optional[int] = None
    phone_number: Optional[str] = None
    business_license: Optional[str] = None
    otp_code: Optional[str] = None
    otp_expiry: Optional[datetime] = None

    @validator("email")
    def normalize_email(cls, v):
        return v.lower()
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    @validator("email")
    def normalize_email(cls, v):
        return v.lower()

class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: Optional[str]
    is_phone_verified: bool
    role: Optional[str]
    permissions: List[str]
    business_license: Optional[str]
    

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user: UserResponse
    token: Token
class OTPVerify(BaseModel):
    phone_number: str
    otp_code: str
    
    
    
class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str
    
    
class UserProfile(BaseModel):
    email: EmailStr
    phone_number: str
    business_license: Optional[str]
    permissions: List[str]

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    business_license: Optional[str] = None

    class Config:
        from_attributes = True  
