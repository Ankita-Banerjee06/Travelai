from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.trip import TripPlanRequest, TripResponse, TripListResponse, OptimizeBudgetRequest
from app.services import ai_service, trip_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("/plan", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def plan_trip(
    trip_data: TripPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and save an AI-powered travel itinerary."""
    try:
        ai_response = ai_service.generate_itinerary(
            destination=trip_data.destination,
            start_date=str(trip_data.start_date),
            end_date=str(trip_data.end_date),
            budget=trip_data.budget,
            currency=trip_data.currency,
            travelers=trip_data.travelers,
            preferences=trip_data.preferences,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

    trip = trip_service.create_trip_with_itinerary(
        db=db,
        user_id=current_user.id,
        trip_data=trip_data.model_dump(),
        ai_response=ai_response,
    )
    return trip


@router.get("/", response_model=list[TripListResponse])
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all trips for the current user."""
    return trip_service.get_user_trips(db, current_user.id)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific trip with full itinerary and budget."""
    trip = trip_service.get_trip_by_id(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a trip."""
    success = trip_service.delete_trip(db, trip_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )


@router.post("/{trip_id}/optimize-budget", response_model=TripResponse)
def optimize_budget(
    trip_id: int,
    optimize_data: OptimizeBudgetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Optimize the budget for an existing trip using AI."""
    trip = trip_service.get_trip_by_id(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Prepare current itinerary and budget for AI
    current_itinerary = [
        {
            "day_number": day.day_number,
            "title": day.title,
            "activities": day.activities,
            "estimated_cost": day.estimated_cost,
        }
        for day in trip.itinerary_days
    ]
    current_budget = [
        {
            "category": item.category,
            "amount": item.amount,
            "notes": item.notes,
        }
        for item in trip.budget_breakdown
    ]

    try:
        ai_response = ai_service.optimize_budget(
            destination=trip.destination,
            budget=trip.budget,
            currency=trip.currency,
            travelers=trip.travelers,
            current_itinerary=current_itinerary,
            current_budget=current_budget,
            optimization_goal=optimize_data.optimization_goal,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI optimization error: {str(e)}"
        )

    updated_trip = trip_service.update_trip_itinerary(db, trip, ai_response)
    return updated_trip
