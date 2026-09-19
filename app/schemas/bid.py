"""Bid and bidding related schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProviderBidRequest(BaseModel):
    """Provider places a bid on a booking request"""
    bid_price: str  # The price the provider is bidding
    bid_message: Optional[str] = None  # Optional message from provider


class ProviderBidResponse(BaseModel):
    """Provider bid response"""
    id: int
    booking_id: int
    provider_id: int
    bid_price: str
    bid_message: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BidWithProviderResponse(BaseModel):
    """Bid with provider profile information for customer to review"""
    id: int
    booking_id: int
    provider_id: int
    bid_price: str
    bid_message: Optional[str] = None
    status: str
    created_at: datetime
    # Provider info
    provider_name: str
    provider_business_name: Optional[str] = None
    provider_rating: str
    provider_completed_jobs: int
    provider_verification_status: str
    provider_profile_image: Optional[str] = None
    provider_years_experience: Optional[int] = None

    class Config:
        from_attributes = True


class SelectBidRequest(BaseModel):
    """Customer selects a provider bid"""
    provider_id: int


class AvailableRequestResponse(BaseModel):
    """Available job request for provider to bid on"""
    id: int
    service_id: int
    service_name: str
    category_name: str
    booking_details: dict
    requested_address: str
    requested_date: str
    requested_time: str
    estimated_price: str  # Algo price for locked services
    customer_notes: Optional[str] = None
    distance_km: Optional[str] = None  # If available
    created_at: datetime

    class Config:
        from_attributes = True
