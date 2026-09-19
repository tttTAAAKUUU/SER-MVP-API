"""Booking endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import Optional

from app.db.database import get_db
from app.models.booking import Booking, BookingStatus, BidStatus, BookingStatusUpdate
from app.models.service import Service, ServiceCategory
from app.models.user import User
from app.schemas.booking import (
    BookingCreateRequest, BookingResponse, BookingListResponse,
    BookingStatusUpdateRequest, BookingStatusUpdateResponse
)
from app.services.pricing_engine import pricing_engine
from app.services.request_matching import request_matcher
from app.services.notification_service import notification_service
from app.core.security import decode_token

router = APIRouter(prefix="/bookings", tags=["bookings"])


async def get_current_customer(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    """Extract current customer from Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/", response_model=BookingResponse)
async def create_booking(
    request: BookingCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer)
):
    """Create a new booking request"""
    # Use the authenticated customer's ID
    customer_id = current_user.id
    
    # Get service for pricing type
    result = await db.execute(select(Service).where(Service.id == request.service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get category name for context
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == request.category_id)
    )
    category = result.scalar_one_or_none()
    category_name = category.name if category else None
    
    # Calculate price using pricing engine
    pricing_result = pricing_engine.calculate_price(
        pricing_type=service.pricing_type,
        booking_details=request.booking_details,
        category_name=category_name,
    )
    
    # Create booking with bidding status
    booking = Booking(
        customer_id=customer_id,
        service_id=request.service_id,
        category_id=request.category_id,
        booking_details=request.booking_details,
        requested_latitude=request.requested_latitude,
        requested_longitude=request.requested_longitude,
        requested_address=request.requested_address,
        requested_date=request.requested_date,
        requested_time=request.requested_time,
        estimated_price=str(pricing_result.total_to_pay),
        commission_amount=str(pricing_result.commission_amount),
        provider_gross=str(pricing_result.provider_gross),
        status=BookingStatus.REQUESTED,
        bid_status=BidStatus.OPEN_FOR_BIDS,  # NEW: Set bidding status
        customer_notes=request.customer_notes,
    )
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    # Distribute to matching providers (NEW)
    matching_providers = await request_matcher.find_matching_providers(booking, db)
    
    if matching_providers:
        provider_ids = [p["provider_id"] for p in matching_providers]
        await notification_service.notify_providers_of_new_job(
            db=db,
            booking_id=booking.id,
            provider_ids=provider_ids,
            service_name=service.name if service else "Service",
            location=booking.requested_address or "Specified location",
            estimated_price=booking.estimated_price,
        )
    
    return booking


@router.get("/", response_model=list[BookingListResponse])
async def list_customer_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer)
):
    """List customer's bookings"""
    # Get bookings for the authenticated customer
    result = await db.execute(
        select(Booking).where(Booking.customer_id == current_user.id).order_by(Booking.created_at.desc())
    )
    bookings = result.scalars().all()
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    """Get booking details"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@router.patch("/{booking_id}/status", response_model=BookingStatusUpdateResponse)
async def update_booking_status(
    booking_id: int,
    request: BookingStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    # current_user would be injected here
):
    """Update booking status"""
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Record status update
    previous_status = booking.status
    booking.status = BookingStatus[request.new_status]
    
    status_update = BookingStatusUpdate(
        booking_id=booking_id,
        previous_status=previous_status,
        new_status=BookingStatus[request.new_status],
        triggered_by_role="PROVIDER",  # Mock - would be actual role
        triggered_by_user_id=booking.provider_id or 1,
        requires_confirmation=str(request.requires_confirmation or False),
        message=request.message,
    )
    
    db.add(status_update)
    await db.commit()
    await db.refresh(booking)
    
    return status_update
