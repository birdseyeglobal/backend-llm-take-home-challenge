"""
Brand Voice API - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.database import create_db_tables

# Initialize FastAPI app
app = FastAPI(
    title="Brand Voice API",
    description=(
        "A REST API service for managing brand voice profiles "
        "and evaluations"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Brand Voice API starting up...")
    create_db_tables()
    print("✅ Database tables created")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("🛑 Brand Voice API shutting down...")