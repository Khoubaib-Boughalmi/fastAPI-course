from fastapi import Depends, HTTPException, Path
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from middlewares.db_session import get_db
from models import Todo

router = APIRouter()

class TodoRequest(BaseModel):
	title: str = Field(min_length=5, max_length=20)
	description: str = Field(min_length=5, max_length=200)
	priority: int = Field(gt=0, lt=6)
	complete: bool


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(db: Session = Depends(get_db)):
	return db.query(Todo).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: Session = Depends(get_db), todo_id: int = Path(gt=0)):
	todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail=f"No todo with id equals {todo_id}")
	return todo_model

@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, db: Session= Depends(get_db)):
	todo = Todo(**todo_request.model_dump())
	db.add(todo)
 

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo_request: TodoRequest, db: Session= Depends(get_db), todo_id: int= Path(gt=0)):
	print(todo_id)
	todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail=f"No todo with id equals {todo_id}")
	todo_model.title = todo_request.title
	todo_model.description = todo_request.description
	todo_model.priority = todo_request.priority
	todo_model.complete = todo_request.complete
	todo_model.priority = todo_request.priority
	
	db.add(todo_model)
 
@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: Session= Depends(get_db), todo_id: int= Path(gt=0)):
	todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail=f"No todo with id equals {todo_id}")
	db.delete(todo_model)

