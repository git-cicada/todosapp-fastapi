from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from database import sessionLocal
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from models import Users
from .auth import get_current_user, bcrypt_context


router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    """ This will open a sessiona, first retunr then go for closing the session"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


db_dependency = Annotated[Session, Depends(get_db)] # To avoid code repetition
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/getUserInfo', status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    user_data = db.query(Users).filter(Users.id == user.get('id')).first()
    return user_data

@router.put('/changePassword')
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Save the new password
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

    return {"message": "Password changed successfully"}