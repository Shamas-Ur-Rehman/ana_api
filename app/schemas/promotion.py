from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PromotionBase(BaseModel):
    title: str
    description: Optional[str]
    terms: Optional[str]
    image_url: Optional[str]
    start_date: datetime
    end_date: datetime
    discount: Optional[int]
    target_segments: Optional[str]

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(PromotionBase):
    status: Optional[str] = None

class PromotionOut(PromotionBase):
    id: int
    status: str
    approval_comments: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
class PromotionApproval(BaseModel):
    approved: bool
    comments: Optional[str] = None
    
    class Config:
        from_attributes = True
class RedeemRequest(BaseModel):
    code: str

