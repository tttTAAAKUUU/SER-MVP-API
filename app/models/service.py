"""Service category and service models"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class PricingType(str, enum.Enum):
    """Service pricing model types"""
    FIXED = "FIXED"
    HOURLY = "HOURLY"
    DURATION = "DURATION"
    SIZE = "SIZE"
    CUSTOM_OPTIONS = "CUSTOM_OPTIONS"
    PROVIDER_DEFINED = "PROVIDER_DEFINED"


class ServiceCategory(Base):
    """Service categories: Cosmetic, Domestic, Car, Training"""
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # e.g., "Cosmetic", "Domestic"
    slug = Column(String, unique=True, nullable=False)  # e.g., "cosmetic", "domestic"
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Path to icon asset
    color = Column(String, nullable=True)  # Hex color for UI
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategories = relationship("ServiceSubcategory", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ServiceCategory {self.name}>"


class ServiceSubcategory(Base):
    """Subcategories within main categories"""
    __tablename__ = "service_subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "Men's Hair", "Womens Hair"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("ServiceCategory", back_populates="subcategories")
    services = relationship("Service", back_populates="subcategory", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ServiceSubcategory {self.name}>"


class Service(Base):
    """Individual services within subcategories"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=False, index=True)
    subcategory_id = Column(Integer, ForeignKey("service_subcategories.id"), nullable=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Classic Haircut", "Gel Manicure"
    description = Column(Text, nullable=True)
    pricing_type = Column(Enum(PricingType), default=PricingType.FIXED, nullable=False)
    base_price_min = Column(Float, nullable=True)  # Minimum price
    base_price_max = Column(Float, nullable=True)  # Maximum price
    estimated_duration_minutes = Column(Integer, nullable=True)  # How long the service typically takes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategory = relationship("ServiceSubcategory", back_populates="services")

    def __repr__(self):
        return f"<Service {self.name}>"


class ServicePricingRule(Base):
    """Algorithmic pricing rules for services (especially Cleaning & Car Wash)"""
    __tablename__ = "service_pricing_rules"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    rule_name = Column(String, nullable=False)  # e.g., "Studio Clean", "3BR Deep Clean"
    base_price = Column(String, nullable=False)  # Stored as decimal string for precision
    rule_conditions = Column(JSON, nullable=True)  # e.g., {"bedrooms": 3, "clean_type": "deep"}
    adjustments = Column(JSON, default=list)  # e.g., [{factor: "bathrooms", price_per_unit: "150"}]
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ServicePricingRule {self.rule_name}>"
