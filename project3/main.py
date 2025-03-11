from fastapi import FastAPI, Request
from database import engine, sessionLocal
from sqlalchemy.orm import Session
from routes import auth, todos
import models
from middlewares.db_session import db_session_middleware


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.middleware("http")(db_session_middleware)

app.include_router(auth.router)
app.include_router(todos.router)