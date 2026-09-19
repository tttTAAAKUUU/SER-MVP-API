"""Bidding and request-based matching endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal

from app.db.database import get_db
from app.models.booking import Booking, BidStatus  # Booking's bidding status
from app.models.bid import ProviderBid, BidStatus as ProviderBidStatus  # Provider's bid status
from app.models.service import Service, ServiceCategory
from app.models.provider import ProviderProfile, ProviderService
from app.models.user import User
from app.schemas.bid import (
    ProviderBidRequest,
    ProviderBidResponse,
    BidWithProviderResponse,
    SelectBidRequest,
    AvailableRequestResponse,
)
from app.services.pricing_engine import pricing_engine
from app.services.request_matching import request_matcher
from app.services.notification_service import notification_service

router = APIRouter(prefix="/bookings", tags=["bidding"])


@router.get("/{booking_id}/available", response_model=AvailableRequestResponse)
async def get_available_request(booking_id: int, db: AsyncSession = Depends(get_db)):
    """Get a booking request (for providers to view)"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get service info
    result = await db.execute(select(Service).where(Service.id == booking.service_id))
    service = result.scalar_one_or_none()
    
    # Get category info
    result = await db.execute(select(ServiceCategory).where(ServiceCategory.id == booking.category_id))
    category = result.scalar_one_or_none()
    
    return {
        "id": booking.id,
        "service_id": booking.service_id,
        "service_name": service.name if service else "Unknown",
        "category_name": category.name if category else "Unknown",
        "booking_details": booking.booking_details,
        "requested_address": booking.requested_address,
        "requested_date": booking.requested_date.isoformat(),
        "requested_time": booking.requested_time,
        "estimated_price": booking.estimated_price,
        "customer_notes": booking.customer_notes,
        "created_at": booking.created_at,
    }


@router.get("/{booking_id}/provider-available-jobs", response_model=list[AvailableRequestResponse])
async def get_provider_available_jobs(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get available job requests for a provider to bid on"""
    # Get provider profile to verify they exist
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.provider_id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Get open bookings (requests) matching provider's services
    result = await db.execute(
        select(ProviderProfile.provider_id).where(ProviderProfile.provider_id == provider_id)
    )
    
    # Get provider's services
    from app.models.provider import ProviderService
    result = await db.execute(
        select(ProviderService.service_id).where(
            (ProviderService.provider_id == provider_id) &
            (ProviderService.is_active == True)
        )
    )
    service_ids = [r[0] for r in result.fetchall()]
    
    if not service_ids:
        return []
    
    # Get open bookings for those services
    result = await db.execute(
        select(Booking).where(
            (Booking.service_id.in_(service_ids)) &
            (Booking.bid_status == BidStatus.OPEN_FOR_BIDS)
        ).order_by(Booking.created_at.desc())
    )
    
    bookings = result.scalars().all()
    
    # Format response
    available_requests = []
    for booking in bookings:
        result = await db.execute(select(Service).where(Service.id == booking.service_id))
        service = result.scalar_one_or_none()
        
        result = await db.execute(select(ServiceCategory).where(ServiceCategory.id == booking.category_id))
        category = result.scalar_one_or_none()
        
        available_requests.append({
            "id": booking.id,
            "service_id": booking.service_id,
            "service_name": service.name if service else "Unknown",
            "category_name": category.name if category else "Unknown",
            "booking_details": booking.booking_details,
            "requested_address": booking.requested_address,
            "requested_date": booking.requested_date.isoformat(),
            "requested_time": booking.requested_time,
            "estimated_price": booking.estimated_price,
            "customer_notes": booking.customer_notes,
            "created_at": booking.created_at,
        })
    
    return available_requests


@router.post("/{booking_id}/bid", response_model=ProviderBidResponse)
async def place_bid(
    booking_id: int,
    request: ProviderBidRequest,
    db: AsyncSession = Depends(get_db),
    # In real impl, current_user would be injected
):
    """Provider places a bid on a booking request"""
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check booking is open for bids
    if booking.bid_status != BidStatus.OPEN_FOR_BIDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not open for bids"
        )
    
    # Get service to check pricing type
    result = await db.execute(select(Service).where(Service.id == booking.service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get category for context
    result = await db.execute(select(ServiceCategory).where(ServiceCategory.id == booking.category_id))
    category = result.scalar_one_or_none()
    category_name = category.name if category else None
    
    # Validate bid price based on pricing type
    bid_price = Decimal(request.bid_price)
    estimated_price = Decimal(booking.estimated_price)
    
    if service.pricing_type == "SIZE":  # Algorithmic pricing (cleaning, car wash)
        # Bid must match estimated price exactly
        if bid_price != estimated_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"For this service, bid price must be R{booking.estimated_price}. Algorithmic pricing is locked."
            )
    elif service.pricing_type == "PROVIDER_DEFINED":  # Cosmetic, trainer (bidding range)
        # Validate bid is within recommended range
        price_range = pricing_engine.get_recommended_price_range(
            service.name,
            category_name,
            booking.booking_details
        )
        
        if bid_price < price_range.min_price or bid_price > price_range.max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bid price must be between R{price_range.min_price} and R{price_range.max_price}"
            )
    
    # For now, assume provider_id = 1 (mock) - in real impl would be from auth
    provider_id = 1
    
    # Create bid
    bid = ProviderBid(
        booking_id=booking_id,
        provider_id=provider_id,
        bid_price=str(bid_price),
        bid_message=request.bid_message,
        status=ProviderBidStatus.PENDING,
    )
    
    db.add(bid)
    
    # Update booking status if this is first bid
    if booking.bid_status == BidStatus.OPEN_FOR_BIDS:
        booking.bid_status = BidStatus.BIDS_RECEIVED
    
    await db.commit()
    await db.refresh(bid)
    
    return bid


@router.get("/{booking_id}/bids", response_model=list[BidWithProviderResponse])
async def get_booking_bids(booking_id: int, db: AsyncSession = Depends(get_db)):
    """Get all bids for a booking (customer view)"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get all pending bids
    result = await db.execute(
        select(ProviderBid).where(
            (ProviderBid.booking_id == booking_id) &
            (ProviderBid.status == ProviderBidStatus.PENDING)
        ).order_by(ProviderBid.created_at.desc())
    )
    bids = result.scalars().all()
    
    # Enrich with provider info
    bids_with_provider = []
    for bid in bids:
        # Get provider user
        result = await db.execute(select(User).where(User.id == bid.provider_id))
        user = result.scalar_one_or_none()
        
        # Get provider profile
        result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.provider_id == bid.provider_id)
        )
        profile = result.scalar_one_or_none()
        
        bids_with_provider.append({
            "id": bid.id,
            "booking_id": bid.booking_id,
            "provider_id": bid.provider_id,
            "bid_price": bid.bid_price,
            "bid_message": bid.bid_message,
            "status": bid.status.value,
            "created_at": bid.created_at,
            "provider_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "provider_business_name": profile.business_name if profile else None,
            "provider_rating": profile.average_rating if profile else "0.0",
            "provider_completed_jobs": profile.completed_jobs if profile else 0,
            "provider_verification_status": profile.verification_status.value if profile else "PENDING",
            "provider_profile_image": profile.profile_image_url if profile else None,
            "provider_years_experience": profile.years_of_experience if profile else None,
        })
    
    return bids_with_provider


@router.post("/{booking_id}/select-bid/{provider_id}")
async def select_bid(
    booking_id: int,
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Customer selects a provider's bid"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check that booking is in correct state
    if booking.bid_status not in [BidStatus.OPEN_FOR_BIDS, BidStatus.BIDS_RECEIVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not accepting selections"
        )
    
    # Get the provider's bid
    result = await db.execute(
        select(ProviderBid).where(
            (ProviderBid.booking_id == booking_id) &
            (ProviderBid.provider_id == provider_id) &
            (ProviderBid.status == ProviderBidStatus.PENDING)
        )
    )
    selected_bid = result.scalar_one_or_none()
    
    if not selected_bid:
        raise HTTPException(
            status_code=404,
            detail="Bid not found or already processed"
        )
    
    # Accept selected bid
    selected_bid.status = ProviderBidStatus.ACCEPTED
    
    # Reject all other bids
    result = await db.execute(
        select(ProviderBid).where(
            (ProviderBid.booking_id == booking_id) &
            (ProviderBid.provider_id != provider_id) &
            (ProviderBid.status == ProviderBidStatus.PENDING)
        )
    )
    other_bids = result.scalars().all()
    
    for bid in other_bids:
        bid.status = ProviderBidStatus.REJECTED
    
    # Update booking
    booking.provider_id = provider_id
    booking.bid_status = BidStatus.PROVIDER_SELECTED
    booking.final_price = selected_bid.bid_price
    
    # Recalculate commission based on final bid price
    bid_price = Decimal(selected_bid.bid_price)
    commission_percent = Decimal(booking.commission_percent or "18")
    commission_amount = bid_price * (commission_percent / Decimal("100"))
    provider_gross = bid_price - commission_amount
    
    booking.commission_amount = str(commission_amount.quantize(Decimal("0.01")))
    booking.provider_gross = str(provider_gross.quantize(Decimal("0.01")))
    
    db.add(booking)
    db.add(selected_bid)
    
    for bid in other_bids:
        db.add(bid)
    
    await db.commit()
    
    # Notify selected provider
    selected_provider = await db.execute(select(User).where(User.id == provider_id))
    provider_user = selected_provider.scalar_one_or_none()
    customer = await db.execute(select(User).where(User.id == booking.customer_id))
    customer_user = customer.scalar_one_or_none()
    
    service = await db.execute(select(Service).where(Service.id == booking.service_id))
    service_obj = service.scalar_one_or_none()
    
    if provider_user and customer_user and service_obj:
        await notification_service.notify_bid_accepted(
            db=db,
            provider_id=provider_id,
            booking_id=booking_id,
            customer_name=customer_user.first_name,
            service_name=service_obj.name
        )
    
    # Notify rejected providers
    for bid in other_bids:
        if bid.provider_id != provider_id:
            await notification_service.notify_bid_rejected(
                db=db,
                provider_id=bid.provider_id,
                booking_id=booking_id,
                service_name=service_obj.name if service_obj else "Service"
            )
    
    return {
        "message": "Provider selected",
        "booking_id": booking_id,
        "provider_id": provider_id,
        "final_price": booking.final_price,
    }


@router.post("/{booking_id}/distribute")
async def distribute_request(booking_id: int, db: AsyncSession = Depends(get_db)):
    """
    Distribute booking request to matching providers.
    Should be called by system after booking creation.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check booking is in right state
    if booking.bid_status != BidStatus.OPEN_FOR_BIDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not in OPEN_FOR_BIDS state"
        )
    
    # Find matching providers
    matching_providers = await request_matcher.find_matching_providers(booking, db)
    
    if not matching_providers:
        return {
            "message": "No matching providers found",
            "booking_id": booking_id,
            "providers_notified": 0,
        }
    
    # Get service info for notification
    result = await db.execute(select(Service).where(Service.id == booking.service_id))
    service = result.scalar_one_or_none()
    
    # Notify providers
    provider_ids = [p["provider_id"] for p in matching_providers]
    
    await notification_service.notify_providers_of_new_job(
        db=db,
        booking_id=booking_id,
        provider_ids=provider_ids,
        service_name=service.name if service else "Service",
        location=booking.requested_address or "Specified location",
        estimated_price=booking.estimated_price,
    )
    
    return {
        "message": "Request distributed to providers",
        "booking_id": booking_id,
        "providers_notified": len(provider_ids),
        "providers": matching_providers,
    }
