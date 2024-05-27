"""
API v1 Router
Main router for all API endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import energy, pricing, renewable, meters, predictions, auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(energy.router, prefix="/energy", tags=["energy"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(renewable.router, prefix="/renewable", tags=["renewable"])
api_router.include_router(meters.router, prefix="/meters", tags=["meters"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
