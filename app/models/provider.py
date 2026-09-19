"""Provider profile and services models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text, Boolean
from datetime import datetime
import enum

from app.db.database import Base


class VerificationStatus(str, enum.Enum):
    """Provider verification status"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class ProviderProfile(Base):
    """Provider profile with verification and service area"""
    __tablename__ = "provider_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String, nullable=True)
    portfolio_photos = Column(JSON, default=list)  # List of photo URLs and captions: [{"url": "...", "caption": "..."}, ...]
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    years_of_experience = Column(Integer, nullable=True)
    
    # Service area (geographic)
    service_area = Column(String, nullable=True)  # Simple area name, e.g. "Bryanston, Sandton"
    service_area_latitude = Column(String, nullable=True)  # Center point
    service_area_longitude = Column(String, nullable=True)
    service_area_radius_km = Column(String, default="15")  # Default 15km
    
    # Availability
    availability_schedule = Column(JSON, default=dict)  # e.g., {"Monday": {"start": "09:00", "end": "17:00"}}
    
    # Stats
    completed_jobs = Column(Integer, default=0)
    average_rating = Column(String, default="0.0")  # Stored as decimal string
    total_ratings = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProviderProfile user_id={self.user_id} status={self.verification_status}>"


class ProviderService(Base):
    """Service offerings by a provider with pricing"""
    __tablename__ = "provider_services"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("provider_profiles.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    
    # Provider's pricing for this service
    # For FIXED: just price
    # For DURATION-based: pricing_options as JSON
    # For SIZE-based: pricing_matrix as JSON
    price = Column(String, nullable=True)  # Base/fixed price
    pricing_options = Column(JSON, default=dict)  # For duration/customizable options
    price_range_min = Column(String, nullable=True)  # For PROVIDER_DEFINED with range
    price_range_max = Column(String, nullable=True)
    
    description = Column(Text, nullable=True)  # Provider's custom description
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProviderService provider_id={self.provider_id} service_id={self.service_id}>"


class ProviderVerification(Base):
    """KYC documents and verification tracking"""
    __tablename__ = "provider_verifications"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("provider_profiles.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False)  # e.g., "ID", "Certification", "Proof of Address"
    document_url = Column(String, nullable=False)  # Encrypted file path
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    admin_notes = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProviderVerification provider_id={self.provider_id} type={self.document_type}>"
