import sys
from pathlib import Path

sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/utils/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/validations/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/schemas/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/routes/")))


from fastapi import FastAPI
from utils.db import create_database
from contextlib import asynccontextmanager
import uvicorn
from routes.routes import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    create_database()
    
    yield
    
    print("Shutting down")


app = FastAPI(lifespan=lifespan)

@app.get('/')
async def greet():
    return { 
        "Project": "Inventory Tracking System",
        "Author": "asta",
        "Version": "1.0.6",
        "Description": "An Inventory Management System with support of Multiple Stores."
    }



########################
#   Routes
########################

#######################
# User Related Routers
#######################
app.include_router(auth_router, tags=["Authentication"])
app.include_router(user_router, tags=["User Management"])
app.include_router(role_router, tags=["User Access Role Managment"])
app.include_router(customer_router, tags=["Customer Management"])
app.include_router(employee_router, tags=["Employee Management"])

#######################
# Order/Refund Routers
#######################
app.include_router(order_router, tags=["Order Managements"])
app.include_router(refund_router, tags=["Refund Management"])

##########################
# Product Related Routers
##########################
app.include_router(category_router, tags=["Category Management"])
app.include_router(product_router, tags=["Product Management"])

########################
# Store Related Routers
########################
app.include_router(location_router, tags=["Location Management"])
app.include_router(store_router, tags=["Store Management"])
app.include_router(inventory_router, tags=["Inventory Management"])

#########################
# Stocks Related Routers
#########################
app.include_router(restock_router, tags=["Restock Management"])
app.include_router(stock_removal_router, tags=["Stock Removal Management"])

##########################
# Partial Auditing Router
##########################
app.include_router(transaction_router, tags=["Transaction Management"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
