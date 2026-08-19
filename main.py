from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SECRET_KEY = "любая-случайная-строка-держи-в-секрете"
ALGORITHM = "HS256"
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        aut = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = aut.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


engine = create_engine("sqlite:///tasks.db")
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Taskbase(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "status": self.status}

    def change_stat(self) -> None:
        self.status = not self.status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    def get_password_hash(self, password: str) -> None:
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def to_dict(self) -> dict:
        return {"id": self.id, "email": self.email}


Base.metadata.create_all(engine)

app = FastAPI()


class TaskCreate(BaseModel):
    title: str


class UserCreate(BaseModel):
    email: str
    password: str


@app.get("/tasks")
def get_tasks(current_user: int = Depends(get_current_user)):
    session = Session()
    tasks = session.query(Taskbase).filter(Taskbase.user_id == current_user).all()
    return [t.to_dict() for t in tasks]


@app.get("/tasks/{task_id}")
def get_task(task_id: int, current_user: int = Depends(get_current_user)):
    session = Session()
    task = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if task:
        return task.to_dict()
    return {"error": "Task not found"}


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
        return {"error": "Task not found"}
    if task_to_delete.user_id != current_user:
        return {"error": "Not your task"}
    session.delete(task_to_delete)
    session.commit()
    return {"message": "Task deleted"}


@app.patch("/tasks/{task_id}")
def task_change_status(task_id: int, current_user: int = Depends(get_current_user)):
    session = Session()
    task_to_update = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if not task_to_update:
        return {"error": "Task not found"}
    if task_to_update.user_id != current_user:
        return {"error": "Not your task"}
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
    return {"error": "Invalid credentials"}
