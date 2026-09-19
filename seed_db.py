#!/usr/bin/env python3
"""Seed database with sample services"""
import asyncio
from app.db.database import AsyncSessionLocal
from app.models.service import ServiceCategory, Service

async def seed():
    async with AsyncSessionLocal() as session:
        # Create categories
        categories_data = [
            {"name": "Cosmetic", "description": "Beauty, hair, and personal care services"},
            {"name": "Domestic", "description": "Home cleaning and maintenance services"},
            {"name": "Car Wash", "description": "Vehicle cleaning and detailing"},
            {"name": "Training", "description": "Educational and coaching services"},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat = ServiceCategory(**cat_data)
            session.add(cat)
            await session.flush()
            categories[cat.name] = cat
        
        # Create services
        services_data = [
            # Cosmetic
            {"name": "Hair Styling", "description": "Professional hair cut and styling", "category": "Cosmetic", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Facial Treatment", "description": "Rejuvenating facial with premium products", "category": "Cosmetic", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Manicure & Pedicure", "description": "Nail care and polish service", "category": "Cosmetic", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Massage Therapy", "description": "Relaxing professional massage", "category": "Cosmetic", "pricing_type": "PROVIDER_DEFINED"},
            
            # Domestic
            {"name": "House Cleaning", "description": "Deep clean or regular maintenance", "category": "Domestic", "pricing_type": "SIZE"},
            {"name": "Laundry Service", "description": "Professional laundry and ironing", "category": "Domestic", "pricing_type": "SIZE"},
            {"name": "Kitchen Cleaning", "description": "Specialized kitchen deep clean", "category": "Domestic", "pricing_type": "SIZE"},
            {"name": "Bathroom Cleaning", "description": "Complete bathroom sanitization", "category": "Domestic", "pricing_type": "SIZE"},
            
            # Car Wash
            {"name": "Basic Car Wash", "description": "Quick exterior wash and dry", "category": "Car Wash", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Premium Detailing", "description": "Complete interior and exterior detailing", "category": "Car Wash", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Engine Cleaning", "description": "Professional engine bay cleaning", "category": "Car Wash", "pricing_type": "PROVIDER_DEFINED"},
            
            # Training
            {"name": "Fitness Training", "description": "Personal training sessions", "category": "Training", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Online Tutoring", "description": "Academic support and tutoring", "category": "Training", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Language Classes", "description": "Learn a new language", "category": "Training", "pricing_type": "PROVIDER_DEFINED"},
            {"name": "Professional Coaching", "description": "Career and professional development", "category": "Training", "pricing_type": "PROVIDER_DEFINED"},
        ]
        
        for svc_data in services_data:
            cat = categories[svc_data.pop("category")]
            service = Service(
                **svc_data,
                category_id=cat.id,
                is_active=True
            )
            session.add(service)
        
        await session.commit()
        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
