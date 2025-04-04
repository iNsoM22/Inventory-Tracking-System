import sys
from pathlib import Path

sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "schemas")))

from schemas import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


DATABASE_URL = "sqlite:///testing.db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        
    except SQLAlchemyError as e:
        db.rollback()

    finally:
        db.close()


def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully.")
    
    
db_dependency = Annotated[Session, Depends(get_db)]