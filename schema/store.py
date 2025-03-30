from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict
from .product import Product


class Store(BaseModel):
    id: int = Field(..., description="Unique identifier for the store")
    name: str = Field(..., description="Name of the store")
    location: str = Field(...,
                          description="Geographical location of the store")

    inventory: Dict[int, int] = Field(
        default_factory=dict,
        description="Mapping of product IDs to their available quantities"
    )
    sales: list[str] = Field(
        default_factory=dict,
        description="Mapping of Order IDs"
    )
    refunds: list[str] = Field(
        default_factory=dict,
        description="Mapping of Refund IDs"
    )
    revenue: float = Field(
        default=0.0, ge=0, description="Total revenue from sales"
    )
    sellouts: list[str] = Field(
        default=list, description="List of Product IDs, which are sold out and needed to be restoked "
    )
    supervisor: str = Field(...,
                            description="Supervisor or Manager of the Store."
                            )
    last_stock_update: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time inventory was updated"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time store details were updated"
    )

    def add_product(self, product: Product, quantity: int = 1):
        """Adds a product to inventory with quantity."""
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if product.id in self.inventory:
            self.inventory[product.id] += quantity
        else:
            self.inventory[product.id] = quantity

        self.last_stock_update = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def sell_product(self, product: Product, quantity: int = 1):
        """Records a sale and updates inventory."""
        product_id = product.id

        if product_id not in self.inventory or self.inventory[product_id] < quantity:
            raise ValueError("Not enough stock available.")

        self.inventory[product_id] -= quantity
        if self.inventory[product_id] == 0:
            del self.inventory[product_id]

        self.sales[product_id] = self.sales.get(product_id, 0) + quantity
        self.revenue += product.discounted_price * quantity

        self.updated_at = datetime.now(timezone.utc)

    def remove_product(self, product):
        product_id = product.id
        if product_id in self.inventory:
            del self.inventory[product_id]
            self.updated_at = datetime.now(timezone.utc)
