from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.schemas.models import Service
from app.engines.document_engine import compute_service_readiness
from app.repositories import repo
from app.data.seed_data import DEMO_USER_ID

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=List[Service])
def get_all_services_endpoint(life_event: Optional[str] = None):
    """
    Get all available government services, optionally filtered by life event.
    Each service includes real-time document readiness for the user.
    """
    services = repo.get_all_services()
    user_docs = repo.get_user_documents(DEMO_USER_ID)

    results = []
    for svc in services:
        if life_event and life_event.lower() not in [e.lower() for e in svc.applicable_life_events]:
            continue
        readiness = compute_service_readiness(svc.required_document_ids, user_docs, svc.id)
        service_copy = svc.model_copy(update={"readiness": readiness})
        results.append(service_copy)

    return results


@router.get("/{service_id}", response_model=Service)
def get_service_by_id_endpoint(service_id: str):
    """
    Get deep details for a specific service, including step-by-step guidance,
    required documents, and document readiness.
    """
    service = repo.get_service_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found in the service catalog."
        )

    user_docs = repo.get_user_documents(DEMO_USER_ID)
    readiness = compute_service_readiness(service.required_document_ids, user_docs, service.id)
    return service.model_copy(update={"readiness": readiness})
