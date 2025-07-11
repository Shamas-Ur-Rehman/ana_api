from sqlalchemy.orm import Session
from fastapi import status
from app.schemas.role import RoleCreate
from app.repo.role_repo import RoleRepository
from fastapi.responses import JSONResponse
from app.utils.response_helper import success_response, error_response


import logging
logger = logging.getLogger(__name__)
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
        return success_response(
            message="Role created successfully",
            code=status.HTTP_201_CREATED,
            data=self._to_response(role_obj)
        )

    def get_roles(self, skip: int = 0, limit: int = 100):
        roles = self.repo.get_all(skip, limit)
        return success_response(
            message="Roles fetched successfully",
            data=[self._to_response(role) for role in roles]
        )

    def get_role(self, role_id: int):
        role = self.repo.get_by_id(role_id)
        if not role:
            return error_response("Role not found", status.HTTP_404_NOT_FOUND)
        return success_response(
            message="Role fetched successfully",
            data=self._to_response(role)
        )

    def update_role(self, role_id: int, role: RoleCreate):
        updated_role = self.repo.update(role_id, role)
        if not updated_role:
            return error_response("Role not found or update failed", status.HTTP_404_NOT_FOUND)
        return success_response(
            message="Role updated successfully",
            data=self._to_response(updated_role)
        )

    def delete_role(self, role_id: int):
        try:
            success = self.repo.delete(role_id)
            if not success:
                logger.warning(f"No role found with ID {role_id}")
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "message": "Role not found",
                        "code": 404,
                        "data": None
                    }
                )
            logger.info(f"Role {role_id} deleted successfully")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Role deleted successfully",
                    "code": 200,
                    "data": None
                }
            )
        except Exception as e:
            logger.error(f"Exception while deleting role {role_id}: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Internal server error while deleting role",
                    "code": 500,
                    "data": None
                }
            )