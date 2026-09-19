"""Service Provider endpoints - Dashboard API"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.provider import ProviderProfile, ProviderService
from app.models.booking import Booking, BookingStatus, BidStatus
from app.models.bid import ProviderBid
from app.models.rating import Rating
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/service-providers", tags=["service-providers"])


# ============ SCHEMAS ============
class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    service_area: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    service_name: str
    client_name: str
    date_iso: str
    price: float
    location: str
    status: str

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    id: int
    service_name: str
    client_name: str
    rating: float
    price: float
    date: str

    class Config:
        from_attributes = True


# ============ DEPENDENCIES ============
async def get_current_provider(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    """Extract current provider from Bearer token"""
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

    # Verify user exists and is a provider
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can access this endpoint"
        )

    return user


# ============ ROUTES ============
@router.post("/login", response_model=TokenResponse)
async def provider_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Provider login endpoint"""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not a provider account"
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.get("/profile", response_model=dict)
async def get_provider_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Get provider's profile"""
    # Get provider profile
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider_profile = result.scalar_one_or_none()

    # Get provider services
    result = await db.execute(
        select(ProviderService).where(
            (ProviderService.provider_id == current_user.id) &
            (ProviderService.is_active == True)
        )
    )
    services = result.scalars().all()

    # Get ratings
    result = await db.execute(
        select(Rating).where(Rating.provider_id == current_user.id)
    )
    ratings = result.scalars().all()
    avg_rating = (
        sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    )

    return {
        "data": {
            "id": current_user.id,
            "name": f"{current_user.first_name} {current_user.last_name}",
            "email": current_user.email,
            "phone": current_user.phone,
            "profile": {
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone": current_user.phone,
                "bio": provider_profile.bio if provider_profile else None,
                "service_area": provider_profile.service_area if provider_profile else None,
                "rating": float(avg_rating),
                "total_jobs": len(ratings),
            },
            "services": [
                {
                    "id": s.id,
                    "name": s.service.name if s.service else "Unknown",
                    "is_active": s.is_active,
                }
                for s in services
            ],
        }
    }


@router.put("/profile", response_model=dict)
async def update_provider_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Update provider profile"""
    # Update user fields
    if profile_data.first_name:
        current_user.first_name = profile_data.first_name
    if profile_data.last_name:
        current_user.last_name = profile_data.last_name
    if profile_data.phone:
        current_user.phone = profile_data.phone

    # Update provider profile
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider_profile = result.scalar_one_or_none()

    if not provider_profile:
        provider_profile = ProviderProfile(user_id=current_user.id)
        db.add(provider_profile)

    if profile_data.bio:
        provider_profile.bio = profile_data.bio
    if profile_data.service_area:
        provider_profile.service_area = profile_data.service_area

    db.add(current_user)
    db.add(provider_profile)
    await db.commit()

    return {"message": "Profile updated successfully"}


@router.post("/logout", response_model=dict)
async def provider_logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Provider logout endpoint"""
    # Token is invalidated on client side; this is just for logging purposes
    return {"message": "Logged out successfully"}


@router.get("/available-jobs", response_model=list)
async def get_available_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Get available job requests for provider"""
    # Get provider's services
    result = await db.execute(
        select(ProviderService.service_id).where(
            (ProviderService.provider_id == current_user.id) &
            (ProviderService.is_active == True)
        )
    )
    service_ids = [r[0] for r in result.fetchall()]

    if not service_ids:
        return []

    # Get open bookings matching provider's services
    result = await db.execute(
        select(Booking).where(
            (Booking.service_id.in_(service_ids)) &
            (Booking.bid_status == BidStatus.OPEN_FOR_BIDS)
        ).order_by(Booking.created_at.desc())
    )
    bookings = result.scalars().all()

    return [
        {
            "id": b.id,
            "title": b.booking_details,
            "category": "grooming",  # TODO: Get from service/category
            "area": "Sandton",  # TODO: Parse from address
            "distance": 5.1,  # TODO: Calculate from coordinates
            "price": float(b.estimated_price),
            "stars": 4.8,
            "description": b.booking_details,
        }
        for b in bookings
    ]


@router.get("/appointments", response_model=list)
async def get_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Get provider's active appointments"""
    from sqlalchemy.orm import joinedload
    
    result = await db.execute(
        select(Booking)
        .where(
            (Booking.provider_id == current_user.id) &
            (Booking.status.in_([
                BookingStatus.ACCEPTED_BY_PROVIDER,
                BookingStatus.CUSTOMER_SELECTED,
                BookingStatus.IN_PROGRESS,
                BookingStatus.ON_MY_WAY,
                BookingStatus.AT_LOCATION,
            ]))
        )
        .order_by(Booking.requested_date)
        .options(joinedload(Booking.customer_id))
    )
    bookings = result.unique().scalars().all()

    appointments = []
    for b in bookings:
        # Get customer name from User table
        customer_result = await db.execute(
            select(User).where(User.id == b.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        # Get service name
        from app.models.service import Service
        service_result = await db.execute(
            select(Service).where(Service.id == b.service_id)
        )
        service = service_result.scalar_one_or_none()
        
        appointments.append({
            "id": b.id,
            "serviceName": service.name if service else b.booking_details,
            "category": "grooming",
            "clientName": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
            "dateISO": b.requested_date.isoformat() if b.requested_date else None,
            "price": float(b.estimated_price),
            "location": b.requested_address or "TBD",
            "status": b.status.value if b.status else "pending",
        })

    return appointments


@router.get("/history", response_model=list)
async def get_job_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Get provider's completed jobs"""
    from sqlalchemy.orm import joinedload
    from app.models.service import Service
    
    result = await db.execute(
        select(Booking).where(
            (Booking.provider_id == current_user.id) &
            (Booking.status == BookingStatus.COMPLETED)
        ).order_by(Booking.updated_at.desc())
    )
    bookings = result.scalars().all()

    history = []
    for b in bookings:
        # Get customer name from User table
        customer_result = await db.execute(
            select(User).where(User.id == b.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        # Get service name
        service_result = await db.execute(
            select(Service).where(Service.id == b.service_id)
        )
        service = service_result.scalar_one_or_none()
        
        # Get rating if exists
        rating_result = await db.execute(
            select(Rating).where(
                (Rating.booking_id == b.id) &
                (Rating.provider_id == current_user.id)
            )
        )
        rating = rating_result.scalar_one_or_none()

        history.append({
            "id": b.id,
            "serviceName": service.name if service else b.booking_details,
            "clientName": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
            "rating": float(rating.rating) if rating else 0,
            "price": float(b.estimated_price),
            "date": b.updated_at.isoformat() if b.updated_at else None,
        })

    return history


@router.get("/earnings", response_model=dict)
async def get_earnings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_provider)
):
    """Get provider's earnings summary"""
    # Get completed bookings
    result = await db.execute(
        select(Booking).where(
            (Booking.provider_id == current_user.id) &
            (Booking.status == BookingStatus.COMPLETED)
        )
    )
    bookings = result.scalars().all()

    total_earnings = sum(float(b.provider_gross) for b in bookings)
    total_jobs = len(bookings)

    return {
        "total_earnings": total_earnings,
        "total_jobs": total_jobs,
        "average_job_value": total_earnings / total_jobs if total_jobs > 0 else 0,
        "pending_payout": 0,  # TODO: Implement payout logic
    }
