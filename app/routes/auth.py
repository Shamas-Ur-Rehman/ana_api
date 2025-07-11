# routes/auth_routes.py
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, Header
from app.utils.security import decode_token
from app.middleware.middleware import checkAuth
from app.handlars.auth_handler import AuthHandler

router = APIRouter(prefix="/auth")
router.post("/register")(AuthHandler.register)
router.post("/login")(AuthHandler.login)
router.post("/forgot-password")(AuthHandler.forgot_password)
router.post("/verify-otp")(AuthHandler.verify_otp)
router.post("/reset-password")(AuthHandler.reset_password)
