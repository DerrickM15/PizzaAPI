from sqlalchemy import  Column, String, Integer
from sqlalchemy.orm import relationship
import pydantic
from pydantic import BaseModel


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
    id: int
    username: str

    class Config:
        orm_mode = True