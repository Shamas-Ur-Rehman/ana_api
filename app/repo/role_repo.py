from sqlalchemy.orm import Session, joinedload
from app.models.role import Role
from app.models.permission import Permission
from app.models.module import Module
from app.schemas.role import RoleCreate
from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, role: RoleCreate):
        
        existing_role = self.db.query(Role).filter(Role.name.ilike(role.name)).first()
        if existing_role:
            raise HTTPException(status_code=400, detail=f"Role '{role.name}' already exists")
        db_role = Role(name=role.name)
        all_permissions = []

        for module_data in role.modules:
            db_module = None

            if module_data.id:
                db_module = self.db.query(Module).filter(Module.id == module_data.id).first()

            if not db_module:
                db_module = self.db.query(Module).filter(Module.name == module_data.name).first()

            if not db_module:
                db_module = Module(name=module_data.name)
                self.db.add(db_module)
                self.db.flush()

            for perm_name in module_data.permissions:
                permission = (
                    self.db.query(Permission)
                    .filter(Permission.name == perm_name, Permission.module_id == db_module.id)
                    .first()
                )

                if not permission:
                    permission = Permission(name=perm_name, module_id=db_module.id)
                    self.db.add(permission)
                    self.db.flush()

                all_permissions.append(permission)

        db_role.permissions = all_permissions
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def get_all(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Role)
            .options(joinedload(Role.permissions).joinedload(Permission.module))
            .offset(skip)
            .limit(limit)
            .all()
        )
    def get_by_id(self, role_id: int):
        return (
            self.db.query(Role)
            .options(joinedload(Role.permissions).joinedload(Permission.module))
            .filter(Role.id == role_id)
            .first()
        )

    def delete(self, role_id: int) -> bool:
        db_role = self.get_by_id(role_id)
        if not db_role:
            return False  # Role does not exist

        try:
            self.db.delete(db_role)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete role {role_id}: {str(e)}")
            return False

    def update(self, role_id: int, role_data: RoleCreate):
        db_role = self.get_by_id(role_id)
        if not db_role:
            return None

        db_role.name = role_data.name
        all_permissions = []

        for module_data in role_data.modules:
            db_module = None
            if module_data.id:
                db_module = self.db.query(Module).filter(Module.id == module_data.id).first()

            if not db_module:
                db_module = self.db.query(Module).filter(Module.name == module_data.name).first()

            if not db_module:
                db_module = Module(name=module_data.name)
                self.db.add(db_module)
                self.db.flush()

            for perm_name in module_data.permissions:
                permission = (
                    self.db.query(Permission)
                    .filter(Permission.name == perm_name, Permission.module_id == db_module.id)
                    .first()
                )
                if not permission:
                    permission = Permission(name=perm_name, module_id=db_module.id)
                    self.db.add(permission)
                    self.db.flush()

                all_permissions.append(permission)

        db_role.permissions = all_permissions
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def delete(self, role_id: int) -> bool:
        db_role = self.get_by_id(role_id)
        if not db_role:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No role found with ID {role_id}")
            return False

        try:
            self.db.delete(db_role)
            self.db.commit()
            logger.info(f"Role {role_id} deleted")
            return True
        except Exception as e:
            self.db.rollback()
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to delete role {role_id}: {str(e)}")
            return False
