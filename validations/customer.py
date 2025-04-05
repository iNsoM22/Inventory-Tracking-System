from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import Optional

class CustomerBase(BaseModel):
    first_name: str = Field(..., max_length=50, description="First Name of the Customer")
    last_name: str = Field(..., max_length=50, description="Last Name of the Customer")
    email: Optional[str] = Field(None, description="Email of the Customer")
    phone_number: str = Field(..., description="Phone of the Customer")
    address: Optional[str] = Field(None, description="Address of the Customer")
    
    model_config = ConfigDict(from_attributes=True)
    
    
class CustomerRequest(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: UUID4 = Field(..., description="Unique Identifier for the Customer")
    

class CustomerUpdateRequest(CustomerBase):
    first_name: Optional[str] = Field(None, max_length=50, description="First Name of the Customer")
    last_name: Optional[str] = Field(None, max_length=50, description="Last Name of the Customer")
    phone_number: Optional[str] = Field(None, description="Phone of the Customer")
    
    