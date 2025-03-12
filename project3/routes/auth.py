from datetime import datetime, timedelta
from models import User
from middlewares.db_session import get_db
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field, EmailStr
from starlette import status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
import jwt

router = APIRouter()
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "dee6bfb1974b22b29d3867d53754fddb0408ad2a6419d5e0a7a552cddce51a35"


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=15)
    password: str = Field(min_length=5)
    is_active: bool = Field(default=True)
    role: str = Field(default="guest")


class ReadUserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str = Field(min_length=5, max_length=15)
    is_active: bool = Field(default=True)
    role: str = Field(default="guest")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def check_valid_username_password(
    db: Session, password: str, username: str
) -> bool:
    user = get_user_by_username(username, db)
    if not user:
        return False
    try:
        return ctx.verify(password, user.hashed_password)
    except:
        return False


def generate_user_token(
    username: str, db: Session, expiration_delta: timedelta = timedelta(hours=1)
) -> str:
    user: ReadUserResponse = get_user_by_username(username, db)
    token = jwt.encode(
        payload={
            "sub": user.username,
            "email": user.email,
            "exp": datetime.now() + expiration_delta,
        },
        key=SECRET_KEY,
        algorithm="HS256",
    )
    return token


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: CreateUserRequest, db: Session = Depends(get_db)):
    new_user = User(
        email=user_request.email,
        username=user_request.username,
        hashed_password=ctx.hash(user_request.password),
        is_active=user_request.is_active,
        role=user_request.role,
    )
    db.add(new_user)


def get_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    return user


@router.get(
    "/users/{username}", response_model=ReadUserResponse, status_code=status.HTTP_200_OK
)
async def read_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User not found"}
        )
    return user


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_202_ACCEPTED)
async def login_access_token(
    form_data=Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)
):

    if not check_valid_username_password(
        db, form_data.password, form_data.username
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Wrong Email or password"},
        )
    token = generate_user_token(form_data.username, db)
    return {"access_token": token, "token_type": "bearer"}
