"""Rating and review endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.rating import Rating
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.rating import RatingCreateRequest, RatingResponse
from app.services.rating_service import rating_service
from app.services.notification_service import notification_service

router = APIRouter(prefix="/bookings", tags=["ratings"])


@router.post("/{booking_id}/rate", response_model=RatingResponse)
async def create_rating(
    booking_id: int,
    request: RatingCreateRequest,
    db: AsyncSession = Depends(get_db),
    # current_user would be injected
):
    """
    Rate a completed booking.
    
    Only the customer can rate after the booking is COMPLETED.
    """
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check booking is completed
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed bookings"
        )
    
    # For now, mock: assume customer_id = 1
    customer_id = 1
    
    # Verify customer is the one rating
    if booking.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the customer can rate this booking"
        )
    
    # Create rating
    try:
        rating = await rating_service.create_rating(
            db=db,
            booking_id=booking_id,
            customer_id=customer_id,
            provider_id=booking.provider_id,
            rating=request.rating,
            comment=request.comment,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Notify provider of rating
    if booking.provider_id:
        provider = await db.execute(select(User).where(User.id == booking.provider_id))
        provider_user = provider.scalar_one_or_none()
        customer = await db.execute(select(User).where(User.id == customer_id))
        customer_user = customer.scalar_one_or_none()
        
        customer_name = f"{customer_user.first_name} {customer_user.last_name}" if customer_user else "Customer"
        
        await notification_service.create_notification(
            db=db,
            user_id=booking.provider_id,
            notification_type="RATING_RECEIVED",
            title=f"You received a {request.rating}-star rating",
            message=f"{customer_name} rated your service: {request.comment or 'No comment'}",
            booking_id=booking_id,
            data={
                "booking_id": booking_id,
                "rating": request.rating,
                "comment": request.comment,
            }
        )
    
    return rating


@router.get("/{booking_id}/rating", response_model=RatingResponse)
async def get_booking_rating(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get rating for a specific booking"""
    rating = await rating_service.get_booking_rating(db, booking_id)
    
    if not rating:
        raise HTTPException(
            status_code=404,
            detail="No rating found for this booking"
        )
    
    return rating


@router.get("/provider/{provider_id}/ratings", response_model=list[RatingResponse])
async def get_provider_ratings(
    provider_id: int,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get all ratings for a provider"""
    # Verify provider exists
    result = await db.execute(select(User).where(User.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    ratings = await rating_service.get_provider_ratings(
        db=db,
        provider_id=provider_id,
        limit=limit,
        offset=offset
    )
    
    return ratings


class RatingSummary(BaseModel):
    """Summary of provider's ratings"""
    average_rating: str
    total_ratings: int
    five_star: int
    four_star: int
    three_star: int
    two_star: int
    one_star: int
    
    class Config:
        from_attributes = True


@router.get("/provider/{provider_id}/rating-summary")
async def get_rating_summary(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get summary of provider's ratings"""
    # Verify provider exists
    result = await db.execute(select(User).where(User.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Get all ratings
    from sqlalchemy import and_
    result = await db.execute(
        select(Rating).where(Rating.provider_id == provider_id)
    )
    ratings = result.scalars().all()
    
    # Count by star
    five_star = sum(1 for r in ratings if r.rating == 5)
    four_star = sum(1 for r in ratings if r.rating == 4)
    three_star = sum(1 for r in ratings if r.rating == 3)
    two_star = sum(1 for r in ratings if r.rating == 2)
    one_star = sum(1 for r in ratings if r.rating == 1)
    
    # Get provider profile for average
    from app.models.provider import ProviderProfile
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.provider_id == provider_id)
    )
    profile = result.scalar_one_or_none()
    
    average_rating = profile.average_rating if profile else "0.0"
    total_ratings = len(ratings)
    
    return {
        "average_rating": average_rating,
        "total_ratings": total_ratings,
        "five_star": five_star,
        "four_star": four_star,
        "three_star": three_star,
        "two_star": two_star,
        "one_star": one_star,
    }
