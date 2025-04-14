from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from validations.product import ProductRequest, ProductResponse, ProductUpdateRequest, ProductResponseWithCategory
from utils.db import db_dependency
from schemas.product import Product
from uuid import UUID
from utils.auth import require_access_level
from sqlalchemy.future import select


router = APIRouter(prefix="/products")


@router.post("/add",
             response_model=List[ProductResponse],
             status_code=status.HTTP_201_CREATED)
async def add_products(products: List[ProductRequest],
                       db: db_dependency,
                       current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Add a List of New Products."""
    try:
        new_products = []
        for product in products:
            new_product = Product(**product.model_dump())
            new_products.append(new_product)
            await db.add(new_product)
            
        await db.commit()
        
        response = []
        for product in new_products:
            db.refresh(product)
            response.append(ProductResponse.model_validate(product))
        
        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Adding Products: {str(e)}")


@router.get("/all/active",
            response_model=List[ProductResponseWithCategory],
            status_code=status.HTTP_200_OK)
async def get_active_products(db: db_dependency):
    try:
        stmt = select(Product).where(Product.is_removed == False)
        result = await db.execute(stmt)
        products = result.scalars().all()
        return [ProductResponseWithCategory.model_validate(product) for product in products]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Products: {str(e)}")


@router.get("/all",
            response_model=List[ProductResponseWithCategory],
            status_code=status.HTTP_200_OK)
async def get_products(db: db_dependency):
    """Get All Products (Active + Removed)."""
    try:
        stmt = select(Product)
        result = await db.execute(stmt)
        products = result.scalars().all()
        return [ProductResponseWithCategory.model_validate(product) for product in products]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Products: {str(e)}")


@router.get("/get/{product_id}",
            response_model=ProductResponse,
            status_code=status.HTTP_200_OK)
async def get_product(product_id: UUID, db: db_dependency):
    try:
        stmt = select(Product).where(Product.id == product_id, Product.is_removed == False)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Product Not Found")

        return ProductResponse.model_validate(product)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Product: {str(e)}")


@router.put("/mod/{product_id}",
            response_model=ProductResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_product(product_id: UUID,
                         update_data: ProductUpdateRequest,
                         db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(4))]):
    try:
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product_to_update = result.scalar_one_or_none()
        
        if not product_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Product Not Found")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(product_to_update, field, value)

        await db.commit()
        await db.refresh(product_to_update)
        return ProductResponse.model_validate(product_to_update)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Product: {str(e)}")


@router.delete("/del/{product_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID,
                         db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(4))]):
    try:
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            await db.delete(product)
            await db.commit()
            return

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product Not Found")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Deleting Product: {str(e)}")
