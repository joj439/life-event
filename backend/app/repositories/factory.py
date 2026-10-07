import logging
from typing import Optional, List, Dict, Any
from app.config import settings
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

logger = logging.getLogger(__name__)

_in_memory_instance: Optional[BaseRepository] = None
_mysql_instance: Optional[BaseRepository] = None


def get_repository() -> BaseRepository:
    """
    Returns the configured repository instance.
    - When USE_MYSQL=False: returns the singleton InMemoryRepository.
    - When USE_MYSQL=True: verifies MySQL database connectivity and returns
      MySQLRepository. Raises a descriptive RuntimeError if connection fails.
      Does NOT silently fall back to in-memory mode.
    """
    global _in_memory_instance, _mysql_instance

    if settings.USE_MYSQL:
        from app.db.connection import verify_db_connection
        # Fail fast: verify database connectivity
        verify_db_connection()
        if _mysql_instance is None:
            from app.repositories.mysql_repo import MySQLRepository
            _mysql_instance = MySQLRepository()
        return _mysql_instance

    if _in_memory_instance is None:
        from app.repositories.in_memory_repo import InMemoryRepository
        _in_memory_instance = InMemoryRepository()
    return _in_memory_instance


def reset_repository_instances() -> None:
    """
    Reset repository singleton instances (useful during test lifecycle).
    """
    global _in_memory_instance, _mysql_instance
    _in_memory_instance = None
    _mysql_instance = None


class RepositoryProxy(BaseRepository):
    """
    Transparent repository proxy delegating calls dynamically to get_repository().
    Ensures seamless switching between InMemory and MySQL storage modes without
    rewriting API routes or breaking existing contracts.
    """

    def __getattr__(self, name: str) -> Any:
        return getattr(get_repository(), name)

    def get_all_services(self) -> List[Service]:
        return get_repository().get_all_services()

    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        return get_repository().get_service_by_id(service_id)

    def get_all_document_types(self) -> List[DocumentType]:
        return get_repository().get_all_document_types()

    def get_document_type(self, doc_type_id: str) -> Optional[DocumentType]:
        return get_repository().get_document_type(doc_type_id)

    def get_user_documents(self, user_id: str) -> Dict[str, UserDocument]:
        return get_repository().get_user_documents(user_id)

    def toggle_user_document_status(
        self, user_id: str, document_type_id: str, status: Optional[DocumentStatus] = None
    ) -> Optional[UserDocument]:
        return get_repository().toggle_user_document_status(user_id, document_type_id, status)

    def get_user_applications(self, user_id: str) -> List[Application]:
        return get_repository().get_user_applications(user_id)

    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        return get_repository().get_application_by_id(app_id)

    def save_life_event(self, life_event: LifeEvent) -> LifeEvent:
        return get_repository().save_life_event(life_event)

    def get_life_event(self, event_id: str) -> Optional[LifeEvent]:
        return get_repository().get_life_event(event_id)

    def update_life_event_context(self, event_id: str, context: ContextAnswers) -> Optional[LifeEvent]:
        return get_repository().update_life_event_context(event_id, context)

    def reset_demo_state(self) -> None:
        return get_repository().reset_demo_state()

    def get_latest_life_event(self) -> Optional[LifeEvent]:
        return get_repository().get_latest_life_event()


# Module-level singleton proxy
repo = RepositoryProxy()
