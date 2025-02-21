from fastapi import APIRouter, Request
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from models import Users
from starlette import status
from passlib.context import CryptContext
from database import sessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

JWT_SECRET = "c94b49e9b7d6aa618b57d0c6afb2f8d9253835a2fb921f121cee3336bb6b81af" #It could be anything. here we generated it with `openssl rand -hex 32` command in terminal
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username : str
    email : str
    first_name : str
    last_name : str
    password : str
    role: str

class Token(BaseModel): # I AM NOT SURE WHAT IS THE NEED. without tis it still work fine
    access_token: str
    token_type: str

def get_db():
    """ This will open a sessiona, first retunr then go for closing the session"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)] # To avoid code repetition
templates = Jinja2Templates(directory="./templates")

## PAGES ##
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

## ENDPOINTS ##
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, user_role:str, expires_delta: timedelta):
    """Create a JWT token"""
    encode = {'sub': username, 'id': user_id, 'role': user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, JWT_SECRET, algorithm=ALGORITHM)

#Using a synchronous function may be simpler, but it can block the event loop, 
# potentially reducing the performance of our FastAPI application when handling multiple concurrent requests.
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """Get the current user from the JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM]) 
        username: str = payload.get('sub')
        user_id: id = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User could not be validated.")
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User could not be validated.")

@router.post('/', status_code=status.HTTP_201_CREATED) # Lets replace /auth with / as we are using /auth in prefix
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    ## NOTE: we could use **create_user_request.dict() to pass all the values to the model
    ## But it will not work here as password filed name in Pydentic model and User model are different
    create_user_model = Users(username=create_user_request.username, 
                             email=create_user_request.email, 
                             first_name=create_user_request.first_name, 
                             last_name=create_user_request.last_name,
                             hashed_password=bcrypt_context.hash(create_user_request.password),
                             role=create_user_request.role,
                             is_active=True)
    db.add(create_user_model)  
    db.commit() 
    return {"message": "User created successfully"}

@router.post('/token', response_model=Token) #auth/token -> due to prefix /auth
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user:
        token = create_access_token(user.username, user.id, user.role, timedelta(minutes=10))
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User could not be validated.")