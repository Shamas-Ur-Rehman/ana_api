from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base 
from app.models.permission import user_permissions  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"))  # ✅ Add this line
    role = relationship("Role", back_populates="users")  # ✅ Add this line

    business_id = Column(Integer, ForeignKey('businesses.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))

    business = relationship("Business", back_populates="users")
    branch = relationship("Branch", back_populates="users")

    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")