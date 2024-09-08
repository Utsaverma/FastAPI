from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..models import Users
from ..database import  get_db
from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix='/users',
    tags=['users']
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserResponse(BaseModel):

    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    phone_number: str

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return {
        'email':  user_model.email,
        'username': user_model.username,
        'first_name': user_model.first_name,
        'last_name': user_model.last_name,
        'role': user_model.role,
        'is_active': user_model.is_active,
        'phone_number': user_model.phone_number
    }


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number:str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()
