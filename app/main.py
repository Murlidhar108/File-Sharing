from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import client_user

# ✅ Auto-create tables in DB
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(client_user.router)
