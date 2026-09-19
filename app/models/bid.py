"""Provider bid model for request-based bidding"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from datetime import datetime
import enum

from app.db.database import Base


class BidStatus(str, enum.Enum):
    """Provider bid status"""
    PENDING = "PENDING"  # Bid submitted, awaiting customer review
    ACCEPTED = "ACCEPTED"  # Customer accepted this bid
    REJECTED = "REJECTED"  # Customer rejected this bid
    WITHDRAWN = "WITHDRAWN"  # Provider withdrew the bid


class ProviderBid(Base):
    """Provider bid on a booking request"""
    __tablename__ = "provider_bids"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Bid details
    bid_price = Column(String, nullable=False)  # Bid amount (can differ from estimated for cosmetic/trainer)
    bid_message = Column(Text, nullable=True)  # Optional message from provider
    
    # Status
    status = Column(Enum(BidStatus), default=BidStatus.PENDING, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProviderBid booking={self.booking_id} provider={self.provider_id} status={self.status}>"
