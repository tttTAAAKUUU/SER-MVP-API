"""Service and pricing schemas"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ServiceCategoryResponse(BaseModel):
    """Service category response"""
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class ServiceResponse(BaseModel):
    """Service response"""
    id: int
    category_id: int
    name: str
    description: Optional[str] = None
    pricing_type: str
    default_price: Optional[str] = None

    class Config:
        from_attributes = True


class ServicePricingRuleResponse(BaseModel):
    """Service pricing rule response"""
    id: int
    service_id: int
    rule_name: str
    base_price: str
    rule_conditions: Optional[Dict[str, Any]] = None
    adjustments: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
