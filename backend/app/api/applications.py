from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.models import Application
from app.repositories import repo
from app.data.seed_data import DEMO_USER_ID

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[Application])
def get_applications_endpoint():
    """
    Get all tracked government service applications for the demo user.
    """
    return repo.get_user_applications(DEMO_USER_ID)


@router.get("/{app_id}", response_model=Application)
def get_application_by_id_endpoint(app_id: str):
    """
    Get deep timeline and status breakdown for a specific tracked application.
    """
    application = repo.get_application_by_id(app_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with tracking ID '{app_id}' was not found."
        )
    return application
