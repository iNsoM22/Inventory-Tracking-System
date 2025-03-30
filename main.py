import uvicorn
from fastapi import FastAPI
from routes.routes import router

app = FastAPI()


@app.get('/')
async def greet():
    return {
        "Project": "Inventory Tracking System",
        "Author": "asta",
        "Version": "1.0.0",
        "Description": "An Inventory Management System with support of Multiple Stores."
    }


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",
                port=8000, reload=True)
