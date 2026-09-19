"""Provider schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ProviderProfileResponse(BaseModel):
    """Provider profile response"""
    id: int
    user_id: int
    business_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    verification_status: str
    years_of_experience: Optional[int] = None
    completed_jobs: int
    average_rating: str
    total_ratings: int

    class Config:
        from_attributes = True


class ProviderServiceResponse(BaseModel):
    """Provider's service offering"""
    id: int
    provider_id: int
    service_id: int
    price: Optional[str] = None
    pricing_options: Optional[Dict[str, Any]] = None
    price_range_min: Optional[str] = None
    price_range_max: Optional[str] = None
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class ProviderOnboardingStep2Request(BaseModel):
    """Provider onboarding step 2: Personal/business info"""
    business_name: Optional[str] = None
    years_of_experience: int
    bio: str


class ProviderOnboardingStep3Request(BaseModel):
    """Provider onboarding step 3: Select services"""
    service_ids: List[int]


class ProviderOnboardingStep4Request(BaseModel):
    """Provider onboarding step 4: Set pricing"""
    services: List[Dict[str, Any]]  # [{service_id: 1, price: "250"}, ...]


class ProviderOnboardingStep5Request(BaseModel):
    """Provider onboarding step 5: Service area"""
    latitude: str
    longitude: str
    radius_km: str = "15"


class ProviderOnboardingStep6Request(BaseModel):
    """Provider onboarding step 6: Availability"""
    schedule: Dict[str, Dict[str, str]]  # {"Monday": {"start": "09:00", "end": "17:00"}}


class ProviderOnboardingStep7Request(BaseModel):
    """Provider onboarding step 7: Upload documents"""
    document_type: str
    document_url: str


class ProviderAvailableJobsResponse(BaseModel):
    """Available job for provider"""
    id: int
    customer_id: int
    service_id: int
    booking_details: Dict[str, Any]
    requested_address: str
    requested_date: str
    requested_time: str
    estimated_price: str
    created_at: str

    class Config:
        from_attributes = True
