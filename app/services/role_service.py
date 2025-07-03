from sqlalchemy.orm import Session
from app.schemas.role import RoleCreate
from app.repo.role_repo import RoleRepository

class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def create_role(self, role: RoleCreate):
        return self.repo.create(role)

    def get_roles(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def get_role(self, role_id: int):
        return self.repo.get_by_id(role_id)

    def update_role(self, role_id: int, name: str):
        return self.repo.update(role_id, name)

    def delete_role(self, role_id: int):
        return self.repo.delete(role_id)
