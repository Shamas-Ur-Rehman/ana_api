from sqlalchemy.orm import Session
from app.schemas.role import RoleCreate
from app.repo.role_repo import RoleRepository


class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def _to_response(self, role):
        return {
            "id": role.id,
            "name": role.name,
            "permissions": [perm.name for perm in role.permissions]
        }

    def create_role(self, role: RoleCreate):
        role_obj = self.repo.create(role)
        return self._to_response(role_obj)

    def get_roles(self, skip: int = 0, limit: int = 100):
        roles = self.repo.get_all(skip, limit)
        return [self._to_response(role) for role in roles]

    def get_role(self, role_id: int):
        role = self.repo.get_by_id(role_id)
        return self._to_response(role) if role else None

    def update_role(self, role_id: int, role: RoleCreate):
        updated_role = self.repo.update(role_id, role)
        return self._to_response(updated_role) if updated_role else None

    def delete_role(self, role_id: int):
        return self.repo.delete(role_id)
