"""Service pricing range model for cosmetic and trainer services"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime

from app.db.database import Base


class ServicePricingRange(Base):
    """Recommended price ranges for provider-defined services (cosmetic, trainer)"""
    __tablename__ = "service_pricing_ranges"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    
    # Price range for this service
    min_price = Column(String, nullable=False)  # Minimum recommended bid price
    max_price = Column(String, nullable=False)  # Maximum recommended bid price
    
    # Additional context
    description = Column(Text, nullable=True)  # e.g., "Standard haircut, 30 minutes"
    category = Column(String, nullable=True)  # e.g., "HAIRCUT", "MASSAGE", "PERSONAL_TRAINING"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServicePricingRange service={self.service_id} min={self.min_price} max={self.max_price}>"
