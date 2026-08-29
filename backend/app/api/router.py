from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.life_events import router as life_events_router
from app.api.services import router as services_router
from app.api.documents import router as documents_router
from app.api.applications import router as applications_router
from app.api.demo import router as demo_router
from app.api.assistant import router as assistant_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(life_events_router)
api_router.include_router(services_router)
api_router.include_router(documents_router)
api_router.include_router(applications_router)
api_router.include_router(assistant_router)
api_router.include_router(demo_router)
