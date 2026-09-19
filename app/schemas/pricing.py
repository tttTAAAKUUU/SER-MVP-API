"""Service pricing range schemas"""
from pydantic import BaseModel
from typing import Optional


class ServicePricingRangeResponse(BaseModel):
    """Service pricing range response"""
    id: int
    service_id: int
    min_price: str
    max_price: str
    description: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class ServicePricingRangeRequest(BaseModel):
    """Create/update service pricing range"""
    service_id: int
    min_price: str
    max_price: str
    description: Optional[str] = None
    category: Optional[str] = None
