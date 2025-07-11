from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime , UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    terms = Column(Text)
    image_url = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    discount = Column(Integer)
    target_segments = Column(String)  
    status = Column(String, default="pending") 
    approval_comments = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="promotions")
    saved_promotions = relationship("SavedPromotion", backref="user", cascade="all, delete")

class SavedPromotion(Base):
    __tablename__ = "saved_promotions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    promotion_id = Column(Integer, ForeignKey("promotions.id"))
    saved_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "promotion_id", name="uix_user_promotion"),)