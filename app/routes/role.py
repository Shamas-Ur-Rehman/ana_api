from fastapi import APIRouter, Depends
from app.handlars.role_handler import RoleHandler
from app.middleware.middleware import checkAuth

router = APIRouter(prefix="/roles", tags=["Roles"])
router.post("/", dependencies=[Depends(checkAuth)])(RoleHandler.create_role)
router.get("/", dependencies=[Depends(checkAuth)])(RoleHandler.read_roles)
router.get("/{role_id}", dependencies=[Depends(checkAuth)])(RoleHandler.read_role)
router.put("/{role_id}", dependencies=[Depends(checkAuth)])(RoleHandler.update_role)
router.delete("/{role_id}", dependencies=[Depends(checkAuth)])(RoleHandler.delete_role)
