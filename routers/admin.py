from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from database import sessionLocal
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from models import ToDos
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def get_db():
    """ This will open a sessiona, first retunr then go for closing the session"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)] # To avoid code repetition
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/readAllTodos', status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db: db_dependency):
    """Depends is for dependency injection. It means before read_all it will first execute get_db
    and retunr the db object"""
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorised")
    return db.query(ToDos).all()

@router.delete('/deleteTodo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, 
                      db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
    return HTTPException(status_code=404, detail="Todo not found")