from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import Optional, List


class LocationBase(BaseModel):
    name: str = Field(..., max_length=50, description="Name of the Location")
    address: str = Field(..., description="Address of the Location")
    model_config = ConfigDict(from_attributes=True)


class LocationRequest(LocationBase):
    pass
    

class LocationResponse(LocationBase):
    id: int = Field(..., description="Unique identifier for the Location")
    


class LocationResponseWithStores(LocationResponse):
    stores: Optional[List[dict]] = Field(
        default=None, description="List of Stores Associated with this Location")
    
    @computed_field
    @property
    def store_count(self) -> int:
        return len(self.stores) if self.stores else 0
    
    
