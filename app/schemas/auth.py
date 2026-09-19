"""Authentication schemas"""
from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user data"""
    email: EmailStr
    phone: str
    first_name: str
    last_name: str


class CustomerSignupRequest(UserBase):
    """Customer signup request"""
    password: str


class ProviderSignupRequest(UserBase):
    """Provider signup request"""
    password: str
    business_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str
    role: Optional[str] = None  # Optional - will be determined from user record


class EmployeeRequest(BaseModel):
    """Employee information for business signup"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: str


class RegisterRequest(BaseModel):
    """Unified registration request for all roles"""
    email: EmailStr
    password: str
    password_confirm: Optional[str] = None
    role: str  # CUSTOMER, PROVIDER, or BUSINESS
    
    # Customer fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    
    # Provider fields
    bio: Optional[str] = None
    service_ids: Optional[list[int]] = None
    kyc_id_type: Optional[str] = None
    kyc_id_number: Optional[str] = None
    
    # Business fields
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    business_name: Optional[str] = None
    business_location: Optional[str] = None
    business_description: Optional[str] = None
    business_phone: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None
    kyc_business_registration: Optional[str] = None
    employees: Optional[list[EmployeeRequest]] = None


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    
    @computed_field  # type: ignore
    @property
    def full_name(self) -> str:
        """Computed full name"""
        return f"{self.first_name} {self.last_name}".strip()

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
