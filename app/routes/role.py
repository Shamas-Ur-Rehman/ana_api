from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.role import RoleCreate, RoleResponse
from app.services import role_service
from app.db import get_db

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return role_service.create_role(db, role)

@router.get("/", response_model=list[RoleResponse])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return role_service.get_roles(db, skip, limit)

@router.get("/{role_id}", response_model=RoleResponse)
def read_role(role_id: int, db: Session = Depends(get_db)):
    db_role = role_service.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    updated = role_service.update_role(db, role_id, role.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated

@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    deleted = role_service.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"detail": "Role deleted successfully"}
