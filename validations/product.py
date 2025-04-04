from pydantic import BaseModel, UUID4, Field, ConfigDict, field_validator
from typing import Optional, List


class CategoryRequest(BaseModel):
    category: str = Field(..., description="Name of the Category")


class CategoryResponse(BaseModel):
    id: int = Field(..., description="Unique Identifier for the Category")
    category: str = Field(..., description="Name of the Category")

    model_config = ConfigDict(from_attributes=True)


class CategoryResponseWithProducts(CategoryResponse):
    products: Optional[List[dict]] = Field(
        default=None, description="List of Products associated with this Category"
    )
    
    @field_validator("products", mode="before")
    @classmethod
    def set_products(cls, value):
        """Ensure the category field is correctly set from the join."""
        products = [ProductResponse.model_validate(product).model_dump(exclude=["category_id"]) for product in value]
        return products
    
    

class ProductBase(BaseModel):
    """Base Pydantic model for Product."""
    name: str = Field(..., max_length=50, description="Name of the Product")
    description: str = Field(..., description="Description of the Product")
    price: float = Field(..., ge=0.0, description="Product price")
    is_removed: bool = Field(False, description="Product Removal Indicator")
    category_id: int = Field(..., description="Foreign Key: Category ID")
    
    model_config = ConfigDict(from_attributes=True)

    
class ProductRequest(ProductBase):
    """Request model for adding a Product."""
    pass


class ProductResponse(ProductBase):
    """Response model for Product."""
    id: UUID4 = Field(..., description="Unique Identifier for the Product")


class ProductResponseWithCategory(ProductBase):
    """Response model for Product."""
    id: UUID4 = Field(..., description="Unique Identifier for the Product")
    category: Optional[str] = Field(None, description="Category of the Product.")
    
    model_config = ConfigDict(from_attributes=True)
    @field_validator("category", mode="before")
    @classmethod
    def set_category(cls, value):
        """Ensure the category field is correctly set from the join."""
        cat = CategoryResponse.model_validate(value)
        return cat.category
    


class ProductUpdateRequest(BaseModel):
    """Request model for updating a Product."""
    name: Optional[str] = Field(None, max_length=50, description="Name of the Product")
    description: Optional[str] = Field(None, description="Description of the Product")
    price: Optional[float] = Field(None, ge=0.0, description="Product price")
    is_removed: Optional[bool] = Field(None, description="Product Removal Indicator")
    category_id: int = Field(None, description="Foreign Key: Category ID")
