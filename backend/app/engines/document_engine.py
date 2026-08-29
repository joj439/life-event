from typing import List, Dict, Optional
from app.schemas.models import (
    DocumentType,
    DocumentReadiness,
    DocumentStatus,
    UserDocument
)
from app.data.seed_data import SEED_DOCUMENT_TYPES


def compute_service_readiness(
    required_doc_ids: List[str],
    user_documents: Dict[str, UserDocument],
    service_id: Optional[str] = None
) -> DocumentReadiness:
    """
    Deterministically evaluates which required documents are available for a given service.
    """
    required_types: List[DocumentType] = []
    available_types: List[DocumentType] = []
    missing_types: List[DocumentType] = []

    for doc_id in required_doc_ids:
        doc_type = SEED_DOCUMENT_TYPES.get(doc_id)
        if not doc_type:
            continue
        required_types.append(doc_type)

        user_doc = user_documents.get(doc_id)
        if user_doc and user_doc.status == DocumentStatus.AVAILABLE:
            available_types.append(doc_type)
        else:
            missing_types.append(doc_type)

    req_count = len(required_types)
    avail_count = len(available_types)
    percentage = int((avail_count / req_count * 100)) if req_count > 0 else 100
    is_ready = (avail_count == req_count)

    return DocumentReadiness(
        service_id=service_id,
        required_count=req_count,
        available_count=avail_count,
        percentage=percentage,
        is_ready=is_ready,
        required_documents=required_types,
        available_documents=available_types,
        missing_documents=missing_types
    )


def compute_overall_readiness(
    relevant_required_doc_ids: List[str],
    user_documents: Dict[str, UserDocument]
) -> Dict[str, int]:
    """
    Computes overall summary readiness across all recommended services.
    """
    unique_req_ids = set(relevant_required_doc_ids)
    total_needed = len(unique_req_ids)
    available_count = 0

    for doc_id in unique_req_ids:
        user_doc = user_documents.get(doc_id)
        if user_doc and user_doc.status == DocumentStatus.AVAILABLE:
            available_count += 1

    percentage = int((available_count / total_needed * 100)) if total_needed > 0 else 100

    return {
        "total_required": total_needed,
        "total_available": available_count,
        "missing_count": total_needed - available_count,
        "percentage": percentage
    }
