from fastapi import APIRouter, HTTPException, status
from app.schemas.assistant import ChatRequest, ChatResponse
from app.engines.assistant_engine import generate_assistant_response

router = APIRouter(prefix="/assistant", tags=["Ask LifeEvent Assistant"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_assistant(payload: ChatRequest):
    """
    Context-aware Ask LifeEvent AI assistant endpoint.
    Retrieves structured context from the backend repository and answers citizen queries
    without hallucinating or altering deterministic service recommendations.
    """
    message = payload.message.strip()
    if not message:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid question for Ask LifeEvent."
        )

    response_data = generate_assistant_response(
        message=message,
        life_event_id=payload.life_event_id,
        service_id=payload.service_id
    )

    return ChatResponse(
        answer=response_data["answer"],
        service_id=response_data.get("service_id"),
        source=response_data.get("source", "deterministic_engine"),
        context_used=response_data.get("context_used", {})
    )
