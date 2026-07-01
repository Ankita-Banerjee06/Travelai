from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional


class TripPlanRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget: float
    currency: str = "USD"
    travelers: int = 1
    preferences: List[str] = []


class ActivityItem(BaseModel):
    time: str
    activity: str
    description: str
    estimated_cost: float
    location: Optional[str] = ""


class ItineraryDayResponse(BaseModel):
    day_number: int
    title: str
    activities: List[ActivityItem]
    estimated_cost: float

    class Config:
        from_attributes = True


class BudgetItemResponse(BaseModel):
    category: str
    amount: float
    notes: str = ""

    class Config:
        from_attributes = True


class TripResponse(BaseModel):
    id: int
    destination: str
    start_date: date
    end_date: date
    budget: float
    currency: str
    travelers: int
    preferences: List[str]
    created_at: datetime
    itinerary_days: List[ItineraryDayResponse] = []
    budget_breakdown: List[BudgetItemResponse] = []

    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    id: int
    destination: str
    start_date: date
    end_date: date
    budget: float
    currency: str
    travelers: int
    preferences: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OptimizeBudgetRequest(BaseModel):
    optimization_goal: str = "reduce_costs"  # reduce_costs, balance, luxury
