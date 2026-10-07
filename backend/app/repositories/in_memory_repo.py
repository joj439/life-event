import copy
from typing import List, Optional, Dict
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.schemas.models import (
    Service,
    DocumentType,
    UserDocument,
    Application,
    LifeEvent,
    ContextAnswers,
    DocumentStatus
)
from app.data.seed_data import (
    SEED_SERVICES,
    SEED_DOCUMENT_TYPES,
    SEED_USER_DOCUMENTS,
    SEED_APPLICATIONS,
    DEMO_USER_ID
)


class InMemoryRepository(BaseRepository):
    def __init__(self):
        self.reset_demo_state()

    def reset_demo_state(self) -> None:
        self.services: Dict[str, Service] = copy.deepcopy(SEED_SERVICES)
        self.document_types: Dict[str, DocumentType] = copy.deepcopy(SEED_DOCUMENT_TYPES)
        self.user_documents: Dict[str, Dict[str, UserDocument]] = {
            DEMO_USER_ID: copy.deepcopy(SEED_USER_DOCUMENTS)
        }
        self.applications: Dict[str, Application] = copy.deepcopy(SEED_APPLICATIONS)
        self.life_events: Dict[str, LifeEvent] = {}

    def get_all_services(self) -> List[Service]:
        return list(self.services.values())

    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        return self.services.get(service_id)

    def get_all_document_types(self) -> List[DocumentType]:
        return list(self.document_types.values())

    def get_document_type(self, doc_type_id: str) -> Optional[DocumentType]:
        return self.document_types.get(doc_type_id)

    def get_user_documents(self, user_id: str) -> Dict[str, UserDocument]:
        if user_id not in self.user_documents:
            # Initialize with default missing state for new users
            self.user_documents[user_id] = {
                dt_id: UserDocument(
                    id=f"udoc_{user_id}_{dt_id}",
                    user_id=user_id,
                    document_type_id=dt_id,
                    document_name=dt.name,
                    status=DocumentStatus.MISSING,
                    is_information_item=dt.is_information_item
                )
                for dt_id, dt in self.document_types.items()
            }
        return self.user_documents[user_id]

    def toggle_user_document_status(
        self, user_id: str, document_type_id: str, status: Optional[DocumentStatus] = None
    ) -> Optional[UserDocument]:
        user_docs = self.get_user_documents(user_id)
        if document_type_id not in user_docs:
            doc_type = self.get_document_type(document_type_id)
            if not doc_type:
                return None
            user_docs[document_type_id] = UserDocument(
                id=f"udoc_{user_id}_{document_type_id}",
                user_id=user_id,
                document_type_id=document_type_id,
                document_name=doc_type.name,
                status=DocumentStatus.MISSING,
                is_information_item=doc_type.is_information_item
            )

        doc = user_docs[document_type_id]
        if status is not None:
            doc.status = status
        else:
            doc.status = (
                DocumentStatus.MISSING
                if doc.status == DocumentStatus.AVAILABLE
                else DocumentStatus.AVAILABLE
            )
        doc.updated_at = datetime.now(timezone.utc).isoformat()
        return doc

    def get_user_applications(self, user_id: str) -> List[Application]:
        return [app for app in self.applications.values() if app.user_id == user_id]

    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        return self.applications.get(app_id)

    def save_life_event(self, life_event: LifeEvent) -> LifeEvent:
        self.life_events[life_event.id] = life_event
        # Initialize document states for DEMO_USER_ID based on event scenario:
        if life_event.event_type == "relocation":
            # Preset demo state for the relocation walkthrough (2 of 4 verified)
            self.user_documents[DEMO_USER_ID] = copy.deepcopy(SEED_USER_DOCUMENTS)
        else:
            # For any newly analyzed non-relocation scenario (fraud, marriage, death),
            # all documents start as Not Yet Verified / Missing (0 of N)
            self.user_documents[DEMO_USER_ID] = {
                dt_id: UserDocument(
                    id=f"udoc_{DEMO_USER_ID}_{dt_id}",
                    user_id=DEMO_USER_ID,
                    document_type_id=dt_id,
                    document_name=dt.name,
                    status=DocumentStatus.MISSING,
                    is_information_item=dt.is_information_item
                )
                for dt_id, dt in self.document_types.items()
            }
        return life_event

    def get_life_event(self, event_id: str) -> Optional[LifeEvent]:
        return self.life_events.get(event_id)

    def get_latest_life_event(self) -> Optional[LifeEvent]:
        if not self.life_events:
            return None
        return list(self.life_events.values())[-1]

    def update_life_event_context(self, event_id: str, context: ContextAnswers) -> Optional[LifeEvent]:
        event = self.life_events.get(event_id)
        if event:
            event.context = context
        return event


# Backward-compatible global singleton: delegates dynamically to factory
from app.repositories.factory import repo
