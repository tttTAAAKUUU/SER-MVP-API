"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    CustomerSignupRequest, ProviderSignupRequest, LoginRequest, TokenResponse, UserResponse, RegisterRequest
)
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/customer/signup", response_model=TokenResponse)
async def customer_signup(request: CustomerSignupRequest, db: AsyncSession = Depends(get_db)):
    """Customer signup"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=request.email,
        phone=request.phone,
        first_name=request.first_name,
        last_name=request.last_name,
        password_hash=hash_password(request.password),
        role=UserRole.CUSTOMER,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({
        "sub": str(user.id),
        "role": UserRole.CUSTOMER.value
    })
    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": UserRole.CUSTOMER.value
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=UserRole.CUSTOMER.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.post("/provider/signup", response_model=TokenResponse)
async def provider_signup(request: ProviderSignupRequest, db: AsyncSession = Depends(get_db)):
    """Provider signup"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=request.email,
        phone=request.phone,
        first_name=request.first_name,
        last_name=request.last_name,
        password_hash=hash_password(request.password),
        role=UserRole.PROVIDER,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({
        "sub": str(user.id),
        "role": UserRole.PROVIDER.value
    })
    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": UserRole.PROVIDER.value
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=UserRole.PROVIDER.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint"""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # If role is provided, validate it matches
    if request.role and user.role.value != request.role.upper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User role mismatch. User is {user.role.value}, not {request.role}"
        )
    
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Unified registration endpoint for customers, providers, and businesses"""
    try:
        # Validate password confirmation
        if request.password_confirm and request.password != request.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if user exists by email
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Determine role
        role_upper = request.role.upper() if request.role else "CUSTOMER"
        
        if role_upper == "CUSTOMER":
            user_role = UserRole.CUSTOMER
            first_name = request.first_name or "User"
            last_name = request.last_name or ""
            phone = request.phone or ""
        elif role_upper == "PROVIDER":
            user_role = UserRole.PROVIDER
            first_name = request.first_name or "Provider"
            last_name = request.last_name or ""
            phone = request.phone or ""
        elif role_upper == "BUSINESS":
            user_role = UserRole.BUSINESS
            first_name = request.owner_first_name or "Business"
            last_name = request.owner_last_name or ""
            phone = request.owner_phone or ""
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be CUSTOMER, PROVIDER, or BUSINESS"
            )
        
        # Create user
        user = User(
            email=request.email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(request.password),
            role=user_role,
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Generate tokens
        access_token = create_access_token({
            "sub": str(user.id),
            "role": user_role.value
        })
        refresh_token = create_refresh_token({
            "sub": str(user.id),
            "role": user_role.value
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=user_role.value,
                is_active=user.is_active,
                created_at=user.created_at,
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Get current user from token"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = authorization.split(" ")[1]
        token_data = decode_token(token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = int(token_data.sub)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )
