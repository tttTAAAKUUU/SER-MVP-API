"""Rating and review model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime

from app.db.database import Base


class Rating(Base):
    """Customer ratings and reviews for completed bookings"""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Rating (1-5 stars)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Rating booking={self.booking_id} rating={self.rating}>"
