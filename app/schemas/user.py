from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password:  instr(min_length=8, max_length=128)
    role_id: Optional[int]
    business_id: Optional[int]
    branch_id: Optional[int]
    phone_number: Optional[str]
    business_license: Optional[str]

    # ✅ Add these two fields
    otp_code: Optional[str] = None
    otp_expiry: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: Optional[str]
    is_phone_verified: bool
    role: Optional[str]
    permissions: List[str]
    business_id: Optional[int]
    branch_id: Optional[int]
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
    business_id: Optional[int]
    branch_id: Optional[int]

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    business_license: Optional[str] = None

    class Config:
        from_attributes = True  
