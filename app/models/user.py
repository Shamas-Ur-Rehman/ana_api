from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.db import Base
from app.models.permission import user_permissions
from app.models.promotion import Promotion

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    phone_number = Column(String, unique=True, nullable=True)
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_phone_verified = Column(Boolean, default=False)
    business_license = Column(String, nullable=True) 
    promotions = relationship("Promotion", back_populates="creator")
    saved_by = relationship("SavedPromotion", backref="promotion", cascade="all, delete")
