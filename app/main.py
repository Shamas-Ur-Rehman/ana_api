
from fastapi import FastAPI
from app.routes import auth, protected
from app.db import Base, engine
from app.routes import role

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(role.router)
