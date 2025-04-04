from fastapi import APIRouter, HTTPException
from typing import List
from validations.product import ProductRequest, ProductResponse, ProductUpdateRequest, ProductResponseWithCategory
from utils.db import db_dependency
from schemas.product import Product
from uuid import UUID


router = APIRouter(prefix="/products")


@router.post("/add", response_model=List[ProductResponse])
async def add_products(products: List[ProductRequest], db: db_dependency):
    """Add a List of New Products."""
    try:
        new_products = [Product(**product.model_dump()) for product in products]
        db.add_all(new_products)
        db.commit()
        
        for product in new_products:
            db.refresh(product)
        return [ProductResponse.model_validate(prod) for prod in new_products]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Adding Products: {str(e)}")


@router.get("/all/active", response_model=List[ProductResponseWithCategory])
async def get_active_products(db: db_dependency):
    try:
        products = db.query(Product).filter(Product.is_removed == False).all()
        return [ProductResponseWithCategory.model_validate(product) for product in products]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Products: {str(e)}")

    
@router.get("/all", response_model=List[ProductResponseWithCategory])
async def get_products(db: db_dependency):
    try:
        products = db.query(Product).all()
        return [ProductResponseWithCategory.model_validate(product) for product in products]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Products: {str(e)}")


@router.get("/get/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: db_dependency):
    try:
        product = db.query(Product).filter(Product.id == product_id, Product.is_removed == False).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product Not Found")
        return ProductResponse.model_validate(product)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Product: {str(e)}")


@router.put("/mod/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, update_data: ProductUpdateRequest, db: db_dependency):
    try:
        product_to_update = db.query(Product).filter(Product.id == product_id).first()
        if not product_to_update:
            raise HTTPException(status_code=404, detail="Product Not Found")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(product_to_update, field, value)

        db.commit()
        db.refresh(product_to_update)
        return ProductResponse.model_validate(product_to_update)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Product: {str(e)}")



@router.delete("/del/{product_id}", response_model=ProductResponse)
async def delete_product(product_id: UUID, db: db_dependency):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()

            return {"detail": "Product and its Related Information has been Deleted Successfully."}

        raise HTTPException(status_code=404, detail="Product Not Found")
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Product: {str(e)}")