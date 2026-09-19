"""Booking details schemas for different service categories - South African market (ZAR)"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LaundryAddOn(BaseModel):
    """Laundry add-on details"""
    type: str = "laundry"
    loads: int = Field(1, ge=1, le=5, description="Number of laundry loads")


class WindowCleaningAddOn(BaseModel):
    """Window cleaning add-on"""
    type: str = "windows"
    scope: str = Field("interior", description="interior or full")


class CleaningBookingDetails(BaseModel):
    """Domestic cleaning service booking details"""
    property_type: str = Field("apartment", description="apartment, townhouse, house, villa")
    bedrooms: int = Field(2, ge=1, le=10, description="Number of bedrooms")
    bathrooms: int = Field(1, ge=1, le=10, description="Number of bathrooms")
    clean_type: str = Field("standard", description="standard, deep, move_in, move_out")
    add_ons: List[Dict[str, Any]] = Field(default_factory=list, description="List of add-ons")
    special_instructions: Optional[str] = Field(None, description="Special requests or notes")


class CarWashBookingDetails(BaseModel):
    """Car wash service booking details"""
    vehicle_type: str = Field("sedan", description="hatchback, sedan, suv, bakkie, luxury")
    package: str = Field("standard", description="basic, standard, premium, executive")
    vehicle_condition: str = Field("moderate", description="clean, moderate, dirty, muddy")
    add_ons: List[str] = Field(default_factory=list, description="Add-on services")
    special_requests: Optional[str] = Field(None, description="Special requests")


class CosmeticBookingDetails(BaseModel):
    """Beauty/cosmetic service booking details"""
    service_type: str = Field("haircut", description="Type of service")
    hair_length: Optional[str] = Field(None, description="short, medium, long")
    hair_type: Optional[str] = Field(None, description="straight, wavy, curly, coily")
    specific_style_description: Optional[str] = Field(None, description="Detailed style description")
    reference_photo_urls: List[str] = Field(default_factory=list, description="Reference photos (up to 3)")
    special_requests: Optional[str] = Field(None, description="Allergies, sensitivities, preferences")


class TrainingBookingDetails(BaseModel):
    """Personal training service booking details"""
    session_type: str = Field("session", description="session or package")
    package_duration: Optional[str] = Field(None, description="4weeks, 6weeks, 8weeks")
    training_type: List[str] = Field(default_factory=list, description="Types of training")
    fitness_goal: str = Field("general", description="Fitness goal")
    experience_level: str = Field("beginner", description="beginner, intermediate, advanced")
    available_equipment: List[str] = Field(default_factory=list, description="Available equipment")
    injuries_limitations: Optional[str] = Field(None, description="Injuries or limitations")
    preferred_intensity: str = Field("moderate", description="light, moderate, high")
    session_duration_preference: str = Field("60", description="Duration in minutes")
    location: str = Field("in_person", description="in_person or online")


class CreateBookingRequest(BaseModel):
    """Create booking request with category-specific details"""
    service_id: int
    category_id: int
    category_name: str = Field(description="cosmetic, domestic, car, training")
    booking_details: Dict[str, Any] = Field(description="Service-specific booking details")
    requested_address: str = Field(description="Service location address")
    requested_date: str = Field(description="Date of service (YYYY-MM-DD)")
    requested_time: str = Field(description="Time of service (HH:MM)")
    customer_notes: Optional[str] = Field(None, description="Additional customer notes")
