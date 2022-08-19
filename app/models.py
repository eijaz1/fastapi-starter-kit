from app.database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self) -> str:
        return self.email

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    def __str__(self) -> str:
        return self.description