from sqlalchemy.orm import Session
from app.models.role import Role
from app.schemas.role import RoleCreate

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, role: RoleCreate):
        db_role = Role(name=role.name)
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Role).offset(skip).limit(limit).all()

    def get_by_id(self, role_id: int):
        return self.db.query(Role).filter(Role.id == role_id).first()

    def update(self, role_id: int, name: str):
        db_role = self.get_by_id(role_id)
        if db_role:
            db_role.name = name
            self.db.commit()
            self.db.refresh(db_role)
        return db_role

    def delete(self, role_id: int):
        db_role = self.get_by_id(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
        return db_role
