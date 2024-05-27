"""
Smart Grid IoT Analytics - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.services.mqtt_service import MQTTService
from app.services.scheduler_service import SchedulerService
from app.init_data import initialize_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
mqtt_service = None
scheduler_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global mqtt_service, scheduler_service

    # Startup
    logger.info("Starting Smart Grid IoT Analytics Backend...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Initialize database with sample data
    try:
        initialize_database()
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

    # Initialize MQTT service
    mqtt_service = MQTTService()
    await mqtt_service.start()
    logger.info("MQTT service started")

    # Initialize scheduler service
    scheduler_service = SchedulerService()
    scheduler_service.start()
    logger.info("Scheduler service started")

    yield

    # Shutdown
    logger.info("Shutting down Smart Grid IoT Analytics Backend...")

    if mqtt_service:
        await mqtt_service.stop()
        logger.info("MQTT service stopped")

    if scheduler_service:
        scheduler_service.stop()
        logger.info("Scheduler service stopped")


# Create FastAPI application
app = FastAPI(
    title="Smart Grid IoT Analytics API",
    description="A comprehensive IoT analytics platform for smart grid energy management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Grid IoT Analytics API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.core.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

        return {
            "status": "healthy",
            "database": "connected",
            "mqtt": "connected" if mqtt_service and mqtt_service.is_connected else "disconnected",
            "scheduler": "running" if scheduler_service and scheduler_service.is_running else "stopped"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
