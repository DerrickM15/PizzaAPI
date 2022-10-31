from sqlalchemy import  Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from base import Base

# Initialize Address class and define database columns
class Address(Base):

    __tablename__ = 'address'

    id=Column(Integer, primary_key=True, autoincrement=True)
    address=Column(String)
    city=Column(String)
    state=Column(String)
    zipcode=Column(String)
    user_id=Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref("address", uselist=False)) #back_populates="address"
    

    def __init__(self, address, city, state, zipcode, user):
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.user = user