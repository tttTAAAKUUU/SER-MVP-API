"""Service endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.service import ServiceCategory, Service
from app.schemas.service import ServiceCategoryResponse, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def get_all_services(db: AsyncSession = Depends(get_db)):
    """Get all services"""
    result = await db.execute(select(Service))
    services = result.scalars().all()
    return services


@router.get("/categories", response_model=list[ServiceCategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all service categories"""
    result = await db.execute(select(ServiceCategory))
    categories = result.scalars().all()
    return categories


@router.get("/categories/{category_id}", response_model=ServiceCategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Get category by ID"""
    result = await db.execute(select(ServiceCategory).where(ServiceCategory.id == category_id))
    category = result.scalar_one_or_none()
    return category


@router.get("/categories/{category_id}/services", response_model=list[ServiceResponse])
async def get_services_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Get services within a category"""
    result = await db.execute(
        select(Service).where(Service.category_id == category_id)
    )
    services = result.scalars().all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    """Get service by ID"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    return service
