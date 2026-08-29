import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    client.post("/api/v1/demo/reset")
    yield
    client.post("/api/v1/demo/reset")


# ==============================================================================
# 1. Financial Fraud Scenario Tests
# ==============================================================================

def test_financial_fraud_detection():
    """Test natural language detection for financial fraud."""
    res = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "Someone made an unauthorized UPI transaction from my account."}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["event_type"] == "financial_fraud"
    assert data["is_supported"] is True


def test_financial_fraud_service_recommendation_and_portal():
    """Test deterministic recommendation and verified portal handoff for financial fraud."""
    # 1. Analyze
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I lost money in an unauthorized payment scam."}
    )
    event_id = res_evt.json()["id"]

    # 2. Submit Context
    res_ctx = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"unauthorized_txn": True, "has_txn_id": True, "knows_bank": True}
    )
    assert res_ctx.status_code == 200
    data = res_ctx.json()
    services = data["recommended_services"]
    assert len(services) == 1
    fraud_svc = services[0]
    assert fraud_svc["id"] == "financial_fraud_reporting"
    assert fraud_svc["portal_url"] == "https://cybercrime.gov.in"
    assert "National Cyber Crime Reporting Portal" in fraud_svc["portal_name"]


def test_financial_fraud_assistant_guidance():
    """Test Ask LifeEvent answers for financial fraud queries."""
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "Someone made an unauthorized UPI transaction from my account."}
    )
    event_id = res_evt.json()["id"]

    # Where should I report this?
    chat_res1 = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Where should I report this?", "life_event_id": event_id}
    )
    assert chat_res1.status_code == 200
    assert "cybercrime.gov.in" in chat_res1.json()["answer"]
    assert "1930" in chat_res1.json()["answer"]

    # What information should I keep ready?
    chat_res2 = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What information should I keep ready?", "life_event_id": event_id}
    )
    assert chat_res2.status_code == 200
    assert "Transaction Reference" in chat_res2.json()["answer"] or "Txn ID" in chat_res2.json()["answer"]


# ==============================================================================
# 2. Marriage Scenario Tests
# ==============================================================================

def test_marriage_detection():
    """Test natural language detection for marriage."""
    res = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I recently got married."}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["event_type"] == "marriage"
    assert data["is_supported"] is True


def test_marriage_service_recommendation_and_aadhaar_update():
    """Test recommendation of Marriage Registration and Aadhaar Demographic Update."""
    # 1. Analyze
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I got married and my name has changed."}
    )
    event_id = res_evt.json()["id"]

    # 2. Submit Context
    res_ctx = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"details_changed": True, "needs_marriage_cert": True, "address_changed": True}
    )
    assert res_ctx.status_code == 200
    services = res_ctx.json()["recommended_services"]
    svc_ids = [s["id"] for s in services]
    assert "marriage_registration" in svc_ids
    assert "aadhaar_update" in svc_ids
    assert "address_update" in svc_ids

    # Check verified portal for Aadhaar
    aadhaar_svc = next(s for s in services if s["id"] == "aadhaar_update")
    assert aadhaar_svc["portal_url"] == "https://myaadhaar.uidai.gov.in"


def test_marriage_assistant_explanation():
    """Test Ask LifeEvent explanation for marriage recommendations."""
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I recently got married."}
    )
    event_id = res_evt.json()["id"]

    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What changed because I got married?", "life_event_id": event_id}
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "Marriage Registration" in answer
    assert "Aadhaar" in answer


# ==============================================================================
# 3. Family Death Scenario Tests
# ==============================================================================

def test_family_death_detection():
    """Test natural language detection for family death."""
    res = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "My father passed away."}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["event_type"] == "family_death"
    assert data["is_supported"] is True


def test_family_death_service_recommendation():
    """Test recommendation of Death Registration and Pension Review."""
    # 1. Analyze
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "My father passed away."}
    )
    event_id = res_evt.json()["id"]

    # 2. Submit Context
    res_ctx = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"looking_for_death_cert": True, "pension_or_benefits_involved": True}
    )
    assert res_ctx.status_code == 200
    services = res_ctx.json()["recommended_services"]
    svc_ids = [s["id"] for s in services]
    assert "death_registration" in svc_ids
    assert "pension_survivor_review" in svc_ids

    # Death registration is primary
    death_svc = services[0]
    assert death_svc["id"] == "death_registration"
    assert death_svc["portal_url"] == "https://crsorgi.gov.in"


def test_family_death_assistant_prioritization():
    """Test that assistant prioritizes Death Registration first."""
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "My father passed away."}
    )
    event_id = res_evt.json()["id"]

    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What do I need to do first?", "life_event_id": event_id}
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "Death Registration" in answer or "Death Certificate" in answer


# ==============================================================================
# 4. Multi-Scenario Document Readiness & Verification Tests
# ==============================================================================

def test_new_scenario_initial_readiness_not_falsely_verified():
    """
    Requirement 1: Newly analyzed scenario does NOT falsely report documents as already verified.
    Starts at 0 available (Not yet verified).
    """
    # 1. Analyze financial fraud
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "Someone made an unauthorized UPI transaction from my account."}
    )
    event_id = res_evt.json()["id"]

    # 2. Submit context
    res_ctx = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"unauthorized_txn": True, "has_txn_id": True, "knows_bank": True}
    )
    assert res_ctx.status_code == 200
    summary = res_ctx.json()["readiness_summary"]
    assert summary["total_required"] == 2
    assert summary["total_available"] == 0
    assert summary["percentage"] == 0
    assert summary["is_demo_preset"] is False


def test_required_items_association_per_scenario():
    """
    Requirement 2: Required items are correctly associated with the scenario/service.
    """
    # Fraud -> txn_details + identity_proof
    fraud_res = client.post("/api/v1/life-events/analyze", json={"message": "UPI fraud scam."})
    fraud_ctx = client.post(f"/api/v1/life-events/{fraud_res.json()['id']}/context", json={"unauthorized_txn": True}).json()
    fraud_svc = fraud_ctx["recommended_services"][0]
    assert set(fraud_svc["required_document_ids"]) == {"txn_details", "identity_proof"}

    # Marriage -> marriage_proof + identity_proof + address_proof
    mrg_res = client.post("/api/v1/life-events/analyze", json={"message": "I got married."})
    mrg_ctx = client.post(f"/api/v1/life-events/{mrg_res.json()['id']}/context", json={"details_changed": True, "needs_marriage_cert": True}).json()
    mrg_req_ids = set()
    for s in mrg_ctx["recommended_services"]:
        mrg_req_ids.update(s["required_document_ids"])
    assert "marriage_proof" in mrg_req_ids
    assert "identity_proof" in mrg_req_ids


def test_marking_item_available_updates_readiness():
    """
    Requirement 3: Marking an item Available updates readiness score deterministically.
    """
    # 1. Start Fraud scenario (0/2 ready)
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "Unauthorized transaction."}
    )
    event_id = res_evt.json()["id"]
    ctx_res = client.post(f"/api/v1/life-events/{event_id}/context", json={"unauthorized_txn": True}).json()
    assert ctx_res["readiness_summary"]["total_available"] == 0

    # 2. Mark txn_details as Available -> 1/2 (50%)
    toggle1 = client.post("/api/v1/documents/toggle", json={"document_type_id": "txn_details", "status": "available"})
    assert toggle1.status_code == 200
    docs1 = client.get("/api/v1/documents").json()
    assert docs1["summary"]["total_available"] == 1
    assert docs1["summary"]["total_required"] == 2
    assert docs1["summary"]["percentage"] == 50

    # 3. Mark identity_proof as Available -> 2/2 (100%)
    toggle2 = client.post("/api/v1/documents/toggle", json={"document_type_id": "identity_proof", "status": "available"})
    assert toggle2.status_code == 200
    docs2 = client.get("/api/v1/documents").json()
    assert docs2["summary"]["total_available"] == 2
    assert docs2["summary"]["total_required"] == 2
    assert docs2["summary"]["percentage"] == 100


def test_marking_item_needed_updates_readiness_down():
    """
    Requirement 4: Marking an item Needed updates readiness again (decreases percentage).
    """
    # Start Fraud, mark both available (2/2)
    res_evt = client.post("/api/v1/life-events/analyze", json={"message": "Unauthorized transaction."})
    client.post(f"/api/v1/life-events/{res_evt.json()['id']}/context", json={"unauthorized_txn": True})
    client.post("/api/v1/documents/toggle", json={"document_type_id": "txn_details", "status": "available"})
    client.post("/api/v1/documents/toggle", json={"document_type_id": "identity_proof", "status": "available"})
    assert client.get("/api/v1/documents").json()["summary"]["total_available"] == 2

    # Toggle txn_details back to needed (missing) -> 1/2 (50%)
    toggle_back = client.post("/api/v1/documents/toggle", json={"document_type_id": "txn_details", "status": "missing"})
    assert toggle_back.status_code == 200
    docs_after = client.get("/api/v1/documents").json()
    assert docs_after["summary"]["total_available"] == 1
    assert docs_after["summary"]["percentage"] == 50


def test_existing_relocation_demo_remains_2_of_4_initially():
    """
    Requirement 5: Existing relocation demo retains the seeded baseline state (2/4 ready initially).
    """
    res_evt = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I moved from Mumbai to Pune."}
    )
    event_id = res_evt.json()["id"]

    res_ctx = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": True}
    )
    assert res_ctx.status_code == 200
    summary = res_ctx.json()["readiness_summary"]
    assert summary["total_required"] == 4
    assert summary["total_available"] == 2
    assert summary["percentage"] == 50
    assert summary["is_demo_preset"] is True


def test_reset_demo_restores_relocation_demo_preset():
    """
    Requirement 6: Reset Demo still restores the relocation demo state (Identity & Address = Available, 2/4).
    """
    # Change documents
    client.post("/api/v1/documents/toggle", json={"document_type_id": "vehicle_reg", "status": "available"})
    client.post("/api/v1/documents/toggle", json={"document_type_id": "pds_ration_card", "status": "available"})

    # Call reset
    reset_res = client.post("/api/v1/demo/reset")
    assert reset_res.status_code == 200

    # Verify restored demo baseline
    docs_reset = client.get("/api/v1/documents").json()
    assert docs_reset["summary"]["total_available"] == 2
    assert docs_reset["summary"]["total_required"] == 4
    doc_map = {d["document_type_id"]: d["status"] for d in docs_reset["documents"]}
    assert doc_map["identity_proof"] == "available"
    assert doc_map["address_proof"] == "available"
    assert doc_map["vehicle_reg"] == "missing"
    assert doc_map["pds_ration_card"] == "missing"


# ==============================================================================
# 5. Unsupported Event Test
# ==============================================================================

def test_unsupported_business_event():
    """Test that unsupported events return a clear message listing supported scenarios."""
    res = client.post(
        "/api/v1/life-events/analyze",
        json={"message": "I started a new business startup."}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_supported"] is False
    assert "relocation" in data["message"]
    assert "financial fraud" in data["message"]
    assert "marriage" in data["message"]
    assert "family-death" in data["message"]
