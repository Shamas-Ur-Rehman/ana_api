from fastapi import APIRouter
from app.handlars.profile_handler import UserHandler

router = APIRouter(prefix="/user", tags=["User"])

router.get("/profile")(UserHandler.read_profile)
router.put("/profile")(UserHandler.edit_profile)
router.delete("/profile")(UserHandler.remove_profile)
