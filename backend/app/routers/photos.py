from fastapi import APIRouter, Query
from app.services.photo_service import get_destination_photo

router = APIRouter(prefix="/api/photos", tags=["Photos"])


@router.get("/destination")
def destination_photo(destination: str = Query(..., min_length=1, max_length=200)):
    """
    Look up a real photo for a destination (city/country string) via
    Unsplash. Returns {"available": false} rather than an error when no
    photo could be found, so the frontend can cleanly fall back to a
    themed gradient without treating it as a failure.
    """
    photo = get_destination_photo(destination)
    if not photo:
        return {"available": False}
    return {"available": True, **photo}
