"""Booking and booking status tracking models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text
from datetime import datetime
import enum

from app.db.database import Base


class BookingStatus(str, enum.Enum):
    """Booking and job status"""
    REQUESTED = "REQUESTED"  # Customer submits request, waiting for providers to bid
    ACCEPTED_BY_PROVIDER = "ACCEPTED_BY_PROVIDER"  # Provider accepted (deprecated in bidding model)
    CUSTOMER_SELECTED = "CUSTOMER_SELECTED"  # Customer selected provider from bids
    ON_MY_WAY = "ON_MY_WAY"  # Provider is en route
    AT_LOCATION = "AT_LOCATION"  # Provider at customer location
    IN_PROGRESS = "IN_PROGRESS"  # Service started (customer confirmed)
    COMPLETED = "COMPLETED"  # Service complete (customer confirmed)
    CANCELLED = "CANCELLED"
    DECLINED = "DECLINED"  # Provider declined


class BidStatus(str, enum.Enum):
    """Booking bidding status"""
    OPEN_FOR_BIDS = "OPEN_FOR_BIDS"  # Accepting provider bids
    BIDS_RECEIVED = "BIDS_RECEIVED"  # Has received bids from providers
    PROVIDER_SELECTED = "PROVIDER_SELECTED"  # Customer selected a provider
    IN_PROGRESS = "IN_PROGRESS"  # Service in progress (after provider selected)
    COMPLETED = "COMPLETED"  # Service completed
    EXPIRED = "EXPIRED"  # Bid window expired with no selection


class Booking(Base):
    """Customer booking request and job tracking"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Assigned after customer selects
    
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=False, index=True)
    
    # Booking details - service-specific request fields stored as JSON
    # e.g., for beauty: {service_type: "Haircut", hair_length: "long"}
    # e.g., for cleaning: {bedrooms: 3, bathrooms: 2, clean_type: "deep", add_ons: ["laundry"]}
    # e.g., for car wash: {vehicle_type: "SUV", package: "premium"}
    booking_details = Column(JSON, nullable=False)
    
    # Location and timing
    requested_latitude = Column(String, nullable=True)
    requested_longitude = Column(String, nullable=True)
    requested_address = Column(String, nullable=True)
    requested_date = Column(DateTime, nullable=False)  # Date of service
    requested_time = Column(String, nullable=False)  # Time slot, e.g., "10:00"
    
    # Pricing
    estimated_price = Column(String, nullable=False)  # Total price (calculated or provided estimate)
    commission_amount = Column(String, nullable=False)  # SIR commission (18% of final_price after bid selection)
    provider_gross = Column(String, nullable=False)  # Provider earnings
    commission_percent = Column(String, default="18")  # For flexibility
    final_price = Column(String, nullable=True)  # Final price after provider selected (for bid services)
    
    # Status tracking - old status field (backward compat)
    status = Column(Enum(BookingStatus), default=BookingStatus.REQUESTED, index=True)
    
    # Bidding status
    bid_status = Column(Enum(BidStatus), default=BidStatus.OPEN_FOR_BIDS, index=True)
    
    # Bid expiry
    bid_expires_at = Column(DateTime, nullable=True)  # Time when bidding window closes
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Booking id={self.id} status={self.status}>"


class BookingStatusUpdate(Base):
    """Granular status updates for real-time tracking"""
    __tablename__ = "booking_status_updates"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    
    # Status change
    previous_status = Column(Enum(BookingStatus), nullable=False)
    new_status = Column(Enum(BookingStatus), nullable=False)
    
    # Who initiated (provider or customer)
    triggered_by_role = Column(String, nullable=False)  # "PROVIDER" or "CUSTOMER"
    triggered_by_user_id = Column(Integer, nullable=False)
    
    # Optional confirmation from the other party
    # e.g., provider marks "IN_PROGRESS", customer must confirm start
    requires_confirmation = Column(String, default="false")
    confirmed_by_user_id = Column(Integer, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    
    # Message/reason
    message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<BookingStatusUpdate booking={self.booking_id} {self.previous_status}->{self.new_status}>"
