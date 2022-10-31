from sqlalchemy import  Column, String, Integer
from sqlalchemy.orm import relationship
import pydantic
from pydantic import BaseModel
import typing

from base import Base

# Initialize user class and define database columns
class User(Base):

    __tablename__ = 'users'

    id=Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String)
    username=Column(String, nullable=False, unique=True)
    email=Column(String)
    password=Column(String)

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password

class UserRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str
    address: str
    city: str
    state: str
    zipcode: str

class UserResponseModel(BaseModel):
    id: int = None
    username: str = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    id: int = None
    name: str = None
    username: str = None
    email: str = None
    password: str = None
    address: str = None
    city: str = None
    state: str = None
    zipcode: str = None
