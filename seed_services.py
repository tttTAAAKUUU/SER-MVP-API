#!/usr/bin/env python3
"""
Seed the database with service categories, subcategories, and services
"""
import asyncio
from app.db.database import AsyncSessionLocal
from app.models.service import ServiceCategory, ServiceSubcategory, Service, PricingType
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_services():
    """Seed services with categories and subcategories"""
    async with AsyncSessionLocal() as session:
        try:
            # Create categories
            cosmetic = ServiceCategory(
                name="Cosmetic",
                slug="cosmetic",
                description="Personal grooming and beauty services",
                color="#FF6B9D"
            )
            domestic = ServiceCategory(
                name="Domestic",
                slug="domestic",
                description="Home cleaning and laundry services",
                color="#4ECDC4"
            )
            car = ServiceCategory(
                name="Car",
                slug="car",
                description="Vehicle detailing and washing services",
                color="#FFE66D"
            )
            training = ServiceCategory(
                name="Training",
                slug="training",
                description="Physical fitness and training sessions",
                color="#95E1D3"
            )
            
            session.add_all([cosmetic, domestic, car, training])
            await session.flush()  # Get IDs without committing
            
            # COSMETIC subcategories and services
            mens_hair_sub = ServiceSubcategory(
                category_id=cosmetic.id,
                name="Men's Hair",
                description="Haircuts and styling for men"
            )
            womens_hair_sub = ServiceSubcategory(
                category_id=cosmetic.id,
                name="Women's Hair",
                description="Haircuts, styling, and color for women"
            )
            nails_sub = ServiceSubcategory(
                category_id=cosmetic.id,
                name="Nails & Lashes",
                description="Manicures, pedicures, nails, lashes and brows"
            )
            makeup_sub = ServiceSubcategory(
                category_id=cosmetic.id,
                name="Makeup",
                description="Makeup application and services"
            )
            massage_sub = ServiceSubcategory(
                category_id=cosmetic.id,
                name="Massage",
                description="Massage therapy and relaxation"
            )
            
            session.add_all([mens_hair_sub, womens_hair_sub, nails_sub, makeup_sub, massage_sub])
            await session.flush()
            
            # Cosmetic services
            cosmetic_services = [
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=mens_hair_sub.id,
                    name="Classic Haircut",
                    description="Professional haircut with clean lines",
                    pricing_type=PricingType.FIXED,
                    base_price_min=25.0,
                    base_price_max=35.0,
                    estimated_duration_minutes=30
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=mens_hair_sub.id,
                    name="Cut & Shave",
                    description="Haircut plus straight razor shave",
                    pricing_type=PricingType.FIXED,
                    base_price_min=45.0,
                    base_price_max=55.0,
                    estimated_duration_minutes=45
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=mens_hair_sub.id,
                    name="Hair Dye",
                    description="Professional hair coloring",
                    pricing_type=PricingType.FIXED,
                    base_price_min=35.0,
                    base_price_max=50.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=womens_hair_sub.id,
                    name="Hair Dye",
                    description="Professional hair coloring and toning",
                    pricing_type=PricingType.FIXED,
                    base_price_min=50.0,
                    base_price_max=75.0,
                    estimated_duration_minutes=90
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=womens_hair_sub.id,
                    name="Braids",
                    description="Box braids, cornrows, and other braided styles",
                    pricing_type=PricingType.FIXED,
                    base_price_min=60.0,
                    base_price_max=120.0,
                    estimated_duration_minutes=180
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=womens_hair_sub.id,
                    name="Blowout",
                    description="Professional hair blow dry and styling",
                    pricing_type=PricingType.FIXED,
                    base_price_min=35.0,
                    base_price_max=50.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=nails_sub.id,
                    name="Gel Manicure",
                    description="Long-lasting gel nail manicure",
                    pricing_type=PricingType.FIXED,
                    base_price_min=30.0,
                    base_price_max=40.0,
                    estimated_duration_minutes=45
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=nails_sub.id,
                    name="Gel Pedicure",
                    description="Long-lasting gel nail pedicure",
                    pricing_type=PricingType.FIXED,
                    base_price_min=35.0,
                    base_price_max=45.0,
                    estimated_duration_minutes=45
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=nails_sub.id,
                    name="Lash Extensions",
                    description="Application of individual or volume lashes",
                    pricing_type=PricingType.FIXED,
                    base_price_min=80.0,
                    base_price_max=150.0,
                    estimated_duration_minutes=120
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=nails_sub.id,
                    name="Eyebrow Design",
                    description="Eyebrow shaping, threading, or microblading",
                    pricing_type=PricingType.FIXED,
                    base_price_min=20.0,
                    base_price_max=35.0,
                    estimated_duration_minutes=30
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=makeup_sub.id,
                    name="Makeup Application",
                    description="Professional makeup for events or daily wear",
                    pricing_type=PricingType.FIXED,
                    base_price_min=40.0,
                    base_price_max=75.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=makeup_sub.id,
                    name="Bridal Makeup",
                    description="Professional bridal makeup package",
                    pricing_type=PricingType.FIXED,
                    base_price_min=100.0,
                    base_price_max=150.0,
                    estimated_duration_minutes=90
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=massage_sub.id,
                    name="Swedish Massage",
                    description="Relaxing full-body Swedish massage",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=60.0,
                    base_price_max=80.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=cosmetic.id,
                    subcategory_id=massage_sub.id,
                    name="Deep Tissue Massage",
                    description="Therapeutic deep tissue massage",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=70.0,
                    base_price_max=90.0,
                    estimated_duration_minutes=60
                ),
            ]
            
            session.add_all(cosmetic_services)
            await session.flush()
            
            # DOMESTIC subcategories and services
            deep_clean_sub = ServiceSubcategory(
                category_id=domestic.id,
                name="Deep Clean",
                description="Thorough deep cleaning services"
            )
            standard_clean_sub = ServiceSubcategory(
                category_id=domestic.id,
                name="Standard Clean",
                description="Regular cleaning services"
            )
            laundry_sub = ServiceSubcategory(
                category_id=domestic.id,
                name="Laundry",
                description="Laundry and ironing services"
            )
            
            session.add_all([deep_clean_sub, standard_clean_sub, laundry_sub])
            await session.flush()
            
            # Domestic services
            domestic_services = [
                Service(
                    category_id=domestic.id,
                    subcategory_id=deep_clean_sub.id,
                    name="Move-In/Out Deep Clean",
                    description="Complete deep cleaning of entire home",
                    pricing_type=PricingType.PROVIDER_DEFINED,
                    base_price_min=200.0,
                    base_price_max=500.0,
                    estimated_duration_minutes=360
                ),
                Service(
                    category_id=domestic.id,
                    subcategory_id=deep_clean_sub.id,
                    name="Deep Bathroom Clean",
                    description="Deep cleaning of bathrooms",
                    pricing_type=PricingType.FIXED,
                    base_price_min=50.0,
                    base_price_max=80.0,
                    estimated_duration_minutes=90
                ),
                Service(
                    category_id=domestic.id,
                    subcategory_id=standard_clean_sub.id,
                    name="Weekly House Clean",
                    description="Regular weekly house cleaning",
                    pricing_type=PricingType.FIXED,
                    base_price_min=80.0,
                    base_price_max=150.0,
                    estimated_duration_minutes=120
                ),
                Service(
                    category_id=domestic.id,
                    subcategory_id=standard_clean_sub.id,
                    name="Biweekly Clean",
                    description="Cleaning every two weeks",
                    pricing_type=PricingType.FIXED,
                    base_price_min=70.0,
                    base_price_max=120.0,
                    estimated_duration_minutes=120
                ),
                Service(
                    category_id=domestic.id,
                    subcategory_id=laundry_sub.id,
                    name="Laundry Service",
                    description="Wash, dry, and fold laundry",
                    pricing_type=PricingType.FIXED,
                    base_price_min=25.0,
                    base_price_max=50.0,
                    estimated_duration_minutes=120
                ),
                Service(
                    category_id=domestic.id,
                    subcategory_id=laundry_sub.id,
                    name="Ironing Service",
                    description="Professional ironing and pressing",
                    pricing_type=PricingType.FIXED,
                    base_price_min=20.0,
                    base_price_max=40.0,
                    estimated_duration_minutes=90
                ),
            ]
            
            session.add_all(domestic_services)
            await session.flush()
            
            # CAR subcategories and services
            detailed_wash_sub = ServiceSubcategory(
                category_id=car.id,
                name="Detailed Wash",
                description="Complete vehicle detailing"
            )
            quick_wash_sub = ServiceSubcategory(
                category_id=car.id,
                name="Quick Wash",
                description="Fast car washing"
            )
            
            session.add_all([detailed_wash_sub, quick_wash_sub])
            await session.flush()
            
            # Car services
            car_services = [
                Service(
                    category_id=car.id,
                    subcategory_id=detailed_wash_sub.id,
                    name="Full Detail",
                    description="Complete exterior and interior detailing",
                    pricing_type=PricingType.FIXED,
                    base_price_min=120.0,
                    base_price_max=200.0,
                    estimated_duration_minutes=180
                ),
                Service(
                    category_id=car.id,
                    subcategory_id=detailed_wash_sub.id,
                    name="Exterior Detail",
                    description="Professional exterior detailing and wax",
                    pricing_type=PricingType.FIXED,
                    base_price_min=80.0,
                    base_price_max=120.0,
                    estimated_duration_minutes=120
                ),
                Service(
                    category_id=car.id,
                    subcategory_id=quick_wash_sub.id,
                    name="Quick Wash",
                    description="Fast exterior wash and dry",
                    pricing_type=PricingType.FIXED,
                    base_price_min=25.0,
                    base_price_max=40.0,
                    estimated_duration_minutes=30
                ),
                Service(
                    category_id=car.id,
                    subcategory_id=quick_wash_sub.id,
                    name="Interior Vacuum",
                    description="Vacuum and interior cleaning",
                    pricing_type=PricingType.FIXED,
                    base_price_min=30.0,
                    base_price_max=50.0,
                    estimated_duration_minutes=45
                ),
            ]
            
            session.add_all(car_services)
            await session.flush()
            
            # TRAINING subcategories and services
            no_equipment_sub = ServiceSubcategory(
                category_id=training.id,
                name="Bodyweight Training",
                description="Fitness training without equipment"
            )
            with_equipment_sub = ServiceSubcategory(
                category_id=training.id,
                name="Equipment Training",
                description="Training with gym equipment"
            )
            
            session.add_all([no_equipment_sub, with_equipment_sub])
            await session.flush()
            
            # Training services
            training_services = [
                Service(
                    category_id=training.id,
                    subcategory_id=no_equipment_sub.id,
                    name="Personal Training Session",
                    description="One-on-one personal training (no equipment)",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=50.0,
                    base_price_max=80.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=training.id,
                    subcategory_id=no_equipment_sub.id,
                    name="Yoga Class",
                    description="Private or group yoga session",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=40.0,
                    base_price_max=60.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=training.id,
                    subcategory_id=with_equipment_sub.id,
                    name="Gym Training Session",
                    description="Personal training with gym equipment",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=60.0,
                    base_price_max=100.0,
                    estimated_duration_minutes=60
                ),
                Service(
                    category_id=training.id,
                    subcategory_id=with_equipment_sub.id,
                    name="CrossFit Training",
                    description="CrossFit style training with equipment",
                    pricing_type=PricingType.HOURLY,
                    base_price_min=70.0,
                    base_price_max=110.0,
                    estimated_duration_minutes=60
                ),
            ]
            
            session.add_all(training_services)
            
            await session.commit()
            print("✅ Services seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding services: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_services())
