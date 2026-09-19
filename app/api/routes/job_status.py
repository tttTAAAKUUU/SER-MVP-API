"""Job status and execution endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.booking import Booking, BookingStatus, BookingStatusUpdate
from app.models.user import User
from app.schemas.booking import BookingStatusUpdateRequest, BookingStatusUpdateResponse
from app.services.job_status_manager import job_status_manager
from app.services.notification_service import notification_service

router = APIRouter(prefix="/bookings", tags=["job-status"])


class StatusUpdateResponse(BaseModel):
    """Response for status update"""
    id: int
    booking_id: int
    previous_status: str
    new_status: str
    triggered_by_role: str
    triggered_by_user_id: int
    requires_confirmation: bool
    confirmed_by_user_id: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StatusHistoryResponse(BaseModel):
    """Status history entry"""
    id: int
    previous_status: str
    new_status: str
    triggered_by_role: str
    confirmed: bool
    confirmed_by_user_id: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    message: Optional[str] = None
    created_at: datetime


class PendingConfirmationResponse(BaseModel):
    """Pending confirmation response"""
    id: int
    booking_id: int
    previous_status: str
    new_status: str
    triggered_by_role: str
    triggered_by_user_id: int
    message: Optional[str] = None
    created_at: datetime


class ConfirmStatusRequest(BaseModel):
    """Confirm a status change"""
    status_update_id: int


@router.patch("/{booking_id}/status")
async def update_booking_status(
    booking_id: int,
    request: BookingStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    # current_user would be injected in real impl
):
    """
    Update booking status (provider or customer).
    
    Transitions:
    - Provider: CUSTOMER_SELECTED → ON_MY_WAY → AT_LOCATION → IN_PROGRESS → COMPLETED
    - Customer: Can confirm AT_LOCATION (arrival) and COMPLETED
    
    Some transitions require confirmation from other party.
    """
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # For now, mock: assume user_id = 1, role = PROVIDER
    # In real impl, would extract from auth
    user_id = 1
    triggered_by_role = request.triggered_by_role or "PROVIDER"
    
    # Parse new status
    try:
        new_status = BookingStatus[request.new_status]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {request.new_status}"
        )
    
    # Update status with validation
    try:
        status_update = await job_status_manager.update_status(
            db=db,
            booking=booking,
            new_status=new_status,
            triggered_by_role=triggered_by_role,
            triggered_by_user_id=user_id,
            message=request.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Notify other party if status requires confirmation
    if status_update.requires_confirmation == "true":
        other_user_id = booking.provider_id if triggered_by_role == "CUSTOMER" else booking.customer_id
        other_role = "CUSTOMER" if triggered_by_role == "PROVIDER" else "PROVIDER"
        
        if other_user_id:
            # Get user name for notification
            user = await db.execute(select(User).where(User.id == user_id))
            user_obj = user.scalar_one_or_none()
            user_name = f"{user_obj.first_name} {user_obj.last_name}" if user_obj else "Service provider"
            
            status_verb = "arrived at" if new_status == BookingStatus.AT_LOCATION else "completed"
            
            await notification_service.create_notification(
                db=db,
                user_id=other_user_id,
                notification_type="STATUS_UPDATE",
                title=f"Action needed: Confirm {status_verb}",
                message=f"{user_name} has {status_verb} your service. Please confirm.",
                booking_id=booking_id,
                data={
                    "booking_id": booking_id,
                    "status_update_id": status_update.id,
                    "status": new_status.value,
                }
            )
    else:
        # Notify other party of status change (no confirmation needed)
        other_user_id = booking.provider_id if triggered_by_role == "CUSTOMER" else booking.customer_id
        
        if other_user_id:
            await notification_service.create_notification(
                db=db,
                user_id=other_user_id,
                notification_type="STATUS_UPDATE",
                title=f"Job status: {new_status.value.replace('_', ' ')}",
                message=f"Your booking is now {new_status.value.replace('_', ' ').lower()}.",
                booking_id=booking_id,
                data={"booking_id": booking_id, "status": new_status.value}
            )
    
    return {
        "id": status_update.id,
        "booking_id": status_update.booking_id,
        "previous_status": status_update.previous_status.value,
        "new_status": status_update.new_status.value,
        "triggered_by_role": status_update.triggered_by_role,
        "triggered_by_user_id": status_update.triggered_by_user_id,
        "requires_confirmation": status_update.requires_confirmation == "true",
        "confirmed_by_user_id": status_update.confirmed_by_user_id,
        "confirmed_at": status_update.confirmed_at,
        "message": status_update.message,
        "created_at": status_update.created_at,
    }


@router.post("/{booking_id}/confirm-status")
async def confirm_status(
    booking_id: int,
    request: ConfirmStatusRequest,
    db: AsyncSession = Depends(get_db),
    # current_user would be injected
):
    """
    Confirm a pending status change (mutual confirmation).
    
    Example: Provider marks AT_LOCATION, customer confirms arrival.
    """
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # For now, mock: assume user_id = 1
    user_id = 1
    
    # Confirm status
    try:
        status_update = await job_status_manager.confirm_status(
            db=db,
            booking=booking,
            status_update_id=request.status_update_id,
            confirmed_by_user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Notify other party of confirmation
    other_user_id = booking.provider_id if booking.customer_id == user_id else booking.customer_id
    
    if other_user_id:
        other_role = "PROVIDER" if booking.customer_id == user_id else "CUSTOMER"
        confirmer_role = "CUSTOMER" if booking.customer_id == user_id else "PROVIDER"
        
        await notification_service.create_notification(
            db=db,
            user_id=other_user_id,
            notification_type="STATUS_UPDATE",
            title=f"{confirmer_role} confirmed: {status_update.new_status.value.replace('_', ' ')}",
            message=f"Status confirmed. Moving forward with service.",
            booking_id=booking_id,
            data={
                "booking_id": booking_id,
                "status": status_update.new_status.value,
                "confirmed": True
            }
        )
    
    return {
        "id": status_update.id,
        "booking_id": status_update.booking_id,
        "previous_status": status_update.previous_status.value,
        "new_status": status_update.new_status.value,
        "triggered_by_role": status_update.triggered_by_role,
        "triggered_by_user_id": status_update.triggered_by_user_id,
        "confirmed_by_user_id": status_update.confirmed_by_user_id,
        "confirmed_at": status_update.confirmed_at,
        "message": status_update.message,
        "created_at": status_update.created_at,
    }


@router.get("/{booking_id}/pending-confirmations", response_model=list[PendingConfirmationResponse])
async def get_pending_confirmations(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get pending confirmations for a booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    pending = await job_status_manager.get_pending_confirmations(db, booking_id)
    
    return [
        {
            "id": update.id,
            "booking_id": update.booking_id,
            "previous_status": update.previous_status.value,
            "new_status": update.new_status.value,
            "triggered_by_role": update.triggered_by_role,
            "triggered_by_user_id": update.triggered_by_user_id,
            "message": update.message,
            "created_at": update.created_at,
        }
        for update in pending
    ]


@router.get("/{booking_id}/status-history", response_model=list[StatusHistoryResponse])
async def get_status_history(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get complete status history for a booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    history = await job_status_manager.get_status_history(db, booking_id)
    
    return [
        {
            "id": update.id,
            "previous_status": update.previous_status.value,
            "new_status": update.new_status.value,
            "triggered_by_role": update.triggered_by_role,
            "confirmed": update.confirmed_at is not None,
            "confirmed_by_user_id": update.confirmed_by_user_id,
            "confirmed_at": update.confirmed_at,
            "message": update.message,
            "created_at": update.created_at,
        }
        for update in history
    ]
