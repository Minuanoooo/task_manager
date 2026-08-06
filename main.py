from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///tasks.db")
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Taskbase(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(Boolean, default=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "status": self.status}

    def change_stat(self) -> None:
        self.status = not self.status


Base.metadata.create_all(engine)

app = FastAPI()


class TaskCreate(BaseModel):
    title: str


@app.get("/tasks")
def get_tasks():
    session = Session()
    tasks = session.query(Taskbase).all()
    return [t.to_dict() for t in tasks]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    session = Session()
    task = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if task:
        return task.to_dict()
    return {"error": "Task not found"}


@app.post("/tasks")
def create_task(task1: TaskCreate):
    session = Session()
    new_task = Taskbase(title=task1.title)
    session.add(new_task)
    session.commit()
    return new_task.to_dict()


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    session = Session()
    task_to_delete = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if task_to_delete:
        session.delete(task_to_delete)
        session.commit()
        return {"message": "Task deleted"}
    return {"error": "Task not found"}


@app.patch("/tasks/{task_id}")
def task_change_status(task_id: int):
    session = Session()
    task_to_update = session.query(Taskbase).filter(Taskbase.id == task_id).first()
    if task_to_update:
        task_to_update.change_stat()
        session.commit()
        return {"message": "Task status changed"}
    return {"error": "Task not found"}
