from fastapi import APIRouter, Request, Response
from schema.product import Product
from typing import List

router = APIRouter()

products = []


@router.get("/products", response_model=List[Product])
async def read_products(request: Request):
    return products


@router.post("/add-products")
async def create_product(product: List[Product], response: Response):
    products.extend(product)
    response.status_code = 202
    return {"message": "Products Added Successfully"}
