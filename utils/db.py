from schemas import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_url = os.environ.get("DB_URL")
db_name = os.environ.get("DB_NAME")


DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_url}/{db_name}"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)


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
    print("Database Created Successfully.")


db_dependency = Annotated[Session, Depends(get_db)]
