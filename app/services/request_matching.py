"""Service to match booking requests with available providers"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal
import math

from app.models.booking import Booking
from app.models.provider import ProviderProfile, ProviderService
from app.models.service import Service, ServiceCategory
from app.models.user import User, UserRole


class RequestMatcher:
    """Match booking requests with eligible providers"""
    
    async def find_matching_providers(
        self,
        booking: Booking,
        db: AsyncSession,
        radius_buffer_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Find providers matching a booking request.
        
        Criteria:
        - Verified provider
        - Offers the requested service
        - Provider's service area overlaps request location
        - Provider is active
        
        Args:
            booking: The booking request
            db: Database session
            radius_buffer_km: Buffer to add to provider's service radius
            
        Returns:
            List of provider dicts with matching info
        """
        
        # Get the service
        result = await db.execute(
            select(Service).where(Service.id == booking.service_id)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            return []
        
        # Get all providers who offer this service
        result = await db.execute(
            select(ProviderService)
            .where(
                (ProviderService.service_id == booking.service_id) &
                (ProviderService.is_active == True)
            )
        )
        provider_services = result.scalars().all()
        
        if not provider_services:
            return []
        
        matching_providers = []
        provider_ids = [ps.provider_id for ps in provider_services]
        
        # Get provider profiles and verify criteria
        result = await db.execute(
            select(ProviderProfile)
            .where(ProviderProfile.provider_id.in_(provider_ids))
        )
        profiles = result.scalars().all()
        
        for profile in profiles:
            # Get user for verification status and basic info
            result = await db.execute(
                select(User).where(User.id == profile.provider_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or user.role != UserRole.PROVIDER or not user.is_active:
                continue
            
            # Check verification status
            if profile.verification_status.value != "VERIFIED":
                continue
            
            # Check service area (simple distance check)
            if self._is_within_service_area(
                booking.requested_latitude,
                booking.requested_longitude,
                profile.service_area_latitude,
                profile.service_area_longitude,
                profile.service_area_radius_km,
                radius_buffer_km
            ):
                matching_providers.append({
                    "provider_id": profile.provider_id,
                    "provider_name": f"{user.first_name} {user.last_name}",
                    "business_name": profile.business_name,
                    "rating": profile.average_rating,
                    "completed_jobs": profile.completed_jobs,
                    "verification_status": profile.verification_status.value,
                })
        
        return matching_providers
    
    def _is_within_service_area(
        self,
        customer_lat: Optional[str],
        customer_lon: Optional[str],
        provider_lat: Optional[str],
        provider_lon: Optional[str],
        provider_radius_km: Optional[str],
        buffer_km: float = 0
    ) -> bool:
        """
        Check if customer location is within provider's service area.
        Uses simple distance calculation (Haversine).
        
        Args:
            customer_lat: Customer latitude as string
            customer_lon: Customer longitude as string
            provider_lat: Provider service area center latitude
            provider_lon: Provider service area center longitude
            provider_radius_km: Provider service radius in km
            buffer_km: Additional buffer to add to radius
            
        Returns:
            True if customer is within service area
        """
        
        # If any coordinate is missing, default to True (allow)
        if not all([customer_lat, customer_lon, provider_lat, provider_lon]):
            return True
        
        try:
            c_lat = float(customer_lat)
            c_lon = float(customer_lon)
            p_lat = float(provider_lat)
            p_lon = float(provider_lon)
            radius = float(provider_radius_km or "15") + buffer_km
        except (ValueError, TypeError):
            return True  # Default to allowing if parsing fails
        
        # Haversine distance
        distance_km = self._haversine_distance(c_lat, c_lon, p_lat, p_lon)
        return distance_km <= radius
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in kilometers.
        
        Args:
            lat1, lon1: First point
            lat2, lon2: Second point
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


# Singleton instance
request_matcher = RequestMatcher()
