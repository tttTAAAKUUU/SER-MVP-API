"""Dynamic pricing engine for SIR marketplace"""
from decimal import Decimal
from typing import Dict, Any, Optional, List
from enum import Enum


class PricingType(str, Enum):
    """Pricing model types"""
    FIXED = "FIXED"
    HOURLY = "HOURLY"
    DURATION = "DURATION"
    SIZE = "SIZE"
    CUSTOM_OPTIONS = "CUSTOM_OPTIONS"
    PROVIDER_DEFINED = "PROVIDER_DEFINED"


class PricingResult:
    """Result of price calculation"""
    
    def __init__(
        self,
        base_price: Decimal,
        commission_percent: Decimal,
        commission_amount: Decimal,
        provider_gross: Decimal,
        total_to_pay: Decimal,
        breakdown: Dict[str, Any]
    ):
        self.base_price = base_price
        self.commission_percent = commission_percent
        self.commission_amount = commission_amount
        self.provider_gross = provider_gross
        self.total_to_pay = total_to_pay
        self.breakdown = breakdown
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "base_price": str(self.base_price),
            "commission_amount": str(self.commission_amount),
            "commission_percent": str(self.commission_percent),
            "provider_gross": str(self.provider_gross),
            "total_to_pay": str(self.total_to_pay),
            "breakdown": self.breakdown,
        }


class PriceRange:
    """Recommended price range for provider-defined services"""
    
    def __init__(self, min_price: Decimal, max_price: Decimal, description: Optional[str] = None):
        self.min_price = min_price
        self.max_price = max_price
        self.description = description
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "min_price": str(self.min_price),
            "max_price": str(self.max_price),
            "description": self.description or "",
        }


class PricingEngine:
    """Dynamic pricing engine supporting multiple pricing models"""
    
    def __init__(self, default_commission_percent: str = "18"):
        self.default_commission_percent = Decimal(default_commission_percent)
    
    def calculate_price(
        self,
        pricing_type: str,
        booking_details: Dict[str, Any],
        provider_price: Optional[str] = None,
        pricing_rules: Optional[List[Dict[str, Any]]] = None,
        category_name: Optional[str] = None,
    ) -> PricingResult:
        """
        Calculate price based on service type and booking details
        
        Args:
            pricing_type: Type of pricing (FIXED, HOURLY, SIZE, etc.)
            booking_details: Service-specific details from booking
            provider_price: Provider's fixed price (for FIXED/PROVIDER_DEFINED)
            pricing_rules: Algorithmic pricing rules for SIZE/DURATION models
            category_name: Service category for context
        
        Returns:
            PricingResult with breakdown
        """
        
        if pricing_type == PricingType.FIXED.value:
            return self._calculate_fixed(provider_price)
        
        elif pricing_type == PricingType.HOURLY.value:
            return self._calculate_hourly(booking_details, provider_price)
        
        elif pricing_type == PricingType.DURATION.value:
            return self._calculate_duration(booking_details, pricing_rules)
        
        elif pricing_type == PricingType.SIZE.value:
            # For cleaning: algorithmic pricing
            if category_name and ("cleaning" in category_name.lower() or "domestic" in category_name.lower()):
                return self._calculate_cleaning_price(booking_details, pricing_rules)
            # For car wash: algorithmic pricing
            elif category_name and ("car wash" in category_name.lower() or "car" in category_name.lower()):
                return self._calculate_car_wash_price(booking_details, pricing_rules)
            else:
                return self._calculate_size_based(booking_details, pricing_rules)
        
        elif pricing_type == PricingType.PROVIDER_DEFINED.value:
            return self._calculate_provider_defined(booking_details, provider_price)
        
        else:
            raise ValueError(f"Unknown pricing type: {pricing_type}")
    
    def _calculate_fixed(self, provider_price: str) -> PricingResult:
        """Fixed price model"""
        base_price = Decimal(provider_price)
        return self._apply_commission(base_price, {"type": "fixed_price"})
    
    def _calculate_hourly(
        self,
        booking_details: Dict[str, Any],
        provider_price: str
    ) -> PricingResult:
        """Hourly pricing"""
        hours = Decimal(booking_details.get("duration_hours", "1"))
        hourly_rate = Decimal(provider_price)
        base_price = hours * hourly_rate
        return self._apply_commission(base_price, {
            "type": "hourly",
            "hourly_rate": str(hourly_rate),
            "hours": str(hours),
        })
    
    def _calculate_duration(
        self,
        booking_details: Dict[str, Any],
        pricing_rules: Optional[List[Dict[str, Any]]]
    ) -> PricingResult:
        """Duration-based pricing (e.g., personal training sessions)"""
        duration = booking_details.get("duration_minutes", 60)
        
        if not pricing_rules:
            # Default fallback
            return self._apply_commission(Decimal("300"), {"type": "duration_default"})
        
        # Find matching rule
        for rule in pricing_rules:
            conditions = rule.get("rule_conditions", {})
            if conditions.get("duration_minutes") == duration:
                base_price = Decimal(rule.get("base_price", "300"))
                return self._apply_commission(base_price, {
                    "type": "duration",
                    "duration_minutes": duration,
                    "rule_name": rule.get("rule_name"),
                })
        
        # Default to first rule or fallback
        if pricing_rules:
            base_price = Decimal(pricing_rules[0].get("base_price", "300"))
        else:
            base_price = Decimal("300")
        
        return self._apply_commission(base_price, {"type": "duration_fallback"})
    
    def _calculate_size_based(
        self,
        booking_details: Dict[str, Any],
        pricing_rules: Optional[List[Dict[str, Any]]]
    ) -> PricingResult:
        """Size-based pricing (flexible for various services)"""
        size = booking_details.get("size", "standard")
        
        if not pricing_rules:
            base_price = Decimal("300")
        else:
            # Find matching rule
            matching_rule = None
            for rule in pricing_rules:
                conditions = rule.get("rule_conditions", {})
                if conditions.get("size") == size:
                    matching_rule = rule
                    break
            
            if matching_rule:
                base_price = Decimal(matching_rule.get("base_price", "300"))
            else:
                base_price = Decimal(pricing_rules[0].get("base_price", "300")) if pricing_rules else Decimal("300")
        
        return self._apply_commission(base_price, {"type": "size_based", "size": size})
    
    def _calculate_cleaning_price(
        self,
        booking_details: Dict[str, Any],
        pricing_rules: Optional[List[Dict[str, Any]]]
    ) -> PricingResult:
        """
        Algorithmic pricing for cleaning services in ZAR (South Africa).
        
        Factors:
        - House size (bedrooms, bathrooms)
        - Property type (apartment, townhouse, house)
        - Clean type (standard, deep, move-in/move-out)
        - Add-ons (laundry by load count, windows, carpet steam, etc.)
        """
        bedrooms = int(booking_details.get("bedrooms", 2))
        bathrooms = int(booking_details.get("bathrooms", 1))
        clean_type = booking_details.get("clean_type", "standard").lower()
        add_ons = booking_details.get("add_ons", [])
        property_type = booking_details.get("property_type", "apartment").lower()
        
        # Base price by bedroom count (Standard Clean) - ZAR South Africa pricing
        base_prices = {
            1: Decimal("280"),   # Studio/1BR apartment
            2: Decimal("420"),   # 2BR apartment/townhouse
            3: Decimal("580"),   # 3BR house
            4: Decimal("720"),   # 4BR house
            5: Decimal("860"),   # 5BR+ house
        }
        
        # Property type multiplier
        property_multipliers = {
            "apartment": Decimal("0.9"),
            "townhouse": Decimal("1.0"),
            "house": Decimal("1.1"),
            "villa": Decimal("1.2"),
        }
        
        bedrooms_key = min(bedrooms, 5)
        base_price = base_prices.get(bedrooms_key, Decimal("580"))
        property_mult = property_multipliers.get(property_type, Decimal("1.0"))
        base_price = base_price * property_mult
        
        breakdown = {
            "type": "cleaning_algorithmic_za",
            "currency": "ZAR",
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "property_type": property_type,
            "clean_type": clean_type,
            "base_price_zar": str(base_price.quantize(Decimal("0.01"))),
        }
        
        # Clean type surcharges
        clean_type_surcharges = {
            "standard": Decimal("0"),
            "deep": Decimal("200"),
            "move_in": Decimal("300"),
            "move_out": Decimal("300"),
        }
        
        surcharge = clean_type_surcharges.get(clean_type, Decimal("0"))
        if surcharge > 0:
            base_price = base_price + surcharge
            breakdown["clean_type_surcharge_zar"] = str(surcharge)
        
        # Add-ons with SA pricing
        total_add_ons = Decimal("0")
        add_ons_detail = {}
        
        if isinstance(add_ons, list):
            for add_on in add_ons:
                if isinstance(add_on, dict):
                    add_on_type = add_on.get("type", "")
                    if add_on_type == "laundry":
                        loads = int(add_on.get("loads", 1))
                        add_on_price = Decimal("60") * Decimal(loads)
                        key = f"laundry_{loads}loads"
                    elif add_on_type == "windows":
                        scope = add_on.get("scope", "interior")
                        add_on_price = Decimal("80") if scope == "interior" else Decimal("150")
                        key = f"windows_{scope}"
                    elif add_on_type == "carpet_steam":
                        add_on_price = Decimal("200")
                        key = "carpet_steam"
                    else:
                        continue
                    
                    total_add_ons += add_on_price
                    add_ons_detail[key] = str(add_on_price.quantize(Decimal("0.01")))
        
        base_price = base_price + total_add_ons
        
        if add_ons_detail:
            breakdown["add_ons_zar"] = add_ons_detail
        
        return self._apply_commission(base_price, breakdown)
    
    def _calculate_car_wash_price(
        self,
        booking_details: Dict[str, Any],
        pricing_rules: Optional[List[Dict[str, Any]]]
    ) -> PricingResult:
        """
        Algorithmic pricing for car wash services in ZAR (South Africa).
        
        Factors:
        - Vehicle type (hatchback, sedan, suv, bakkie, luxury)
        - Package (basic, standard, premium, executive/detail)
        - Vehicle condition (clean, moderate, dirty, muddy)
        - Add-ons (engine bay, undercarriage, leather, tire shine, ceramic)
        """
        vehicle_type = booking_details.get("vehicle_type", "sedan").lower()
        package = booking_details.get("package", "standard").lower()
        vehicle_condition = booking_details.get("vehicle_condition", "moderate").lower()
        add_ons = booking_details.get("add_ons", [])
        
        # Pricing matrix in ZAR: vehicle_type x package (South Africa)
        pricing_matrix = {
            "hatchback": {
                "basic": Decimal("100"),
                "standard": Decimal("160"),
                "premium": Decimal("280"),
                "executive": Decimal("380"),
            },
            "sedan": {
                "basic": Decimal("120"),
                "standard": Decimal("200"),
                "premium": Decimal("320"),
                "executive": Decimal("450"),
            },
            "suv": {
                "basic": Decimal("150"),
                "standard": Decimal("260"),
                "premium": Decimal("420"),
                "executive": Decimal("580"),
            },
            "bakkie": {
                "basic": Decimal("140"),
                "standard": Decimal("240"),
                "premium": Decimal("380"),
                "executive": Decimal("520"),
            },
            "luxury": {
                "basic": Decimal("200"),
                "standard": Decimal("350"),
                "premium": Decimal("550"),
                "executive": Decimal("800"),
            },
        }
        
        vehicle_pricing = pricing_matrix.get(vehicle_type, pricing_matrix["sedan"])
        base_price = vehicle_pricing.get(package, Decimal("200"))
        
        breakdown = {
            "type": "car_wash_algorithmic_za",
            "currency": "ZAR",
            "vehicle_type": vehicle_type,
            "package": package,
            "vehicle_condition": vehicle_condition,
            "base_price_zar": str(base_price),
        }
        
        # Condition multiplier
        condition_multipliers = {
            "clean": Decimal("0.8"),
            "moderate": Decimal("1.0"),
            "dirty": Decimal("1.15"),
            "muddy": Decimal("1.3"),
        }
        condition_mult = condition_multipliers.get(vehicle_condition, Decimal("1.0"))
        if condition_mult != Decimal("1.0"):
            surcharge = base_price * (condition_mult - Decimal("1.0"))
            base_price = base_price * condition_mult
            breakdown["condition_surcharge_zar"] = str(surcharge.quantize(Decimal("0.01")))
        
        # Add-ons pricing in ZAR
        add_on_prices = {
            "engine_bay": Decimal("50"),
            "undercarriage": Decimal("40"),
            "leather_conditioning": Decimal("70"),
            "tire_shine": Decimal("30"),
            "window_tint": Decimal("40"),
            "ceramic_coat": Decimal("150"),
        }
        
        total_add_ons = Decimal("0")
        add_ons_detail = {}
        
        if isinstance(add_ons, list):
            for add_on in add_ons:
                add_on_key = add_on if isinstance(add_on, str) else add_on.get("type", "")
                add_on_price = add_on_prices.get(add_on_key, Decimal("0"))
                if add_on_price > 0:
                    total_add_ons += add_on_price
                    add_ons_detail[add_on_key] = str(add_on_price)
        
        base_price = base_price + total_add_ons
        
        if add_ons_detail:
            breakdown["add_ons_zar"] = add_ons_detail
        
        return self._apply_commission(base_price, breakdown)
    
    def _calculate_provider_defined(
        self,
        booking_details: Dict[str, Any],
        provider_price: Optional[str] = None
    ) -> PricingResult:
        """Provider-defined pricing with optional range validation"""
        if provider_price:
            base_price = Decimal(provider_price)
        else:
            # Fallback to booking-provided price
            base_price = Decimal(booking_details.get("provider_set_price", "300"))
        
        return self._apply_commission(base_price, {
            "type": "provider_defined",
            "provider_set_price": str(base_price),
        })
    
    def _apply_commission(
        self,
        base_price: Decimal,
        breakdown: Dict[str, Any]
    ) -> PricingResult:
        """Apply SIR commission to base price"""
        commission_percent = self.default_commission_percent
        commission_amount = base_price * (commission_percent / Decimal("100"))
        provider_gross = base_price - commission_amount
        
        # Round to 2 decimal places
        commission_amount = commission_amount.quantize(Decimal("0.01"))
        provider_gross = provider_gross.quantize(Decimal("0.01"))
        base_price = base_price.quantize(Decimal("0.01"))
        
        breakdown["commission_percent"] = str(commission_percent)
        breakdown["commission_amount"] = str(commission_amount)
        breakdown["provider_gross"] = str(provider_gross)
        
        return PricingResult(
            base_price=base_price,
            commission_percent=commission_percent,
            commission_amount=commission_amount,
            provider_gross=provider_gross,
            total_to_pay=base_price,
            breakdown=breakdown,
        )
    
    def get_recommended_price_range(
        self,
        service_name: str,
        category_name: Optional[str] = None,
        booking_details: Optional[Dict[str, Any]] = None
    ) -> PriceRange:
        """
        Get recommended price range for provider-defined services in ZAR (South Africa).
        
        Args:
            service_name: Name of the service (e.g., "Haircut", "Personal Training")
            category_name: Service category (e.g., "Beauty", "Fitness")
            booking_details: Service-specific details for context
            
        Returns:
            PriceRange with min and max recommended prices in ZAR
        """
        service_lower = service_name.lower()
        category_lower = (category_name or "").lower()
        
        # Beauty & personal care services (ZAR pricing for South Africa)
        if "haircut" in service_lower:
            return PriceRange(Decimal("150"), Decimal("350"), "Classic haircut, 30-45 minutes")
        elif "styling" in service_lower or "braid" in service_lower:
            return PriceRange(Decimal("200"), Decimal("600"), "Hair styling, varies by complexity")
        elif "nail" in service_lower:
            return PriceRange(Decimal("120"), Decimal("300"), "Nail service, 45-60 minutes")
        elif "lash" in service_lower or "eyelash" in service_lower:
            return PriceRange(Decimal("150"), Decimal("400"), "Lash service, 60-90 minutes")
        elif "makeup" in service_lower:
            return PriceRange(Decimal("200"), Decimal("500"), "Makeup application, 60 minutes")
        elif "massage" in service_lower or "spa" in service_lower:
            # Duration matters for massage
            duration = booking_details.get("duration_minutes", 60) if booking_details else 60
            if duration <= 30:
                return PriceRange(Decimal("150"), Decimal("300"), "30-minute massage")
            elif duration <= 60:
                return PriceRange(Decimal("250"), Decimal("500"), "60-minute massage")
            else:
                return PriceRange(Decimal("350"), Decimal("700"), "90+ minute massage")
        
        # Personal training (ZAR pricing for South Africa)
        elif category_lower == "fitness" or category_lower == "personal training" or "trainer" in service_lower or "training" in service_lower or "bodyweight" in service_lower:
            # Duration matters
            duration = booking_details.get("duration_minutes", 60) if booking_details else 60
            if duration <= 30:
                return PriceRange(Decimal("150"), Decimal("300"), "30-minute session")
            elif duration <= 60:
                return PriceRange(Decimal("250"), Decimal("500"), "60-minute session")
            else:
                return PriceRange(Decimal("350"), Decimal("700"), "90+ minute session")
        
        # Default range for unknown provider-defined services (ZAR)
        return PriceRange(Decimal("150"), Decimal("800"), "Custom service pricing")


# Default pricing engine instance
pricing_engine = PricingEngine()
