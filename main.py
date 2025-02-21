from fastapi import FastAPI, Request, status
from database import engine
from routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine) #Create the db file and the table in the database
# templates = Jinja2Templates(directory="./templates") Not required now
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/")
def test(request: Request):
    # return templates.TemplateResponse("home.html", {"request": request})
    return RedirectResponse(url='/todos/todo-page', status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)