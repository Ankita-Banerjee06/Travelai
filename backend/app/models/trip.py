from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    travelers = Column(Integer, default=1)
    preferences = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="trips")
    itinerary_days = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")
    budget_breakdown = relationship("BudgetBreakdown", back_populates="trip", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    activities = Column(JSON, default=list)
    estimated_cost = Column(Float, default=0.0)

    trip = relationship("Trip", back_populates="itinerary_days")


class BudgetBreakdown(Base):
    __tablename__ = "budget_breakdowns"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(String(500), default="")

    trip = relationship("Trip", back_populates="budget_breakdown")
