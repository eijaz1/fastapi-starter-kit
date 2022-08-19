from fastapi import FastAPI
# from . import models
from app import models
# from .database import engine
from app.database import engine
from app.routers import user, task, auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)