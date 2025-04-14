from schemas import *
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_url = os.environ.get("DB_URL")
db_name = os.environ.get("DB_NAME")


DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_url}/{db_name}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            
        except SQLAlchemyError:
            await session.rollback()
            raise
        
        finally:
            await session.close()


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database Created Successfully.")


db_dependency = Annotated[AsyncSession, Depends(get_db)]
