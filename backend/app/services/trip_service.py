from sqlalchemy.orm import Session
from app.models.trip import Trip, Itinerary, BudgetBreakdown


def create_trip_with_itinerary(db: Session, user_id: int, trip_data: dict, ai_response: dict) -> Trip:
    """Create a trip record with its generated itinerary and budget breakdown."""
    trip = Trip(
        user_id=user_id,
        destination=trip_data["destination"],
        start_date=trip_data["start_date"],
        end_date=trip_data["end_date"],
        budget=trip_data["budget"],
        currency=trip_data.get("currency", "USD"),
        travelers=trip_data.get("travelers", 1),
        preferences=trip_data.get("preferences", []),
    )
    db.add(trip)
    db.flush()

    # Add itinerary days
    for day in ai_response.get("itinerary", []):
        itinerary_day = Itinerary(
            trip_id=trip.id,
            day_number=day["day_number"],
            title=day["title"],
            activities=day.get("activities", []),
            estimated_cost=day.get("estimated_cost", 0.0),
        )
        db.add(itinerary_day)

    # Add budget breakdown
    for item in ai_response.get("budget_breakdown", []):
        budget_item = BudgetBreakdown(
            trip_id=trip.id,
            category=item["category"],
            amount=item["amount"],
            notes=item.get("notes", ""),
        )
        db.add(budget_item)

    db.commit()
    db.refresh(trip)
    return trip


def get_user_trips(db: Session, user_id: int) -> list[Trip]:
    """Get all trips for a user."""
    return db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).all()


def get_trip_by_id(db: Session, trip_id: int, user_id: int) -> Trip | None:
    """Get a specific trip by ID for a user."""
    return db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()


def delete_trip(db: Session, trip_id: int, user_id: int) -> bool:
    """Delete a trip by ID for a user."""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        return False
    db.delete(trip)
    db.commit()
    return True


def update_trip_itinerary(db: Session, trip: Trip, ai_response: dict) -> Trip:
    """Update a trip's itinerary and budget breakdown with new AI response."""
    # Delete existing itinerary and budget
    db.query(Itinerary).filter(Itinerary.trip_id == trip.id).delete()
    db.query(BudgetBreakdown).filter(BudgetBreakdown.trip_id == trip.id).delete()

    # Add new itinerary days
    for day in ai_response.get("itinerary", []):
        itinerary_day = Itinerary(
            trip_id=trip.id,
            day_number=day["day_number"],
            title=day["title"],
            activities=day.get("activities", []),
            estimated_cost=day.get("estimated_cost", 0.0),
        )
        db.add(itinerary_day)

    # Add new budget breakdown
    for item in ai_response.get("budget_breakdown", []):
        budget_item = BudgetBreakdown(
            trip_id=trip.id,
            category=item["category"],
            amount=item["amount"],
            notes=item.get("notes", ""),
        )
        db.add(budget_item)

    db.commit()
    db.refresh(trip)
    return trip
