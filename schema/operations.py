from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone, timedelta
from typing import Dict, Literal


class Refund(BaseModel):
    id: int = Field(..., description="Unique identifier for the refund")
    order_id: str = Field(..., description="ID of the order that was refunded")
    product_ids: Dict[str, int] = Field(
        ..., description="IDs and Quantity of the product that was refunded")
    application_date: datetime = Field(
        ..., description="Date and time of when applied for refund")
    refund_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date and Time when the refund occurred")
    amount: float = Field(..., description="Amount for refunded")
    status: Literal["Pending", "Approved",
                    "Rejected"] = Field(default="Pending", description="")

    @property
    def is_refundable(self):
        """Checks if the refund can be processed."""
        return (datetime.now(timezone.utc) - self.application_date) <= timedelta(days=15)

    @property
    def handle_refund(self):
        """Checks if the refund can be approved."""
        if self.is_refundable:
            self.status = "Approved"
        else:
            self.status = "Rejected"
