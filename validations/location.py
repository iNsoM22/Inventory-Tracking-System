from pydantic import BaseModel, Field, computed_field
from uuid import UUID
from typing import Optional, List


class LocationRequest(BaseModel):
    name: str = Field(..., max_length=50, description="Name of the Location")
    address: str = Field(..., description="Address of the Location")


class LocationResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the Location")
    name: str = Field(..., max_length=50, description="Name of the Location")
    address: str = Field(..., description="Address of the Location")

    model_config = {"from_attributes": True}


class LocationResponseWithStores(LocationResponse):
    stores: Optional[List[dict]] = Field(
        default=None, description="List of Store IDs associated with this Location"
    )
    
    @computed_field
    @property
    def store_count(self) -> int:
        return len(self.stores) if self.stores else 0
    
    
