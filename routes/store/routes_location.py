from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from schemas.store import Location
from validations.location import LocationRequest, LocationResponse, LocationResponseWithStores
from utils.db import db_dependency
from utils.auth import require_access_level
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


router = APIRouter(prefix="/locations")


@router.post("/add",
             response_model=LocationResponse,
             status_code=status.HTTP_201_CREATED)
async def add_location(location: LocationRequest, db: db_dependency,
                       current_user: Annotated[dict, Depends(require_access_level(4))]):
    try:
        new_location = Location(**location.model_dump())
        db.add(new_location)
        await db.commit()
        await db.refresh(new_location)
        return LocationResponse.model_validate(new_location)

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Location with Same Name or Address Already Exists.")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error Adding Location: {str(e)}")


@router.get("/all",
            response_model=List[LocationResponseWithStores],
            status_code=status.HTTP_200_OK)
async def get_locations(db: db_dependency,
                        limit: int = 50,
                        offset: int = 0):
    try:
        stmt = select(Location).offset(offset).limit(limit)
        result = await db.execute(stmt)
        locations = result.scalars().all()
        return [LocationResponseWithStores.model_validate(location) for location in locations]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Locations: {str(e)}")


@router.get("/get/{id}",
            response_model=LocationResponseWithStores,
            status_code=status.HTTP_200_OK)
async def get_location(id: int, db: db_dependency):
    try:
        stmt = select(Location).where(Location.id == id)
        result = await db.execute()
        location = result.scalar_one_or_none()
        
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Location Not Found")
        return LocationResponseWithStores.model_validate(location)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error Fetching Location: {str(e)}")


@router.delete("/del/{id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(id: int, db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(4))]):
    try:
        stmt = select(Location).where(Location.id == id)
        result = await db.execute(stmt)
        location = result.scalar_one_or_none()
        if location:
            await db.delete(location)
            await db.commit()
            return

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Location Not Found")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error deleting location: {str(e)}")


@router.put("/mod/{id}",
            response_model=LocationResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_location(id: int, location: LocationRequest, db: db_dependency):
    try:
        stmt = select(Location).where(Location.id == id)
        result = await db.execute(stmt)
        location_to_update = result.scalar_one_or_none()
        
        if not location_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Location Not Found")

        if not location.name and not location.address:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Fields Provided for Updation.")

        if location.name:
            location_to_update.name = location.name
        if location.address:
            location_to_update.address = location.address

        await db.commit()
        await db.refresh(location_to_update)
        return LocationResponse.model_validate(location_to_update)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Location: {str(e)}")
