"""Services endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.database import get_db
from app.models.service import ServiceCategory, ServiceSubcategory, Service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/services", tags=["services"])


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    pricing_type: str
    base_price_min: Optional[float]
    base_price_max: Optional[float]
    estimated_duration_minutes: Optional[int]
    
    class Config:
        from_attributes = True


class SubcategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    services: List[ServiceResponse]
    
    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    color: Optional[str]
    subcategories: List[SubcategoryResponse]
    
    class Config:
        from_attributes = True


class CategorySimpleResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    color: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/categories", response_model=List[CategorySimpleResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all service categories"""
    result = await db.execute(select(ServiceCategory).order_by(ServiceCategory.name))
    categories = result.scalars().all()
    return categories


@router.get("/categories/{category_slug}", response_model=CategoryResponse)
async def get_category_with_services(
    category_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get category with subcategories and services"""
    result = await db.execute(
        select(ServiceCategory)
        .where(ServiceCategory.slug == category_slug)
        .options(
            joinedload(ServiceCategory.subcategories).selectinload(
                ServiceSubcategory.services
            )
        )
    )
    category = result.unique().scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.get("/", response_model=List[ServiceResponse])
async def get_all_services(db: AsyncSession = Depends(get_db)):
    """Get all services"""
    result = await db.execute(
        select(Service)
        .where(Service.is_active == True)
        .order_by(Service.name)
    )
    services = result.scalars().all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific service"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service
