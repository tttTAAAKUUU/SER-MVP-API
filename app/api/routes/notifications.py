"""Notification endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkNotificationReadRequest,
)
from app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationListResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    # current_user would be injected in real impl
):
    """Get user's notifications"""
    # For now, assume user_id = 1 (mock)
    user_id = 1
    
    notifications = await notification_service.get_all_notifications(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    
    return notifications


@router.get("/unread", response_model=list[NotificationListResponse])
async def get_unread_notifications(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    # current_user would be injected in real impl
):
    """Get unread notifications"""
    # For now, assume user_id = 1 (mock)
    user_id = 1
    
    notifications = await notification_service.get_unread_notifications(
        db=db,
        user_id=user_id,
        limit=limit
    )
    
    return notifications


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific notification"""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    request: MarkNotificationReadRequest,
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read/unread"""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if request.is_read:
        return await notification_service.mark_as_read(db, notification_id)
    else:
        # Mark as unread
        notification.is_read = False
        notification.read_at = None
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification


@router.post("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    # current_user would be injected in real impl
):
    """Mark all notifications as read"""
    # For now, assume user_id = 1 (mock)
    user_id = 1
    
    count = await notification_service.mark_all_as_read(db, user_id)
    
    return {"message": "Notifications marked as read", "count": count}
