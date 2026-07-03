from sqlalchemy.orm import Session
from app.models.trip import Trip, Itinerary, BudgetBreakdown


def _build_itinerary_rows(trip_id: int, itinerary: list) -> list[Itinerary]:
    """Convert AI-generated itinerary entries into Itinerary rows, skipping
    any malformed entries instead of crashing the whole request."""
    rows = []
    if not isinstance(itinerary, list):
        return rows

    next_day_number = 1
    for day in itinerary:
        if not isinstance(day, dict):
            continue

        day_number = day.get("day_number")
        if not isinstance(day_number, int):
            day_number = next_day_number
        next_day_number = day_number + 1

        title = day.get("title") or f"Day {day_number}"

        activities = day.get("activities", [])
        if not isinstance(activities, list):
            activities = []
        activities = [a for a in activities if isinstance(a, dict)]

        estimated_cost = day.get("estimated_cost", 0.0)
        if not isinstance(estimated_cost, (int, float)):
            estimated_cost = 0.0

        rows.append(Itinerary(
            trip_id=trip_id,
            day_number=day_number,
            title=title,
            activities=activities,
            estimated_cost=estimated_cost,
        ))
    return rows


def _build_budget_rows(trip_id: int, budget_breakdown: list) -> list[BudgetBreakdown]:
    """Convert AI-generated budget entries into BudgetBreakdown rows,
    skipping any malformed entries instead of crashing the whole request."""
    rows = []
    if not isinstance(budget_breakdown, list):
        return rows

    for item in budget_breakdown:
        if not isinstance(item, dict):
            continue

        category = item.get("category")
        if not category:
            continue

        amount = item.get("amount", 0.0)
        if not isinstance(amount, (int, float)):
            amount = 0.0

        rows.append(BudgetBreakdown(
            trip_id=trip_id,
            category=category,
            amount=amount,
            notes=item.get("notes", "") or "",
        ))
    return rows


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

    for itinerary_day in _build_itinerary_rows(trip.id, ai_response.get("itinerary", [])):
        db.add(itinerary_day)

    for budget_item in _build_budget_rows(trip.id, ai_response.get("budget_breakdown", [])):
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

    for itinerary_day in _build_itinerary_rows(trip.id, ai_response.get("itinerary", [])):
        db.add(itinerary_day)

    for budget_item in _build_budget_rows(trip.id, ai_response.get("budget_breakdown", [])):
        db.add(budget_item)

    db.commit()
    db.refresh(trip)
    return trip
