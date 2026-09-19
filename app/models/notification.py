"""Notification model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Enum
from datetime import datetime
import enum

from app.db.database import Base


class NotificationType(str, enum.Enum):
    """Notification types"""
    NEW_JOB = "NEW_JOB"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_REJECTED = "BID_REJECTED"
    STATUS_UPDATE = "STATUS_UPDATE"
    RATING_RECEIVED = "RATING_RECEIVED"


class Notification(Base):
    """Real-time notifications for users"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification type
    type = Column(String, nullable=False)  # e.g., "NEW_JOB", "BOOKING_ACCEPTED", "PROVIDER_EN_ROUTE", "VERIFICATION_APPROVED"
    
    # Related entity
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    provider_id = Column(Integer, nullable=True)
    
    # Message and data
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(JSON, default=dict)  # Additional context, e.g., {"booking_id": 123, "provider_name": "John"}
    
    # Read status
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Notification user={self.user_id} type={self.type}>"
