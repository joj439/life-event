from typing import List, Dict, Optional
from app.schemas.models import (
    Service,
    ContextAnswers,
    UserDocument,
    LifeEvent
)
from app.data.seed_data import SEED_SERVICES
from app.engines.document_engine import compute_service_readiness


def evaluate_services_for_relocation(
    origin: Optional[str],
    destination: Optional[str],
    context: ContextAnswers,
    user_documents: Dict[str, UserDocument]
) -> List[Service]:
    """
    Deterministic Service Recommendation Engine for Relocation.
    """
    origin_display = origin or "your previous city"
    dest_display = destination or "your new city"

    recommended_service_ids: List[str] = []

    # Rule 1: Address Update is ALWAYS relevant for relocation
    recommended_service_ids.append("address_update")

    # Rule 2: PDS / Ration Update is relevant ONLY IF user receives PDS benefits
    if context.receives_pds:
        recommended_service_ids.append("pds_update")

    # Rule 3: Vehicle Update is relevant ONLY IF user owns a vehicle
    if context.owns_vehicle:
        recommended_service_ids.append("vehicle_update")

    # Rule 4: Benefits Review is relevant as a general recommendation
    recommended_service_ids.append("benefits_review")

    result_services: List[Service] = []

    for svc_id in recommended_service_ids:
        base_service = SEED_SERVICES.get(svc_id)
        if not base_service:
            continue

        customized_why = base_service.why_relevant
        if svc_id == "address_update":
            customized_why = f"You indicated that you moved from {origin_display} to {dest_display}. Official address updating ensures timely local services, civic rights, and municipal communications."
        elif svc_id == "pds_update":
            customized_why = f"You indicated that you receive food/PDS benefits and moved from {origin_display} to {dest_display}. Updating your ration record helps transfer your quota to your new locality."
        elif svc_id == "vehicle_update":
            customized_why = f"You indicated vehicle ownership and relocation from {origin_display} to {dest_display}. Updating your vehicle RC records your new address with the local transport office."
        elif svc_id == "benefits_review":
            customized_why = f"Relocating from {origin_display} to {dest_display} allows you to explore municipal welfare programs, health schemes, and public services in your new area."

        readiness = compute_service_readiness(
            required_doc_ids=base_service.required_document_ids,
            user_documents=user_documents,
            service_id=svc_id
        )

        result_services.append(
            base_service.model_copy(
                update={"why_relevant": customized_why, "readiness": readiness}
            )
        )

    return result_services


def evaluate_services_for_financial_fraud(
    context: ContextAnswers,
    user_documents: Dict[str, UserDocument]
) -> List[Service]:
    """
    Deterministic Service Recommendation Engine for Financial Fraud / Cyber Crime.
    """
    recommended_service_ids = ["financial_fraud_reporting"]
    result_services: List[Service] = []

    for svc_id in recommended_service_ids:
        base_service = SEED_SERVICES.get(svc_id)
        if not base_service:
            continue

        readiness = compute_service_readiness(
            required_doc_ids=base_service.required_document_ids,
            user_documents=user_documents,
            service_id=svc_id
        )

        result_services.append(
            base_service.model_copy(update={"readiness": readiness})
        )

    return result_services


def evaluate_services_for_marriage(
    context: ContextAnswers,
    user_documents: Dict[str, UserDocument]
) -> List[Service]:
    """
    Deterministic Service Recommendation Engine for Marriage:
    - Marriage Registration: Always recommended for marriage life event.
    - Aadhaar Demographic Update: Recommended if personal/demographic details have changed.
    - Address Update: Recommended if residential address has changed.
    """
    recommended_service_ids = []

    if context.needs_marriage_cert is not False:
        recommended_service_ids.append("marriage_registration")

    if context.details_changed is not False:
        recommended_service_ids.append("aadhaar_update")

    if context.address_changed is True:
        recommended_service_ids.append("address_update")

    # If no specific flags triggered, guarantee the core marriage services
    if not recommended_service_ids:
        recommended_service_ids = ["marriage_registration", "aadhaar_update"]

    result_services: List[Service] = []

    for svc_id in recommended_service_ids:
        base_service = SEED_SERVICES.get(svc_id)
        if not base_service:
            continue

        customized_why = base_service.why_relevant
        if svc_id == "aadhaar_update":
            customized_why = "Your marriage may have resulted in changes to your demographic details. Aadhaar demographic update may therefore be relevant to update your name or marital particulars."

        readiness = compute_service_readiness(
            required_doc_ids=base_service.required_document_ids,
            user_documents=user_documents,
            service_id=svc_id
        )

        result_services.append(
            base_service.model_copy(
                update={"why_relevant": customized_why, "readiness": readiness}
            )
        )

    return result_services


def evaluate_services_for_family_death(
    context: ContextAnswers,
    user_documents: Dict[str, UserDocument]
) -> List[Service]:
    """
    Deterministic Service Recommendation Engine for Family Demise:
    - Death Registration & Certificate: Core primary vital records requirement.
    - Pension & Survivor Benefits Review: Recommended if pension or benefits involved.
    """
    recommended_service_ids = ["death_registration"]

    if context.pension_or_benefits_involved is not False:
        recommended_service_ids.append("pension_survivor_review")

    result_services: List[Service] = []

    for svc_id in recommended_service_ids:
        base_service = SEED_SERVICES.get(svc_id)
        if not base_service:
            continue

        readiness = compute_service_readiness(
            required_doc_ids=base_service.required_document_ids,
            user_documents=user_documents,
            service_id=svc_id
        )

        result_services.append(
            base_service.model_copy(update={"readiness": readiness})
        )

    return result_services


def evaluate_services_for_life_event(
    event_type: str,
    origin: Optional[str],
    destination: Optional[str],
    context: ContextAnswers,
    user_documents: Dict[str, UserDocument]
) -> List[Service]:
    """
    Universal dispatch engine for deterministic service recommendations across all supported scenarios.
    """
    if event_type == "financial_fraud":
        return evaluate_services_for_financial_fraud(context, user_documents)
    elif event_type == "marriage":
        return evaluate_services_for_marriage(context, user_documents)
    elif event_type == "family_death":
        return evaluate_services_for_family_death(context, user_documents)
    else:
        # Default / relocation
        return evaluate_services_for_relocation(origin, destination, context, user_documents)
