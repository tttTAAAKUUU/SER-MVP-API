"""Rating schemas"""
from pydantic import BaseModel
from typing import Optional


class RatingCreateRequest(BaseModel):
    """Create rating/review"""
    booking_id: int
    rating: int  # 1-5
    comment: Optional[str] = None


class RatingResponse(BaseModel):
    """Rating response"""
    id: int
    booking_id: int
    customer_id: int
    provider_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True
