from fastapi import FastAPI
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes import auth
from app.db import Base, engine
from app.routes import role
from app.routes import user
from app.routes import promotion
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(role.router)
app.include_router(user.router)
app.include_router(promotion.router)

app.add_middleware(LoggingMiddleware)

