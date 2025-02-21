from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter, Request, status
from database import sessionLocal
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from models import ToDos
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


template = Jinja2Templates(directory="./templates")


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)



class ToDoRequest(BaseModel):
    """ To handle POST Request data parsing
    Here we dont have to worry about id as SQLAlchemy will auto increment it as it defined as Primary Key"""
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=5)
    complete: bool

def get_db():
    """ This will open a sessiona, first retunr then go for closing the session"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

db_dependency = Annotated[Session, Depends(get_db)] # To avoid code repetition
user_dependency = Annotated[dict, Depends(get_current_user)]


### PAGES ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        
        todos = db.query(ToDos).filter(ToDos.owner_id == user.get('id')).all()
        return template.TemplateResponse("todo.html", {"request": request, "todos": todos, "user":user})
    except:
        return redirect_to_login()
    

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return template.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except Exception as e:
        print("Exception", e)
        return redirect_to_login()
    
@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        
        todo = db.query(ToDos).filter(ToDos.id == todo_id).first()
        if todo:
            return template.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
        return HTTPException(status_code=404, detail="Todo not found")
    except Exception as e:
        print("Exception", e)
        return redirect_to_login()
    

### END POINTS ###
@router.get('/readAllTodos', status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db: db_dependency):
    """Depends is for dependency injection. It means before read_all it will first execute get_db
    and retunr the db object"""
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    return db.query(ToDos).all()




@router.get('/readTodosByUserId/{user_id}', status_code=status.HTTP_200_OK)
async def read_todos_by_user(user_id:int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    return db.query(ToDos).filter(ToDos.owner_id == user_id).all()




@router.get('/readTodo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    if user is None:    
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get(id)).first()
    if todo_model:
        return todo_model
    return HTTPException(status_code=404, detail="Todo not found")




@router.post('/createTodo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      todo_request: ToDoRequest, db: db_dependency):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    todo_model = ToDos(**todo_request.dict(), owner_id=user['id'])
    db.add(todo_model)
    db.commit()
    return todo_model




@router.put('/updateTodo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: ToDoRequest,
                      todo_id: int = Path(gt=0)):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_model:
        for key, value in todo_request.dict().items():
            setattr(todo_model, key, value)
        db.add(todo_model)
        db.commit()
        return
    return HTTPException(status_code=404, detail="Todo not found")




@router.delete('/deleteTodo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, 
                      db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
    return HTTPException(status_code=404, detail="Todo not found")