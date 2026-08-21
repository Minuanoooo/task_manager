from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


class UserCreate(BaseModel):
    email: str
    password: str
