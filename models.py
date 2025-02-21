from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class ToDos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    description = Column(String(100))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String(50))