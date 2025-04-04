from fastapi import APIRouter, HTTPException
from typing import List
from utils.db import db_dependency
from schemas.product import Category
from validations.product import CategoryRequest, CategoryResponse, CategoryResponseWithProducts

router = APIRouter(prefix="/categories")

@router.get("/all", response_model=List[CategoryResponseWithProducts])
async def get_categories(db: db_dependency):
    """Retrieve all Categories."""
    try:
        categories = db.query(Category).all()
        return [CategoryResponseWithProducts.model_validate(category) for category in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Records: {str(e)}")

@router.post("/add", response_model=List[CategoryResponse])
async def add_categories(categories: List[CategoryRequest], db: db_dependency):
    """Add a list of new categories."""
    try:
        new_categories = [Category(**cat.model_dump()) for cat in categories]
        db.add_all(new_categories)
        db.commit()
        
        for category in new_categories:
            db.refresh(category)
        
        return [CategoryResponse.model_validate(cat) for cat in new_categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Adding Records: {str(e)}")


@router.get("/get/{id}", response_model=CategoryResponseWithProducts)
async def get_category(id:int , db: db_dependency):
    """Retrieve a Category by ID."""
    try:
        category = db.query(Category).filter(Category.id == id).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category Not Found")
        
        return CategoryResponseWithProducts.model_validate(category)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Retrieving Category: {str(e)}")


@router.delete("/del/{id}", response_model=CategoryResponse)
async def delete_category(id:int , db: db_dependency):
    """Delete a Category by ID."""
    try:
        category = db.query(Category).filter(Category.id == id).first()
        
        if category:
            db.delete(category)
            db.commit()
            return CategoryResponse.model_validate(category)
        
        raise HTTPException(status_code=404, detail="Category Not Found")
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Deleting Category: {str(e)}")


@router.put("/mod/{id}", response_model=CategoryResponse)
async def update_category(id:int, updated_data:CategoryRequest, db: db_dependency):
    """Update a Category by ID."""
    try:
        category = db.query(Category).filter(Category.id == id).first()
        
        if category:
            category.category = updated_data.category
            db.commit()
            db.refresh(category)
            return CategoryResponse.model_validate(category)
        
        raise HTTPException(status_code=404, detail="Category Not Found")
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Updating Category: {str(e)}")
