from database import Base
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
