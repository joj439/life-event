from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's query for Ask LifeEvent.")
    life_event_id: Optional[str] = Field(default=None, description="Current life event ID from the session.")
    service_id: Optional[str] = Field(default=None, description="Optional service ID if asking in the context of a specific service.")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The assistant's contextual answer.")
    service_id: Optional[str] = Field(default=None, description="The service ID in context, if applicable.")
    source: str = Field(default="deterministic_engine", description="Source of response ('deterministic_engine' or 'gemini_llm').")
    context_used: Dict[str, Any] = Field(default_factory=dict, description="Summary of structured context used to formulate the answer.")
