from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models import User, Role, Module, Permission
from app.dependencies import get_current_user


def checkPermission(module_name: str, permission_name: str):
    def permission_dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        module = db.query(Module).filter(func.lower(Module.name) == module_name.lower()).first()

        if not module:
            raise HTTPException(
                status_code=404,
                detail=f"Module '{module_name}' not found.",
            )

        permission = (
            db.query(Permission)
            .filter(
                func.lower(Permission.name) == permission_name.lower(),
                Permission.module_id == module.id,
            )
            .first()
        )

        print(f"Checking permission: {permission_name} in module: {module_name} for user: {current_user.email}")

        if not permission:
            available_permissions = db.query(Permission).filter(Permission.module_id == module.id).all()
            available_names = [perm.name for perm in available_permissions]
            raise HTTPException(
                status_code=403,
                detail={
                    "error": f"Permission '{permission_name}' not found in module '{module_name}'.",
                    "available_permissions": available_names
                },
            )

        # Check if user has the permission
        if permission in current_user.permissions:
            return True

        # Check if user's role has the permission
        role = current_user.role
        if role and permission in role.permissions:
            return True

        # If user/role doesn't have the permission
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": f"Permission '{permission_name}' denied for user '{current_user.email}' in module '{module_name}'.",
                "available_role_permissions": [perm.name for perm in role.permissions] if role else []
            },
        )

    return permission_dependency
