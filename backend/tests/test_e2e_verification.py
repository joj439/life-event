import pytest
from fastapi.testclient import TestClient
from main import app
from app.data.seed_data import DEMO_USER_ID

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    client.post("/api/v1/demo/reset")
    yield
    client.post("/api/v1/demo/reset")


def test_scenario_1_primary_demo_flow():
    """
    Scenario 1: Primary demo flow
    'I moved from Mumbai to Pune.' -> Context (Permanent=True, Vehicle=True, PDS=True)
    Verify 4 services returned, document readiness (2/3), and application statuses.
    """
    # 1. Analyze
    analyze_res = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    assert analyze_res.status_code == 200
    event = analyze_res.json()
    assert event["event_type"] == "relocation"
    assert event["origin"] == "Mumbai"
    assert event["destination"] == "Pune"
    assert event["is_supported"] is True

    # 2. Submit Context
    ctx_res = client.post(
        f"/api/v1/life-events/{event['id']}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": True}
    )
    assert ctx_res.status_code == 200
    data = ctx_res.json()
    services = data["recommended_services"]
    assert len(services) == 4
    service_ids = [s["id"] for s in services]
    assert service_ids == ["address_update", "pds_update", "vehicle_update", "benefits_review"]

    # Check customized why_relevant text
    addr_svc = next(s for s in services if s["id"] == "address_update")
    assert "Mumbai to Pune" in addr_svc["why_relevant"]

    # Check readiness in services
    assert addr_svc["readiness"]["available_count"] == 2
    assert addr_svc["readiness"]["required_count"] == 2
    assert addr_svc["readiness"]["is_ready"] is True

    veh_svc = next(s for s in services if s["id"] == "vehicle_update")
    assert veh_svc["readiness"]["available_count"] == 2
    assert veh_svc["readiness"]["required_count"] == 3
    assert veh_svc["readiness"]["is_ready"] is False
    assert veh_svc["readiness"]["missing_documents"][0]["id"] == "vehicle_reg"

    # Check overall summary
    summary = data["readiness_summary"]
    assert summary["total_available"] == 2


def test_scenario_2_vehicle_false_exclusion():
    """Scenario 2: Vehicle = No -> Vehicle service is excluded"""
    analyze_res = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    event_id = analyze_res.json()["id"]

    ctx_res = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": False, "receives_pds": True}
    )
    assert ctx_res.status_code == 200
    services = ctx_res.json()["recommended_services"]
    service_ids = [s["id"] for s in services]
    assert "vehicle_update" not in service_ids
    assert "address_update" in service_ids
    assert "pds_update" in service_ids
    assert "benefits_review" in service_ids
    assert len(services) == 3


def test_scenario_3_pds_false_exclusion():
    """Scenario 3: PDS = No -> PDS service is excluded"""
    analyze_res = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    event_id = analyze_res.json()["id"]

    ctx_res = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": False}
    )
    assert ctx_res.status_code == 200
    services = ctx_res.json()["recommended_services"]
    service_ids = [s["id"] for s in services]
    assert "pds_update" not in service_ids
    assert "address_update" in service_ids
    assert "vehicle_update" in service_ids
    assert "benefits_review" in service_ids
    assert len(services) == 3


def test_scenario_4_unsupported_event():
    """Scenario 4: 'I started a business.' -> Friendly unsupported-event message"""
    res = client.post("/api/v1/life-events/analyze", json={"message": "I started a new business company."})
    assert res.status_code == 200
    data = res.json()
    assert data["is_supported"] is False
    assert data["event_type"] == "business"
    assert "currently supports relocation" in data["message"]


def test_scenario_5_empty_input_validation():
    """Scenario 5: Empty input -> Friendly validation 422 error"""
    res1 = client.post("/api/v1/life-events/analyze", json={"message": ""})
    assert res1.status_code == 422
    assert "detail" in res1.json()

    res2 = client.post("/api/v1/life-events/analyze", json={"message": "   "})
    assert res2.status_code == 422


def test_scenario_6_invalid_service_id():
    """Scenario 6: Invalid service ID -> 404 with clear message"""
    res = client.get("/api/v1/services/fake_non_existent_id")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"]


def test_scenario_7_document_toggle_and_readiness_recalculation():
    """Scenario 7: Toggle document status -> Readiness recalculates correctly"""
    # Initial state
    docs_before = client.get("/api/v1/documents").json()
    assert docs_before["summary"]["total_available"] >= 2

    # Toggle vehicle_reg to available
    toggle_res = client.post(
        "/api/v1/documents/toggle",
        json={"document_type_id": "vehicle_reg", "status": "available"}
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["status"] == "available"

    # Check updated readiness
    docs_after = client.get("/api/v1/documents").json()
    assert docs_after["summary"]["total_available"] >= 3

    # Check vehicle service readiness is now 100%
    veh_svc = client.get("/api/v1/services/vehicle_update").json()
    assert veh_svc["readiness"]["available_count"] == 3
    assert veh_svc["readiness"]["required_count"] == 3
    assert veh_svc["readiness"]["is_ready"] is True
    assert veh_svc["readiness"]["percentage"] == 100


def test_scenario_8_reset_demo_state():
    """Scenario 8: Reset demo -> Returns to original pristine demo state"""
    # Modify a document
    client.post("/api/v1/documents/toggle", json={"document_type_id": "vehicle_reg", "status": "available"})
    assert client.get("/api/v1/documents").json()["summary"]["total_available"] >= 3

    # Call reset
    reset_res = client.post("/api/v1/demo/reset")
    assert reset_res.status_code == 200

    # Verify reset conditions
    docs_reset = client.get("/api/v1/documents").json()
    assert docs_reset["summary"]["total_available"] >= 2
    doc_map = {d["document_type_id"]: d["status"] for d in docs_reset["documents"]}
    assert doc_map["identity_proof"] == "available"
    assert doc_map["address_proof"] == "available"
    assert doc_map["vehicle_reg"] == "missing"
    assert doc_map["pds_ration_card"] == "missing"

    apps_reset = client.get("/api/v1/applications").json()
    status_map = {a["service_id"]: a["status"] for a in apps_reset}
    assert status_map["address_update"] == "completed"
    assert status_map["pds_update"] == "under_review"
    assert status_map["vehicle_update"] == "action_required"
    assert status_map["benefits_review"] == "not_started"


def test_scenario_9_applications_tracking_detail():
    """Scenario 9: Applications tracking details and 404 for invalid app"""
    # Valid app
    app_res = client.get("/api/v1/applications/app_addr_01")
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["tracking_number"] == "MH-2026-ADDR-9104"
    assert app_data["status"] == "completed"
    assert len(app_data["steps"]) == 3

    # Invalid app -> 404
    invalid_app = client.get("/api/v1/applications/non_existent_app_id")
    assert invalid_app.status_code == 404
