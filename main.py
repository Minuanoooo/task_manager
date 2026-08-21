from auth import create_access_token, get_current_user
from database import Base, Session, engine
from fastapi import Depends, FastAPI, HTTPException
from models import Taskbase, User
from schemas import TaskCreate, UserCreate

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/tasks")
def get_tasks(current_user: int = Depends(get_current_user)):
    session = Session()
    tasks = session.query(Taskbase).filter(Taskbase.user_id == current_user).all()
    return [t.to_dict() for t in tasks]


@app.get("/tasks/{task_id}")
def get_task(task_id: int, current_user: int = Depends(get_current_user)):
    session = Session()
    task = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user:
        raise HTTPException(status_code=403, detail="Task not yours")
    return task.to_dict()


@app.post("/tasks")
def create_task(task1: TaskCreate, current_user: int = Depends(get_current_user)):
    session = Session()
    new_task = Taskbase(title=task1.title, user_id=current_user)
    session.add(new_task)
    session.commit()
    return new_task.to_dict()


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: int = Depends(get_current_user)):
    session = Session()
    task_to_delete = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if not task_to_delete:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_to_delete.user_id != current_user:
        raise HTTPException(status_code=403, detail="Task not yours")
    session.delete(task_to_delete)
    session.commit()
    return {"message": "Task deleted"}


@app.patch("/tasks/{task_id}")
def task_change_status(task_id: int, current_user: int = Depends(get_current_user)):
    session = Session()
    task_to_update = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if not task_to_update:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_to_update.user_id != current_user:
        raise HTTPException(status_code=403, detail="Task not yours")
    task_to_update.change_stat()
    session.commit()
    return {"message": "Task status changed"}


@app.post("/users")
def create_user(user: UserCreate):
    session = Session()
    new_user = User(email=user.email)
    new_user.get_password_hash(user.password)
    session.add(new_user)
    session.commit()
    return new_user.to_dict()


@app.post("/login")
def login_user(user: UserCreate):
    session = Session()
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user and existing_user.verify_password(user.password):
        return create_access_token(existing_user.id)
    raise HTTPException(status_code=401, detail="Unauthorized")
