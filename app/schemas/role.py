from pydantic import BaseModel
from typing import List

class ModulePermission(BaseModel):
    id: int
    name: str
    permissions: List[str]

class RoleCreate(BaseModel):
    name: str
    modules: List[ModulePermission]
class ModuleInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PermissionResponse(BaseModel):
    id: int
    name: str
    module: ModuleInfo 

    class Config:
        from_attributes = True
