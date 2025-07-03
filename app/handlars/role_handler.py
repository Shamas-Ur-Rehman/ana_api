from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.role import RoleCreate
from app.services.role_service import RoleService

class RoleHandler:
    async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
        return RoleService(db).create_role(role)

    async def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return RoleService(db).get_roles(skip, limit)

    async def read_role(role_id: int, db: Session = Depends(get_db)):
        role = RoleService(db).get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
        updated = RoleService(db).update_role(role_id, role.name)
        if not updated:
            raise HTTPException(status_code=404, detail="Role not found")
        return updated

    async def delete_role(role_id: int, db: Session = Depends(get_db)):
        deleted = RoleService(db).delete_role(role_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"detail": "Role deleted successfully"}
