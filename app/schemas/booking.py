"""Booking schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class BookingCreateRequest(BaseModel):
    """Create booking request"""
    service_id: int
    category_id: int
    booking_details: Dict[str, Any]  # Service-specific details
    requested_latitude: Optional[str] = None
    requested_longitude: Optional[str] = None
    requested_address: str
    requested_date: datetime
    requested_time: str  # e.g., "10:00"
    customer_notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Booking response"""
    id: int
    customer_id: int
    provider_id: Optional[int] = None
    service_id: int
    category_id: int
    booking_details: Dict[str, Any]
    requested_address: str
    requested_date: datetime
    requested_time: str
    estimated_price: str
    commission_amount: str
    provider_gross: str
    final_price: Optional[str] = None
    status: str
    bid_status: Optional[str] = None
    customer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Booking list response"""
    id: int
    status: str
    bid_status: Optional[str] = None
    service_id: int
    requested_date: datetime
    requested_time: str
    requested_address: str
    estimated_price: str
    final_price: Optional[str] = None
    provider_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdateRequest(BaseModel):
    """Update booking status"""
    new_status: str
    triggered_by_role: str = "PROVIDER"  # "PROVIDER" or "CUSTOMER"
    message: Optional[str] = None


class BookingStatusUpdateResponse(BaseModel):
    """Status update response"""
    id: int
    booking_id: int
    previous_status: str
    new_status: str
    triggered_by_role: str
    created_at: datetime

    class Config:
        from_attributes = True
