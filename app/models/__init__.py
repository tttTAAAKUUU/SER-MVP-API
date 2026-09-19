"""Models module - import all models to register with SQLAlchemy Base"""
from app.models.user import User
from app.models.service import Service, ServiceCategory, ServiceSubcategory, PricingType
from app.models.booking import Booking, BookingStatus, BookingStatusUpdate
from app.models.provider import ProviderProfile, ProviderService, VerificationStatus
from app.models.customer import CustomerProfile
from app.models.bid import ProviderBid, BidStatus
from app.models.rating import Rating
from app.models.pricing import ServicePricingRange
from app.models.notification import Notification, NotificationType

__all__ = [
    "User",
    "Service",
    "ServiceCategory",
    "ServiceSubcategory",
    "PricingType",
    "Booking",
    "BookingStatus",
    "BookingStatusUpdate",
    "ProviderProfile",
    "ProviderService",
    "VerificationStatus",
    "CustomerProfile",
    "ProviderBid",
    "BidStatus",
    "Rating",
    "ServicePricingRange",
    "Notification",
    "NotificationType",
]
