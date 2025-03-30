from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# Design Choice: Each Customer has to Place their Orders for their Data to be handled and Stored.
class Customer(BaseModel):
    id: str = Field(..., description="Unique identifier for the customer")
    first_name: str = Field(..., description="First name of the customer")
    last_name: str = Field(..., description="Last name of the customer")
    order_id: Optional[str] = Field(
        None, description="Associated order ID")
    phone_number: Optional[str] = Field(
        None, description="Customer's Phone number")
    email: Optional[EmailStr] = Field(
        None, description="Customer's Email Address")
    address: Optional[str] = Field(
        None, description="Customer's Physical Address")
