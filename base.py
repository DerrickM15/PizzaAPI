from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Create the SQLAlchemy engine and session
engine = create_engine("sqlite:///pizza_users.db", echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()