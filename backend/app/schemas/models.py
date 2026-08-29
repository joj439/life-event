from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    NOT_STARTED = "not_started"
    READY = "ready"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACTION_REQUIRED = "action_required"
    COMPLETED = "completed"


class DocumentStatus(str, Enum):
    AVAILABLE = "available"
    MISSING = "missing"


class DocumentType(BaseModel):
    id: str
    code: str
    name: str
    description: str
    accepted_examples: List[str] = Field(default_factory=list)
    is_information_item: bool = False


class UserDocument(BaseModel):
    id: str
    user_id: str
    document_type_id: str
    document_name: str
    status: DocumentStatus = DocumentStatus.MISSING
    updated_at: Optional[str] = None
    is_information_item: bool = False


class DocumentReadiness(BaseModel):
    service_id: Optional[str] = None
    required_count: int
    available_count: int
    percentage: int
    is_ready: bool
    required_documents: List[DocumentType] = Field(default_factory=list)
    available_documents: List[DocumentType] = Field(default_factory=list)
    missing_documents: List[DocumentType] = Field(default_factory=list)


class Service(BaseModel):
    id: str
    name: str
    category: str
    description: str
    why_relevant: str
    required_document_ids: List[str] = Field(default_factory=list)
    basic_steps: List[str] = Field(default_factory=list)
    applicable_life_events: List[str] = Field(default_factory=lambda: ["relocation"])
    portal_name: str
    portal_url: str
    is_mock_portal: bool = True
    estimated_processing_days: int = 7
    readiness: Optional[DocumentReadiness] = None
    mock_status: Optional[ApplicationStatus] = None


class ContextAnswers(BaseModel):
    # Relocation
    permanent: Optional[bool] = True
    owns_vehicle: Optional[bool] = False
    receives_pds: Optional[bool] = False
    
    # Financial Fraud
    unauthorized_txn: Optional[bool] = True
    has_txn_id: Optional[bool] = True
    knows_bank: Optional[bool] = True
    
    # Marriage
    details_changed: Optional[bool] = True
    address_changed: Optional[bool] = False
    needs_marriage_cert: Optional[bool] = True
    
    # Family Death
    looking_for_death_cert: Optional[bool] = True
    pension_or_benefits_involved: Optional[bool] = True


class LifeEvent(BaseModel):
    id: str
    raw_input: str
    event_type: str = "relocation"
    origin: Optional[str] = None
    destination: Optional[str] = None
    confidence: float = 1.0
    is_supported: bool = True
    message: str = "Event detected"
    context: Optional[ContextAnswers] = None


class ApplicationStep(BaseModel):
    step_order: int
    title: str
    description: str
    is_completed: bool = False


class Application(BaseModel):
    id: str
    user_id: str
    service_id: str
    service_name: str
    category: str
    status: ApplicationStatus = ApplicationStatus.NOT_STARTED
    tracking_number: str
    applied_date: Optional[str] = None
    estimated_completion_date: Optional[str] = None
    remarks: str = ""
    steps: List[ApplicationStep] = Field(default_factory=list)
    is_mock: bool = True
