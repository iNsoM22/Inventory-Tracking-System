from pydantic import BaseModel, Field, model_validator
from typing import Dict, Literal
from datetime import datetime, timezone


class Order(BaseModel):
    id: str = Field(..., description="Unique identifier for the order.")

    cart: Dict[str, int] = Field(default_factory=dict,
                                 description="Mapping of product ID to quantity in the order.")

    total_price: float = Field(default=0.0, ge=0,
                               description="Total price of the order, including tax and discount.")

    discount: float = Field(default=0.0, ge=0, le=1,
                            description="Discount percentage applied to the order.")

    tax: float = Field(default=0.0, ge=0, le=1,
                       description="Tax percentage applied to the order.")

    status: Literal[
        "Done",
        "Pending",
        "Refunded",
        "Canceled"] = Field(default="Pending", description="Order status.")

    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                   description="Timestamp when the order was created.")

    order_mode: Literal[
        "Online",
        "Offline"] = Field(..., description="Order mode, either Online or Offline.")

    def calculate_total(self, catalog):
        """
        Calculates the total price after applying discount and tax.

        Args:
            product_prices (Dict[str, float])->{Product.id: Product.price}:
            A dictionary mapping product IDs to their discounted price.
        """
        subtotal = sum(
            catalog[product_id].discounted_price * quantity for product_id, quantity in self.cart.items())

        if self.discount:
            discount_amount = subtotal * self.discount
        tax_amount = (subtotal - discount_amount) * self.tax
        self.total_price = subtotal - discount_amount + tax_amount
