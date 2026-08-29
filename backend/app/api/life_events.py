from fastapi import APIRouter, HTTPException, status
from app.schemas.models import LifeEvent, ContextAnswers
from app.schemas.requests import AnalyzeLifeEventRequest, ContextAnswersRequest, ContextResponse
from app.engines.nlp_extractor import extract_life_event
from app.engines.service_engine import evaluate_services_for_life_event
from app.engines.document_engine import compute_overall_readiness
from app.repositories.in_memory_repo import repo
from app.data.seed_data import DEMO_USER_ID

router = APIRouter(prefix="/life-events", tags=["Life Events"])


@router.post("/analyze", response_model=LifeEvent, status_code=status.HTTP_200_OK)
def analyze_life_event_endpoint(payload: AnalyzeLifeEventRequest):
    """
    Analyze user's natural language input to detect the life event and extract entity slots.
    Supports: relocation, financial_fraud, marriage, family_death.
    """
    input_text = payload.message.strip()
    if not input_text:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid life event description (e.g., 'I moved from Mumbai to Pune.')."
        )

    life_event = extract_life_event(input_text)
    saved_event = repo.save_life_event(life_event)
    return saved_event


@router.get("/{event_id}", response_model=LifeEvent)
def get_life_event_endpoint(event_id: str):
    """
    Get a previously analyzed life event by its ID.
    """
    event = repo.get_life_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Life event with ID '{event_id}' not found."
        )
    return event


@router.post("/{event_id}/context", response_model=ContextResponse)
def submit_context_answers_endpoint(event_id: str, answers: ContextAnswersRequest):
    """
    Submit context answers and receive deterministically computed services
    and document/information readiness for the detected life event.
    """
    event = repo.get_life_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Life event with ID '{event_id}' not found."
        )

    context_domain = ContextAnswers(
        permanent=answers.permanent,
        owns_vehicle=answers.owns_vehicle,
        receives_pds=answers.receives_pds,
        unauthorized_txn=answers.unauthorized_txn,
        has_txn_id=answers.has_txn_id,
        knows_bank=answers.knows_bank,
        details_changed=answers.details_changed,
        address_changed=answers.address_changed,
        needs_marriage_cert=answers.needs_marriage_cert,
        looking_for_death_cert=answers.looking_for_death_cert,
        pension_or_benefits_involved=answers.pension_or_benefits_involved,
    )
    repo.update_life_event_context(event_id, context_domain)

    # Get current user documents
    user_docs = repo.get_user_documents(DEMO_USER_ID)

    # Compute deterministic recommendations across all supported event types
    recommended_services = evaluate_services_for_life_event(
        event_type=event.event_type,
        origin=event.origin,
        destination=event.destination,
        context=context_domain,
        user_documents=user_docs
    )

    # Aggregate required documents across all recommended services
    all_req_doc_ids = []
    for svc in recommended_services:
        all_req_doc_ids.extend(svc.required_document_ids)

    readiness_summary = compute_overall_readiness(all_req_doc_ids, user_docs)
    readiness_summary["is_demo_preset"] = (event.event_type == "relocation")

    return ContextResponse(
        life_event=event,
        context=context_domain,
        recommended_services=recommended_services,
        readiness_summary=readiness_summary
    )
