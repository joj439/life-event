from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from app.schemas.requests import DocumentListResponse, ToggleDocumentRequest
from app.schemas.models import UserDocument, DocumentStatus, ContextAnswers
from app.engines.document_engine import compute_overall_readiness
from app.engines.service_engine import evaluate_services_for_life_event
from app.repositories import repo
from app.data.seed_data import DEMO_USER_ID

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
def get_documents_endpoint(event_id: Optional[str] = None):
    """
    Get all tracked user documents and overall readiness metrics for the active scenario.
    """
    user_docs = repo.get_user_documents(DEMO_USER_ID)
    doc_list = list(user_docs.values())

    active_event = repo.get_life_event(event_id) if event_id else repo.get_latest_life_event()

    if active_event:
        ctx = active_event.context or ContextAnswers(
            permanent=True, owns_vehicle=True, receives_pds=True,
            unauthorized_txn=True, has_txn_id=True, knows_bank=True,
            details_changed=True, needs_marriage_cert=True,
            looking_for_death_cert=True, pension_or_benefits_involved=True
        )
        services = evaluate_services_for_life_event(
            active_event.event_type, active_event.origin, active_event.destination, ctx, user_docs
        )
        all_req_doc_ids = []
        for svc in services:
            all_req_doc_ids.extend(svc.required_document_ids)

        req_ids = list(set(all_req_doc_ids)) if all_req_doc_ids else ["identity_proof", "address_proof", "vehicle_reg", "pds_ration_card"]
        summary = compute_overall_readiness(req_ids, user_docs)
        summary["is_demo_preset"] = (active_event.event_type == "relocation")
    else:
        # Default relocation baseline (2 of 4 ready demo preset)
        relocation_req_ids = ["identity_proof", "address_proof", "vehicle_reg", "pds_ration_card"]
        summary = compute_overall_readiness(relocation_req_ids, user_docs)
        summary["is_demo_preset"] = True

    return DocumentListResponse(
        documents=doc_list,
        summary=summary
    )


@router.post("/toggle", response_model=UserDocument)
def toggle_document_status_endpoint(payload: ToggleDocumentRequest):
    """
    Toggle a document's availability state (Available <-> Needed) or set it explicitly.
    """
    updated_doc = repo.toggle_user_document_status(
        user_id=DEMO_USER_ID,
        document_type_id=payload.document_type_id,
        status=payload.status
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type with ID '{payload.document_type_id}' does not exist."
        )
    return updated_doc


@router.post("/upload", response_model=UserDocument)
async def mock_upload_document_endpoint(
    document_type_id: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Simple mock document upload endpoint. Marks the document as Available.
    """
    updated_doc = repo.toggle_user_document_status(
        user_id=DEMO_USER_ID,
        document_type_id=document_type_id,
        status=DocumentStatus.AVAILABLE
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type with ID '{document_type_id}' does not exist."
        )
    return updated_doc
