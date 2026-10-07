from fastapi import APIRouter
from app.repositories import repo

router = APIRouter(prefix="/demo", tags=["Demo Management"])


@router.post("/reset")
def reset_demo_state_endpoint():
    """
    Reset repository state back to pristine default demo state.
    """
    repo.reset_demo_state()
    return {
        "status": "success",
        "message": "Demo state successfully reset to default conditions."
    }
