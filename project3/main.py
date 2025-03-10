from functools import wraps
from fastapi import Depends, FastAPI, HTTPException, Path, Request
from pydantic import BaseModel, Field
from database import engine, sessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
	"""
		- Database session middleware ensures that a single session is maintained throughout the request: middleware-based session, all endpoints within the same request lifecycle share the same session (querying data, logging in, sending an email...).
		- Properly commits on success and rolls back on failure
		It reduces the overhead of creating and destroying multiple database connections.
		It ensures consistency across different parts of the request (e.g., if a transaction spans multiple operations, they all happen within the same session).
		It allows you to commit or rollback changes at the end of the request, preventing half-completed database operations in case of an error. ==> Atomicity
	"""
	db = sessionLocal()
	request.state.db = db
	try:
		response = await call_next(request)
		if request.method not in ["GET"]:
			db.flush()
			db.commit()
	except:
		print("rollback")
		db.rollback()
		raise
	finally:
		print("close")
		db.close()
	return response


def get_db(request: Request) -> Session:
	return request.state.db

class TodoRequest(BaseModel):
	title: str = Field(min_length=5, max_length=20)
	description: str = Field(min_length=5, max_length=200)
	priority: int = Field(gt=0, lt=6)
	complete: bool


@app.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(db: Session = Depends(get_db)):
	return db.query(models.Todos).all()


@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: Session = Depends(get_db), todo_id: int = Path(gt=0)):
	todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail=f"No todo with id equals {todo_id}")
	return todo_model

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, db: Session= Depends(get_db)):
	todo = models.Todos(**todo_request.model_dump())
	db.add(todo)