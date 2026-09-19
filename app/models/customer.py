"""Customer profile model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime

from app.db.database import Base


class CustomerProfile(Base):
    """Customer profile with location and preferences"""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    latitude = Column(String, nullable=True)  # Will be float, using string for flexibility
    longitude = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    preferred_categories = Column(JSON, default=list)  # e.g., ["Beauty", "Cleaning"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CustomerProfile user_id={self.user_id}>"
