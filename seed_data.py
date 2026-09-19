#!/usr/bin/env python3
"""
Seed database with sample data
"""
import asyncio
from app.db.database import AsyncSessionLocal
from app.models.service import ServiceCategory, Service

async def seed_data():
    """Add sample data to database"""
    async with AsyncSessionLocal() as session:
        # Check if we already have data
        from sqlalchemy import select
        result = await session.execute(select(ServiceCategory))
        existing = result.scalars().first()
        
        if existing:
            print("✅ Database already has data, skipping seed")
            return
        
        # Add categories
        categories = [
            ServiceCategory(name="Cleaning", description="Home and office cleaning services"),
            ServiceCategory(name="Plumbing", description="Plumbing and water system repairs"),
            ServiceCategory(name="Electrical", description="Electrical installation and repairs"),
            ServiceCategory(name="Painting", description="Interior and exterior painting"),
            ServiceCategory(name="Gardening", description="Landscaping and garden maintenance"),
            ServiceCategory(name="Handyman", description="General repairs and maintenance"),
            ServiceCategory(name="Appliance Repair", description="Repair of home appliances"),
            ServiceCategory(name="Carpentry", description="Woodworking and carpentry services"),
        ]
        
        for cat in categories:
            session.add(cat)
        
        await session.flush()  # Get IDs without committing
        
        # Add services
        services = [
            # Cleaning services
            Service(
                name="Residential Cleaning",
                description="Complete home cleaning service",
                category_id=categories[0].id,
                pricing_type="SIZE",
                is_active=True
            ),
            Service(
                name="Office Cleaning",
                description="Commercial office cleaning",
                category_id=categories[0].id,
                pricing_type="SIZE",
                is_active=True
            ),
            # Plumbing services
            Service(
                name="Pipe Repair",
                description="Fix leaks and burst pipes",
                category_id=categories[1].id,
                pricing_type="PROVIDER_DEFINED",
                is_active=True
            ),
            Service(
                name="Drain Cleaning",
                description="Unclog drains and pipes",
                category_id=categories[1].id,
                pricing_type="PROVIDER_DEFINED",
                is_active=True
            ),
            # Electrical services
            Service(
                name="Electrical Wiring",
                description="Install and repair electrical wiring",
                category_id=categories[2].id,
                pricing_type="PROVIDER_DEFINED",
                is_active=True
            ),
            Service(
                name="Light Installation",
                description="Install lights and fixtures",
                category_id=categories[2].id,
                pricing_type="PROVIDER_DEFINED",
                is_active=True
            ),
            # Painting
            Service(
                name="Interior Painting",
                description="Paint interior walls and ceilings",
                category_id=categories[3].id,
                pricing_type="SIZE",
                is_active=True
            ),
            Service(
                name="Exterior Painting",
                description="Paint exterior walls and structures",
                category_id=categories[3].id,
                pricing_type="SIZE",
                is_active=True
            ),
            # Gardening
            Service(
                name="Lawn Maintenance",
                description="Regular lawn mowing and care",
                category_id=categories[4].id,
                pricing_type="SIZE",
                is_active=True
            ),
            Service(
                name="Garden Design",
                description="Professional garden design and landscaping",
                category_id=categories[4].id,
                pricing_type="PROVIDER_DEFINED",
                is_active=True
            ),
        ]
        
        for svc in services:
            session.add(svc)
        
        await session.commit()
        print(f"✅ Seeded {len(categories)} categories and {len(services)} services")

if __name__ == "__main__":
    asyncio.run(seed_data())
