from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/utils/")))

from schemas.store import Location
from validations.location import LocationRequest, LocationResponse, LocationResponseWithStores
from utils.db import db_dependency


router = APIRouter(prefix="/locations")


@router.post("/add", response_model=LocationResponse)
async def add_location(location: LocationRequest, db: db_dependency):
    try:
        new_location = Location(**location.model_dump())
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
        return LocationResponse.model_validate(new_location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Adding Location: {str(e)}")


@router.get("/all", response_model=List[LocationResponseWithStores])
async def get_locations(db: db_dependency):
    try:
        locations = db.query(Location).all()
        return [LocationResponseWithStores.model_validate(location) for location in locations]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Locations: {str(e)}")


@router.get("/get/{id}", response_model=LocationResponseWithStores)
async def get_location(id: int, db: db_dependency):
    try:
        location = db.query(Location).filter(Location.id == id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location Not Found")
        return LocationResponseWithStores.model_validate(location)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Location: {str(e)}")

@router.delete("/del/{id}", response_model=LocationResponse)
async def delete_location(id: int, db: db_dependency):
    try:
        location = db.query(Location).filter(Location.id == id).first()
        if location:
            db.delete(location)
            db.commit()
            return LocationResponse.model_validate(location)
       
        raise HTTPException(status_code=404, detail="Location Not Found")
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting location: {str(e)}")


@router.put("/mod/{id}", response_model=LocationResponse)
async def update_location(id: int, location: LocationRequest, db: db_dependency):
    try:
        location_to_update = db.query(Location).filter(Location.id == id).first()
        if location_to_update:
            location_to_update.name = location.name
            location_to_update.address = location.address
            db.commit()
            db.refresh(location_to_update)
            return LocationResponse.model_validate(location_to_update)
        
        raise HTTPException(status_code=404, detail="Location Not Found")
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating location: {str(e)}")
