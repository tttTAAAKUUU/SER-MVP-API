"""Notification schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    booking_id: Optional[int] = None
    type: str
    title: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications for user"""
    id: int
    booking_id: Optional[int] = None
    type: str
    title: str
    message: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarkNotificationReadRequest(BaseModel):
    """Mark notification as read"""
    is_read: bool = True
