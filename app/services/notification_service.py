"""Service to create and manage notifications"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.models.notification import Notification, NotificationType


class NotificationService:
    """Handle notification creation and management"""
    
    async def create_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        booking_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            db: Database session
            user_id: User to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            booking_id: Related booking ID
            data: Additional data as JSON
            
        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            booking_id=booking_id,
            data=data or {},
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    async def notify_providers_of_new_job(
        self,
        db: AsyncSession,
        booking_id: int,
        provider_ids: List[int],
        service_name: str,
        location: str,
        estimated_price: str
    ) -> List[Notification]:
        """
        Notify multiple providers of a new job request.
        
        Args:
            db: Database session
            booking_id: Booking ID
            provider_ids: List of provider user IDs to notify
            service_name: Name of service
            location: Service location
            estimated_price: Estimated price
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        title = f"New {service_name} request"
        message = f"A customer is looking for {service_name} at {location}"
        data = {
            "booking_id": booking_id,
            "service_name": service_name,
            "location": location,
            "estimated_price": estimated_price,
        }
        
        for provider_id in provider_ids:
            notif = await self.create_notification(
                db=db,
                user_id=provider_id,
                notification_type="NEW_JOB",
                title=title,
                message=message,
                booking_id=booking_id,
                data=data
            )
            notifications.append(notif)
        
        return notifications
    
    async def notify_bid_accepted(
        self,
        db: AsyncSession,
        provider_id: int,
        booking_id: int,
        customer_name: str,
        service_name: str
    ) -> Notification:
        """Notify provider their bid was accepted"""
        return await self.create_notification(
            db=db,
            user_id=provider_id,
            notification_type="BID_ACCEPTED",
            title="Bid accepted!",
            message=f"{customer_name} accepted your bid for {service_name}",
            booking_id=booking_id,
            data={"booking_id": booking_id}
        )
    
    async def notify_bid_rejected(
        self,
        db: AsyncSession,
        provider_id: int,
        booking_id: int,
        service_name: str
    ) -> Notification:
        """Notify provider their bid was rejected"""
        return await self.create_notification(
            db=db,
            user_id=provider_id,
            notification_type="BID_REJECTED",
            title="Bid not selected",
            message=f"The customer selected another provider for {service_name}",
            booking_id=booking_id,
            data={"booking_id": booking_id}
        )
    
    async def get_unread_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20
    ) -> List[Notification]:
        """Get unread notifications for a user"""
        result = await db.execute(
            select(Notification)
            .where(
                (Notification.user_id == user_id) &
                (Notification.is_read == False)
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_all_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get all notifications for a user"""
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: int
    ) -> Notification:
        """Mark notification as read"""
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
        
        return notification
    
    async def mark_all_as_read(
        self,
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Mark all notifications as read for a user"""
        result = await db.execute(
            select(Notification)
            .where(
                (Notification.user_id == user_id) &
                (Notification.is_read == False)
            )
        )
        notifications = result.scalars().all()
        
        for notif in notifications:
            notif.is_read = True
            notif.read_at = datetime.utcnow()
        
        await db.commit()
        return len(notifications)


# Singleton instance
notification_service = NotificationService()
