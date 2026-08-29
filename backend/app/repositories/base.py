from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from app.schemas.models import (
    Service,
    DocumentType,
    UserDocument,
    Application,
    LifeEvent,
    ContextAnswers,
    DocumentStatus
)


class BaseRepository(ABC):

    # Services
    @abstractmethod
    def get_all_services(self) -> List[Service]:
        pass

    @abstractmethod
    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        pass

    # Documents
    @abstractmethod
    def get_all_document_types(self) -> List[DocumentType]:
        pass

    @abstractmethod
    def get_document_type(self, doc_type_id: str) -> Optional[DocumentType]:
        pass

    @abstractmethod
    def get_user_documents(self, user_id: str) -> Dict[str, UserDocument]:
        pass

    @abstractmethod
    def toggle_user_document_status(
        self, user_id: str, document_type_id: str, status: Optional[DocumentStatus] = None
    ) -> Optional[UserDocument]:
        pass

    # Applications
    @abstractmethod
    def get_user_applications(self, user_id: str) -> List[Application]:
        pass

    @abstractmethod
    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        pass

    # Life Events & Sessions
    @abstractmethod
    def save_life_event(self, life_event: LifeEvent) -> LifeEvent:
        pass

    @abstractmethod
    def get_life_event(self, event_id: str) -> Optional[LifeEvent]:
        pass

    @abstractmethod
    def update_life_event_context(self, event_id: str, context: ContextAnswers) -> Optional[LifeEvent]:
        pass

    @abstractmethod
    def reset_demo_state(self) -> None:
        pass
