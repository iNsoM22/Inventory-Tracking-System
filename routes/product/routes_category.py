from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from utils.db import db_dependency
from schemas.product import Category
from validations.product import CategoryRequest, CategoryResponse, CategoryResponseWithProducts
from utils.auth import require_access_level
from sqlalchemy.future import select


router = APIRouter(prefix="/categories")


@router.get("/all",
            response_model=List[CategoryResponseWithProducts],
            status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency):
    """Retrieve all Categories."""
    try:
        stmt = select(Category)
        result = await db.execute(stmt)
        categories = result.scalars().all()
        return [CategoryResponseWithProducts.model_validate(category) for category in categories]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Records: {str(e)}")


@router.post("/add",
             response_model=List[CategoryResponse],
             status_code=status.HTTP_201_CREATED)
async def add_categories(categories: List[CategoryRequest], db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Add a List of New Categories."""
    try:
        new_categories = []
        for cat in categories:
            new_category = Category(**cat.model_dump())
            new_categories.append(new_category)
            await db.add(new_category)
        
        await db.commit()
        response = []
        for category in new_categories:
            await db.refresh(category)
            response.append(CategoryResponse.model_validate(category))
        
        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Adding Records: {str(e)}")


@router.get("/get/{id}",
            response_model=CategoryResponseWithProducts,
            status_code=status.HTTP_200_OK)
async def get_category(id: int, db: db_dependency):
    """Retrieve a Category by ID."""
    try:
        stmt = select(Category).where(Category.id == id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Category Not Found")

        return CategoryResponseWithProducts.model_validate(category)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Retrieving Category: {str(e)}")


@router.delete("/del/{id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: int, db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Delete a Category by ID."""
    try:
        stmt = select(Category).where(Category.id == id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if category:
            await db.delete(category)
            await db.commit()
            return

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category Not Found")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Category: {str(e)}")


@router.put("/mod/{id}",
            response_model=CategoryResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_category(id: int, updated_data: CategoryRequest, db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Update a Category by ID."""
    try:
        stmt = select(Category).where(Category.id == id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if category:
            category.category = updated_data.category
            await db.commit()
            await db.refresh(category)
            return CategoryResponse.model_validate(category)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category Not Found")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Updating Category: {str(e)}")
