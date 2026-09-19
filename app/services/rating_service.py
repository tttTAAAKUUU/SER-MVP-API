"""Rating and review management"""
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.rating import Rating
from app.models.booking import Booking, BookingStatus
from app.models.provider import ProviderProfile
from app.models.user import User


class RatingService:
    """Handle rating creation and provider stats updates"""
    
    async def create_rating(
        self,
        db: AsyncSession,
        booking_id: int,
        customer_id: int,
        provider_id: int,
        rating: int,
        comment: Optional[str] = None,
    ) -> Rating:
        """
        Create a rating for a completed booking.
        
        Args:
            db: Database session
            booking_id: Booking ID
            customer_id: Customer who is rating
            provider_id: Provider being rated
            rating: Rating value (1-5)
            comment: Optional review comment
            
        Returns:
            Created Rating
        """
        # Validate rating
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        # Check booking exists and is completed
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.COMPLETED:
            raise ValueError("Can only rate completed bookings")
        
        # Check rating doesn't already exist
        result = await db.execute(
            select(Rating).where(Rating.booking_id == booking_id)
        )
        existing_rating = result.scalar_one_or_none()
        
        if existing_rating:
            raise ValueError("This booking has already been rated")
        
        # Create rating
        new_rating = Rating(
            booking_id=booking_id,
            customer_id=customer_id,
            provider_id=provider_id,
            rating=rating,
            comment=comment,
        )
        
        db.add(new_rating)
        await db.commit()
        
        # Update provider stats
        await self.update_provider_stats(db, provider_id)
        
        await db.refresh(new_rating)
        return new_rating
    
    async def update_provider_stats(self, db: AsyncSession, provider_id: int) -> None:
        """
        Recalculate provider's average rating and total ratings.
        
        Args:
            db: Database session
            provider_id: Provider to update
        """
        # Get all ratings for provider
        result = await db.execute(
            select(func.avg(Rating.rating).label("avg_rating"), func.count(Rating.id).label("total"))
            .where(Rating.provider_id == provider_id)
        )
        row = result.first()
        
        avg_rating = row[0] if row[0] else Decimal("0.0")
        total_ratings = row[1] if row[1] else 0
        
        # Update provider profile
        result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.provider_id == provider_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            profile.average_rating = str(Decimal(str(avg_rating)).quantize(Decimal("0.1")))
            profile.total_ratings = total_ratings
            db.add(profile)
            await db.commit()
    
    async def get_provider_ratings(
        self,
        db: AsyncSession,
        provider_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Rating]:
        """
        Get ratings for a provider.
        
        Args:
            db: Database session
            provider_id: Provider ID
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of ratings
        """
        result = await db.execute(
            select(Rating)
            .where(Rating.provider_id == provider_id)
            .order_by(Rating.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_booking_rating(
        self,
        db: AsyncSession,
        booking_id: int
    ) -> Optional[Rating]:
        """
        Get rating for a specific booking.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            Rating if exists, None otherwise
        """
        result = await db.execute(
            select(Rating).where(Rating.booking_id == booking_id)
        )
        return result.scalar_one_or_none()


# Singleton instance
rating_service = RatingService()
