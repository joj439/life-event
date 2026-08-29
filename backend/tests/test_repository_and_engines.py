import pytest
from app.repositories.in_memory_repo import InMemoryRepository
from app.schemas.models import (
    ContextAnswers,
    DocumentStatus,
    ApplicationStatus
)
from app.engines.service_engine import evaluate_services_for_relocation
from app.engines.document_engine import compute_service_readiness, compute_overall_readiness
from app.data.seed_data import DEMO_USER_ID


@pytest.fixture
def clean_repo():
    repo = InMemoryRepository()
    return repo


def test_seed_services_retrieval(clean_repo):
    services = clean_repo.get_all_services()
    assert len(services) >= 4
    service_ids = {s.id for s in services}
    assert {"address_update", "pds_update", "vehicle_update", "benefits_review"}.issubset(service_ids)

    addr_svc = clean_repo.get_service_by_id("address_update")
    assert addr_svc is not None
    assert addr_svc.name == "Address Update"
    assert "identity_proof" in addr_svc.required_document_ids
    assert "address_proof" in addr_svc.required_document_ids


def test_seed_document_types_retrieval(clean_repo):
    doc_types = clean_repo.get_all_document_types()
    assert len(doc_types) >= 4
    type_ids = {dt.id for dt in doc_types}
    assert {"identity_proof", "address_proof", "vehicle_reg", "pds_ration_card"}.issubset(type_ids)


def test_seed_demo_user_documents(clean_repo):
    user_docs = clean_repo.get_user_documents(DEMO_USER_ID)
    assert len(user_docs) >= 4
    assert user_docs["identity_proof"].status == DocumentStatus.AVAILABLE
    assert user_docs["address_proof"].status == DocumentStatus.AVAILABLE
    assert user_docs["vehicle_reg"].status == DocumentStatus.MISSING
    assert user_docs["pds_ration_card"].status == DocumentStatus.MISSING


def test_seed_applications(clean_repo):
    apps = clean_repo.get_user_applications(DEMO_USER_ID)
    assert len(apps) >= 4
    status_by_service = {a.service_id: a.status for a in apps}
    assert status_by_service["address_update"] == ApplicationStatus.COMPLETED
    assert status_by_service["pds_update"] == ApplicationStatus.UNDER_REVIEW
    assert status_by_service["vehicle_update"] == ApplicationStatus.ACTION_REQUIRED
    assert status_by_service["benefits_review"] == ApplicationStatus.NOT_STARTED


def test_document_toggle_status(clean_repo):
    # Initial state: vehicle_reg is MISSING
    user_docs = clean_repo.get_user_documents(DEMO_USER_ID)
    assert user_docs["vehicle_reg"].status == DocumentStatus.MISSING

    # Toggle to AVAILABLE
    updated_doc = clean_repo.toggle_user_document_status(DEMO_USER_ID, "vehicle_reg")
    assert updated_doc is not None
    assert updated_doc.status == DocumentStatus.AVAILABLE

    # Toggle back to MISSING
    updated_doc = clean_repo.toggle_user_document_status(DEMO_USER_ID, "vehicle_reg")
    assert updated_doc.status == DocumentStatus.MISSING


def test_deterministic_service_rules(clean_repo):
    user_docs = clean_repo.get_user_documents(DEMO_USER_ID)

    # Case 1: No vehicle, No PDS -> Address Update & Benefits Review (2 services)
    ctx1 = ContextAnswers(permanent=True, owns_vehicle=False, receives_pds=False)
    services1 = evaluate_services_for_relocation("Mumbai", "Pune", ctx1, user_docs)
    ids1 = [s.id for s in services1]
    assert "address_update" in ids1
    assert "benefits_review" in ids1
    assert "vehicle_update" not in ids1
    assert "pds_update" not in ids1
    assert len(services1) == 2

    # Case 2: Vehicle = True, PDS = False -> Address, Vehicle, Benefits (3 services)
    ctx2 = ContextAnswers(permanent=True, owns_vehicle=True, receives_pds=False)
    services2 = evaluate_services_for_relocation("Mumbai", "Pune", ctx2, user_docs)
    ids2 = [s.id for s in services2]
    assert "address_update" in ids2
    assert "vehicle_update" in ids2
    assert "benefits_review" in ids2
    assert "pds_update" not in ids2
    assert len(services2) == 3

    # Case 3: Vehicle = False, PDS = True -> Address, PDS, Benefits (3 services)
    ctx3 = ContextAnswers(permanent=True, owns_vehicle=False, receives_pds=True)
    services3 = evaluate_services_for_relocation("Mumbai", "Pune", ctx3, user_docs)
    ids3 = [s.id for s in services3]
    assert "address_update" in ids3
    assert "pds_update" in ids3
    assert "benefits_review" in ids3
    assert "vehicle_update" not in ids3
    assert len(services3) == 3

    # Case 4: Vehicle = True, PDS = True -> All 4 services
    ctx4 = ContextAnswers(permanent=True, owns_vehicle=True, receives_pds=True)
    services4 = evaluate_services_for_relocation("Mumbai", "Pune", ctx4, user_docs)
    ids4 = [s.id for s in services4]
    assert ids4 == ["address_update", "pds_update", "vehicle_update", "benefits_review"]
    assert len(services4) == 4


def test_document_readiness_calculation(clean_repo):
    user_docs = clean_repo.get_user_documents(DEMO_USER_ID)

    # Address update requires identity_proof and address_proof (both available)
    addr_readiness = compute_service_readiness(["identity_proof", "address_proof"], user_docs, "address_update")
    assert addr_readiness.required_count == 2
    assert addr_readiness.available_count == 2
    assert addr_readiness.percentage == 100
    assert addr_readiness.is_ready is True
    assert len(addr_readiness.missing_documents) == 0

    # Vehicle update requires identity_proof, address_proof, and vehicle_reg (vehicle_reg is missing)
    veh_readiness = compute_service_readiness(["identity_proof", "address_proof", "vehicle_reg"], user_docs, "vehicle_update")
    assert veh_readiness.required_count == 3
    assert veh_readiness.available_count == 2
    assert veh_readiness.percentage == 66 or veh_readiness.percentage == 67
    assert veh_readiness.is_ready is False
    assert len(veh_readiness.missing_documents) == 1
    assert veh_readiness.missing_documents[0].id == "vehicle_reg"

    # Overall readiness across relocation services
    overall = compute_overall_readiness(["identity_proof", "address_proof", "vehicle_reg"], user_docs)
    assert overall["total_required"] == 3
    assert overall["total_available"] == 2
    assert overall["missing_count"] == 1
    assert overall["percentage"] == 66 or overall["percentage"] == 67
