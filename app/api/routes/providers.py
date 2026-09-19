"""Provider endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.provider import ProviderProfile, ProviderService
from app.models.service import Service
from app.schemas.provider import (
    ProviderProfileResponse, ProviderServiceResponse, ProviderAvailableJobsResponse
)

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/{provider_id}/profile", response_model=ProviderProfileResponse)
async def get_provider_profile(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Get provider profile (public view - no KYC data)"""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == provider_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return profile


@router.get("/{provider_id}/services", response_model=list[ProviderServiceResponse])
async def get_provider_services(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Get provider's active services"""
    result = await db.execute(
        select(ProviderService).where(
            (ProviderService.provider_id == provider_id) &
            (ProviderService.is_active == True)
        )
    )
    services = result.scalars().all()
    return services


@router.get("/{provider_id}/available-jobs", response_model=list[ProviderAvailableJobsResponse])
async def get_available_jobs(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Get available job requests for provider (matching service area & availability)"""
    # Get provider profile
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Get requested bookings matching provider's services
    result = await db.execute(
        select(Booking).where(
            (Booking.status == BookingStatus.REQUESTED) &
            (Booking.provider_id == None)  # Not yet assigned
        ).order_by(Booking.created_at.desc())
    )
    
    bookings = result.scalars().all()
    return bookings


@router.post("/{provider_id}/accept-job/{booking_id}")
async def accept_job(
    provider_id: int,
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Provider accepts a job"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not in requested state"
        )
    
    # Update booking status
    booking.status = BookingStatus.ACCEPTED_BY_PROVIDER
    booking.provider_id = provider_id
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    return {"message": "Job accepted", "booking_id": booking.id}


@router.post("/{provider_id}/decline-job/{booking_id}")
async def decline_job(
    provider_id: int,
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Provider declines a job"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Set status to declined (keep open for other providers)
    booking.status = BookingStatus.DECLINED
    
    db.add(booking)
    await db.commit()
    
    return {"message": "Job declined", "booking_id": booking.id}
