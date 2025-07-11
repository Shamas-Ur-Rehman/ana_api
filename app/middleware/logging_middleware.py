from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime
from app.dependencies import get_current_user_optional

logger = logging.getLogger("app.middleware.logging")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = await get_current_user_optional(request)
        user_email = user.email if user else "Anonymous"

        method = request.method
        url_path = request.url.path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_message = f"[{timestamp}] {method} {url_path} by {user_email}"
        logger.info(log_message)

        response = await call_next(request)
        return response
