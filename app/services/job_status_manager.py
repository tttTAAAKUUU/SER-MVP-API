"""Job status management and tracking"""
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.models.booking import Booking, BookingStatus, BookingStatusUpdate


class JobStatusManager:
    """Manage job status transitions with validation and confirmation flow"""
    
    # Valid status transitions per role
    PROVIDER_TRANSITIONS = {
        BookingStatus.CUSTOMER_SELECTED: [BookingStatus.ON_MY_WAY],
        BookingStatus.ON_MY_WAY: [BookingStatus.AT_LOCATION],
        BookingStatus.AT_LOCATION: [BookingStatus.IN_PROGRESS],
        BookingStatus.IN_PROGRESS: [BookingStatus.COMPLETED],
    }
    
    CUSTOMER_TRANSITIONS = {
        BookingStatus.ON_MY_WAY: [BookingStatus.ON_MY_WAY],  # Can acknowledge
        BookingStatus.AT_LOCATION: [BookingStatus.IN_PROGRESS],  # Confirm arrival
        BookingStatus.IN_PROGRESS: [BookingStatus.COMPLETED],  # Confirm completion
    }
    
    # Transitions that require confirmation from other party
    REQUIRE_CONFIRMATION = {
        BookingStatus.AT_LOCATION,  # Provider says arrived, customer must confirm
        BookingStatus.COMPLETED,  # Provider marks done, customer must confirm
    }
    
    async def is_valid_transition(
        self,
        booking: Booking,
        new_status: BookingStatus,
        triggered_by_role: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if status transition is allowed.
        
        Args:
            booking: Current booking
            new_status: Desired new status
            triggered_by_role: "PROVIDER" or "CUSTOMER"
            
        Returns:
            (is_valid, error_message)
        """
        current_status = booking.status
        
        # Get valid transitions for this role
        if triggered_by_role == "PROVIDER":
            valid_next = self.PROVIDER_TRANSITIONS.get(current_status, [])
        elif triggered_by_role == "CUSTOMER":
            valid_next = self.CUSTOMER_TRANSITIONS.get(current_status, [])
        else:
            return False, "Invalid role"
        
        # Check if transition is valid
        if new_status not in valid_next:
            return False, f"Cannot transition from {current_status.value} to {new_status.value} as {triggered_by_role}"
        
        return True, None
    
    async def update_status(
        self,
        db: AsyncSession,
        booking: Booking,
        new_status: BookingStatus,
        triggered_by_role: str,
        triggered_by_user_id: int,
        message: Optional[str] = None,
    ) -> BookingStatusUpdate:
        """
        Update booking status with validation.
        
        Args:
            db: Database session
            booking: Booking to update
            new_status: New status
            triggered_by_role: "PROVIDER" or "CUSTOMER"
            triggered_by_user_id: User ID making the change
            message: Optional message/reason
            
        Returns:
            Created BookingStatusUpdate record
        """
        # Validate transition
        is_valid, error = await self.is_valid_transition(booking, new_status, triggered_by_role)
        
        if not is_valid:
            raise ValueError(error)
        
        # Record previous status
        previous_status = booking.status
        
        # Determine if confirmation is needed
        requires_confirmation = new_status in self.REQUIRE_CONFIRMATION
        
        # Create status update record
        status_update = BookingStatusUpdate(
            booking_id=booking.id,
            previous_status=previous_status,
            new_status=new_status,
            triggered_by_role=triggered_by_role,
            triggered_by_user_id=triggered_by_user_id,
            requires_confirmation="true" if requires_confirmation else "false",
            message=message,
        )
        
        db.add(status_update)
        
        # If no confirmation needed, update booking status immediately
        if not requires_confirmation:
            booking.status = new_status
        # Else: stay in current status until other party confirms
        
        db.add(booking)
        await db.commit()
        await db.refresh(status_update)
        
        return status_update
    
    async def confirm_status(
        self,
        db: AsyncSession,
        booking: Booking,
        status_update_id: int,
        confirmed_by_user_id: int,
    ) -> BookingStatusUpdate:
        """
        Confirm a pending status change.
        
        Args:
            db: Database session
            booking: Booking being confirmed
            status_update_id: Status update record ID
            confirmed_by_user_id: User ID confirming
            
        Returns:
            Updated BookingStatusUpdate record
        """
        # Get the status update
        result = await db.execute(
            select(BookingStatusUpdate).where(BookingStatusUpdate.id == status_update_id)
        )
        status_update = result.scalar_one_or_none()
        
        if not status_update:
            raise ValueError("Status update not found")
        
        # Verify this update requires confirmation
        if status_update.requires_confirmation != "true":
            raise ValueError("This status update does not require confirmation")
        
        # Mark as confirmed
        status_update.confirmed_by_user_id = confirmed_by_user_id
        status_update.confirmed_at = datetime.utcnow()
        
        # Update booking to the new status
        booking.status = status_update.new_status
        booking.updated_at = datetime.utcnow()
        
        db.add(status_update)
        db.add(booking)
        await db.commit()
        await db.refresh(status_update)
        
        return status_update
    
    async def get_pending_confirmations(
        self,
        db: AsyncSession,
        booking_id: int,
    ) -> List[BookingStatusUpdate]:
        """
        Get pending status changes awaiting confirmation.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            List of pending status updates
        """
        result = await db.execute(
            select(BookingStatusUpdate).where(
                (BookingStatusUpdate.booking_id == booking_id) &
                (BookingStatusUpdate.requires_confirmation == "true") &
                (BookingStatusUpdate.confirmed_at == None)
            ).order_by(BookingStatusUpdate.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_status_history(
        self,
        db: AsyncSession,
        booking_id: int,
    ) -> List[BookingStatusUpdate]:
        """
        Get complete status history for a booking.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            List of all status updates in order
        """
        result = await db.execute(
            select(BookingStatusUpdate).where(
                BookingStatusUpdate.booking_id == booking_id
            ).order_by(BookingStatusUpdate.created_at.asc())
        )
        return result.scalars().all()


# Singleton instance
job_status_manager = JobStatusManager()
