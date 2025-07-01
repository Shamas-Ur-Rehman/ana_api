
from fastapi import FastAPI
from app.routes import auth, protected
from app.db import Base, engine
from app.routes import role
from app.routes import user
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(role.router)
app.include_router(user.router)

