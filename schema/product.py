from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., description="Unique Identifier for the Product.")
    name: str = Field(..., description="Name of the Product.")
    category: str = Field(..., description="Category of the Product.")

    price: float = Field(default=0.0, ge=0, description="Product price.")
    discount: float = Field(default=0.0, ge=0, le=1,
                            description="Product discount (0-1).")

    @property
    def discounted_price(self) -> float:
        """Calculate the price after discount, ensuring it doesn't go negative."""
        return max(0, self.price * (1 - self.discount))
