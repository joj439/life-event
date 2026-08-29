from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.models import (
    LifeEvent,
    ContextAnswers,
    Service,
    UserDocument,
    Application,
    DocumentStatus
)


class AnalyzeLifeEventRequest(BaseModel):
    message: str = Field(..., description="Natural language description of the citizen's life event.")


class ContextAnswersRequest(BaseModel):
    # Relocation
    permanent: Optional[bool] = Field(default=True, description="Is this a permanent move?")
    owns_vehicle: Optional[bool] = Field(default=False, description="Do you own a motor vehicle?")
    receives_pds: Optional[bool] = Field(default=False, description="Are you currently receiving government food/PDS benefits?")
    
    # Financial Fraud
    unauthorized_txn: Optional[bool] = Field(default=True, description="Was the financial transaction unauthorized?")
    has_txn_id: Optional[bool] = Field(default=True, description="Do you have the transaction or reference ID?")
    knows_bank: Optional[bool] = Field(default=True, description="Do you know which bank or payment app was involved?")
    
    # Marriage
    details_changed: Optional[bool] = Field(default=True, description="Have your personal details or name changed?")
    address_changed: Optional[bool] = Field(default=False, description="Has your residential address changed?")
    needs_marriage_cert: Optional[bool] = Field(default=True, description="Do you need guidance on Marriage Registration?")
    
    # Family Death
    looking_for_death_cert: Optional[bool] = Field(default=True, description="Are you looking for Death Registration guidance?")
    pension_or_benefits_involved: Optional[bool] = Field(default=True, description="Are government pension or survivor benefits involved?")


class ToggleDocumentRequest(BaseModel):
    document_type_id: str = Field(..., description="The ID of the document type (e.g. vehicle_reg, identity_proof).")
    status: Optional[DocumentStatus] = Field(default=None, description="Explicit target status ('available' or 'missing'). If omitted, toggles state.")


class ContextResponse(BaseModel):
    life_event: LifeEvent
    context: ContextAnswers
    recommended_services: List[Service]
    readiness_summary: Dict[str, Any]


class DocumentListResponse(BaseModel):
    documents: List[UserDocument]
    summary: Dict[str, Any]


class JourneySummaryResponse(BaseModel):
    life_event: Optional[LifeEvent] = None
    context: Optional[ContextAnswers] = None
    services: List[Service] = Field(default_factory=list)
    documents: DocumentListResponse
    applications: List[Application] = Field(default_factory=list)
