from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.trip import TripPlanRequest, TripResponse, TripListResponse, OptimizeBudgetRequest
from app.services import ai_service, trip_service
from app.services.ai_service import AIServiceError, AIRateLimitError
from app.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trips", tags=["Trips"])

MAX_TRIP_DAYS = 21


@router.post("/plan", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def plan_trip(
    trip_data: TripPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and save an AI-powered travel itinerary."""
    trip_length = (trip_data.end_date - trip_data.start_date).days + 1
    if trip_length > MAX_TRIP_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trips longer than {MAX_TRIP_DAYS} days aren't supported yet. Please choose a shorter date range."
        )
    if trip_length < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after the start date."
        )

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
    except AIRateLimitError as e:
        logger.warning(f"AI rate limit hit in plan_trip (destination={trip_data.destination!r}): {e}")
        headers = {"Retry-After": str(e.retry_after_seconds)} if e.retry_after_seconds else {}
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Our AI planner is at capacity right now. Please try again in a few minutes.",
            headers=headers,
        )
    except AIServiceError as e:
        logger.error(f"AIServiceError in plan_trip (destination={trip_data.destination!r}): {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Our AI planner had trouble generating your itinerary. Please try again in a moment."
        )
    except Exception:
        logger.exception(f"Unexpected error in plan_trip (destination={trip_data.destination!r})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating your itinerary. Please try again."
        )

    if not ai_response.get("itinerary"):
        logger.error(f"AI planner returned no itinerary for destination={trip_data.destination!r}: {ai_response!r}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI planner didn't return a usable itinerary. Please try again."
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
    except AIRateLimitError as e:
        logger.warning(f"AI rate limit hit in optimize_budget (trip_id={trip_id}): {e}")
        headers = {"Retry-After": str(e.retry_after_seconds)} if e.retry_after_seconds else {}
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Our AI planner is at capacity right now. Please try again in a few minutes.",
            headers=headers,
        )
    except AIServiceError as e:
        logger.error(f"AIServiceError in optimize_budget (trip_id={trip_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Our AI planner had trouble optimizing your budget. Please try again in a moment."
        )
    except Exception:
        logger.exception(f"Unexpected error in optimize_budget (trip_id={trip_id})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while optimizing your budget. Please try again."
        )

    updated_trip = trip_service.update_trip_itinerary(db, trip, ai_response)
    return updated_trip