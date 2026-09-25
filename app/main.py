"""SIR Backend - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, services_new, bookings, providers, bidding, notifications, job_status, ratings, service_providers

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="South African service-at-home marketplace",
    version=settings.api_version,
    debug=settings.debug,
)

# Expanded CORS origins for new frontends (includes common dev ports and Vercel)
cors_origins = [
    # Local development
    "http://localhost:3000",  # ser frontend
    "http://localhost:3001",  # ser_dashboard frontend
    "http://localhost:3002",  # store portal
    "http://localhost:3003",  # backup port
    "http://localhost:3004",  # backup port
    "http://localhost:3005",  # backup port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    # Vercel deployment
    "https://*.vercel.app",  # All Vercel preview deployments
    "https://store-portal.vercel.app",  # Production store portal (update with actual domain)
    # Add your production domains here
    # "https://your-store-portal-domain.com",
    # "https://your-api-domain.com",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(services_new.router)
app.include_router(bookings.router)
app.include_router(bidding.router)
app.include_router(job_status.router)
app.include_router(notifications.router)
app.include_router(ratings.router)
app.include_router(providers.router)
app.include_router(service_providers.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SIR API",
        "docs": "/docs",
        "version": settings.api_version,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
