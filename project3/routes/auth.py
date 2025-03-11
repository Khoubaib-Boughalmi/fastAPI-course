from models import User
from middlewares.db_session import get_db
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field, EmailStr 
from starlette import status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_valid_username_password(db: Session, password: str, username: str) -> bool:
	user = db.query(User).filter(User.username == username).first()
	if not user:
		return False
	try:
		return ctx.verify(password, user.hashed_password)
	except:
		return False

class CreateUserRequest(BaseModel):
	email: EmailStr
	username: str = Field(min_length=5, max_length=15)
	password: str = Field(min_length=5)
	is_active: bool = Field(default=True)
	role: str = Field(default="guest")

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: CreateUserRequest, db: Session = Depends(get_db)):
	new_user = User(
		email= user_request.email,
		username= user_request.username,
		hashed_password= ctx.hash(user_request.password),
		is_active= user_request.is_active,
		role= user_request.role
	) 
	db.add(new_user)


@router.post("/token", status_code=status.HTTP_202_ACCEPTED)
async def login_access_token(form_data = Depends(OAuth2PasswordRequestForm),
							 db: Session = Depends(get_db)):
	
	if not check_valid_username_password(db, form_data.password, form_data.username):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Wrong Email or password"})
	return "Token"