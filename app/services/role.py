from app.models.role import Role
from app.repo.role_repo import RoleRepository

class RoleService:
    def __init__(self, db):
        self.db = db
        self.repo = RoleRepository(db)

    def create_role(self, role_data, user_id: int):
        role = Role(
            name=role_data.name,
            created_by=user_id  
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id, role_data, user_id: int):
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise Exception("Not found")

        role.name = role_data.name
        role.updated_by = user_id  

        self.db.commit()
        return role
