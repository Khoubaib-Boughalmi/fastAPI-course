from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_DATABASE_URL = "sqlite:///./project3.db" # File-based

engine = create_engine(SQL_DATABASE_URL, connect_args={"check_same_thread": False})

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine) # will be instantiated to create a live db connection: db = sessionLocal()

Base = declarative_base() # will be inherited by class Model: class User(Base)
