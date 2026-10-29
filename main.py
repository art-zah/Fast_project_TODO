from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from pydantic import ValidationError
from database import Tasks, create_tables, add_data, Session
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import os

from pedant import Tasks as Tasks_pd
from templates_config import templates

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан, проверьте .env")

app = FastAPI()

create_tables()

app.mount("/css", StaticFiles(directory="css"), name="css")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

def get_tasks():
    with Session() as db_session:
        tasks = db_session.execute(select(Tasks)).scalars().all()
    return tasks

@app.get("/", tags=["root"])
async def root(request: Request):
   tasks = get_tasks()
   errors = request.session.pop("errors", [])
   return templates.TemplateResponse(request=request, name="index.html",
           context={"request": request, "tasks": tasks, "errors": errors})


@app.post("/create", tags=["create"], status_code=201)
async def create(request: Request, task_header: str = Form(""), task_description: str = Form(""), 
    status: str = Form("")):
    errors = []
    tasks = get_tasks()

    try: 
        Tasks_pd(task_header=task_header, task_description=task_description, status=status)

        TasksORM = Tasks(task_header=task_header, task_description=task_description, addition_time=datetime.now(), status=status)
        with Session() as db_sesion:
            add_data(TasksORM)

        return RedirectResponse(url="/", status_code=303)

    except ValidationError:
        if not task_header or not status:
            errors.append("Пожалуйста, заполните обязательные поля (название задачи и статус) ")

        if len(task_header) < 1 or len(task_header) > 100:
            errors.append('поле "название заадчи" не должно превышать 100 символов и должно содержать хотя бы 1 символ')

        if len(task_description) > 255:
            errors.append('поле "описание задачи" не должно превышать 255 символов')

        if len(task_description) > 255:
            errors.append('поле "статус" не должно превышать 255 символов')

    except IntegrityError:
        errors.append("задача уже существует")

    except Exception as e:
        print("Ошибка в /create:", e)
        errors.append("неизвестная ошибка, попробуйте повторить действия позже")

    request.session["errors"] = errors
    return RedirectResponse(url="/", status_code=303)

@app.post("/update/{id}", tags=["update"])
async def update(request: Request, id: int, task_header: str = Form(""), task_description: str = Form(""), 
    status: str = Form("")):
    errors = []
    taskss = get_tasks()

    try: 
        Tasks_pd(task_header=task_header, task_description=task_description, status=status)

        with Session() as db_session:
            tasks = db_session.execute(select(Tasks).where(Tasks.id == id)).scalars().first()

            if tasks is None:
                request.session["errors"] = ["Задача не найдена"]
                return RedirectResponse(url="/", status_code=303)
                
            tasks.task_header = task_header
            if not task_description is None: 
                tasks.task_description = task_description
            tasks.status = status

            db_session.commit()
            return RedirectResponse(url="/", status_code=303)

    except ValidationError:
        if not task_header or not status:
            errors.append("Пожалуйста, заполните обязательные поля (название задачи и статус) ")

        if len(task_header) < 1 or len(task_header) > 100:
            errors.append('поле "название заадчи" не должно превышать 100 символов и должно содержать хотя бы 1 символ')

        if len(task_description) > 255:
            errors.append('поле "описание задачи" не должно превышать 255 символов')

        if len(status) > 255:
            errors.append('поле "статус" не должно превышать 255 символов')

    except Exception as e:
        print("Ошибка в /update:", e)
        errors.append("неизвестная ошибка, попробуйте повторить действия позже")

    request.session["errors"] = errors
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{id}", tags=["delete"])
async def delete(request: Request, id: int):
    try:
        with Session() as db_session:
            tasks = db_session.execute(select(Tasks).where(Tasks.id == id)).scalars().first()
            
            if tasks is None:
                request.session["errors"] = ["Задача не найдена"]
                return RedirectResponse(url="/", status_code=303)

            db_session.delete(tasks)
            db_session.commit()


    except Exception as e:
        print("Ошибка в /delete:", e)
        request.session["errors"] = ["Неизвестная ошибка, попробуйте повторить действия позже"]
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)