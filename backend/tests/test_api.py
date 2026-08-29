import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    # Reset repo state before each test
    client.post("/api/v1/demo/reset")
    yield


def test_primary_demo_relocation_extraction():
    """Test primary demonstration phrase: 'I moved from Mumbai to Pune.'"""
    response = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "relocation"
    assert data["origin"] == "Mumbai"
    assert data["destination"] == "Pune"
    assert data["is_supported"] is True
    assert data["confidence"] >= 0.90
    assert "Mumbai → Pune" in data["message"] or "Relocation" in data["message"]


def test_inverted_syntax_extraction():
    """Test inverted syntax: 'I have moved to Pune from Mumbai.'"""
    response = client.post("/api/v1/life-events/analyze", json={"message": "I have moved to Pune from Mumbai."})
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "relocation"
    assert data["origin"] == "Mumbai"
    assert data["destination"] == "Pune"
    assert data["is_supported"] is True


def test_relocation_phrase_variations():
    """Test 'shifted from Mumbai to Pune' and 'relocated from Delhi to Bangalore'"""
    res1 = client.post("/api/v1/life-events/analyze", json={"message": "I shifted from Mumbai to Pune."})
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["origin"] == "Mumbai"
    assert d1["destination"] == "Pune"
    assert d1["is_supported"] is True

    res2 = client.post("/api/v1/life-events/analyze", json={"message": "I relocated from Delhi to Bangalore."})
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["origin"] == "Delhi"
    assert d2["destination"] == "Bangalore"
    assert d2["is_supported"] is True


def test_unsupported_life_events():
    """Test unsupported events such as 'I started a business.'"""
    res = client.post("/api/v1/life-events/analyze", json={"message": "I started a business startup."})
    assert res.status_code == 200
    data = res.json()
    assert data["is_supported"] is False
    assert "currently supports relocation" in data["message"]


def test_empty_and_whitespace_input():
    """Test empty string and whitespace input handling"""
    res1 = client.post("/api/v1/life-events/analyze", json={"message": ""})
    assert res1.status_code == 422

    res2 = client.post("/api/v1/life-events/analyze", json={"message": "   "})
    assert res2.status_code == 422


def test_context_submission_and_service_filtering():
    """Test context submission affecting service recommendations"""
    # 1. Analyze event
    analyze_res = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    event_id = analyze_res.json()["id"]

    # 2. Context with vehicle=False, PDS=False -> 2 services (Address + Benefits)
    ctx_res1 = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": False, "receives_pds": False}
    )
    assert ctx_res1.status_code == 200
    d1 = ctx_res1.json()
    svc_ids1 = [s["id"] for s in d1["recommended_services"]]
    assert "address_update" in svc_ids1
    assert "benefits_review" in svc_ids1
    assert "vehicle_update" not in svc_ids1
    assert "pds_update" not in svc_ids1

    # 3. Context with vehicle=True, PDS=False -> 3 services
    ctx_res2 = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": False}
    )
    assert ctx_res2.status_code == 200
    d2 = ctx_res2.json()
    svc_ids2 = [s["id"] for s in d2["recommended_services"]]
    assert "vehicle_update" in svc_ids2
    assert "pds_update" not in svc_ids2

    # 4. Context with vehicle=False, PDS=True -> 3 services
    ctx_res3 = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": False, "receives_pds": True}
    )
    assert ctx_res3.status_code == 200
    d3 = ctx_res3.json()
    svc_ids3 = [s["id"] for s in d3["recommended_services"]]
    assert "pds_update" in svc_ids3
    assert "vehicle_update" not in svc_ids3

    # 5. Context with vehicle=True, PDS=True -> All 4 services
    ctx_res4 = client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": True}
    )
    assert ctx_res4.status_code == 200
    d4 = ctx_res4.json()
    assert len(d4["recommended_services"]) == 4


def test_services_catalog_and_detail_endpoints():
    """Test retrieving services catalog and individual service details"""
    res = client.get("/api/v1/services")
    assert res.status_code == 200
    services = res.json()
    assert len(services) >= 4

    # Valid service detail
    res_detail = client.get("/api/v1/services/address_update")
    assert res_detail.status_code == 200
    svc = res_detail.json()
    assert svc["name"] == "Address Update"
    assert len(svc["basic_steps"]) == 4
    assert svc["readiness"]["is_ready"] is True

    # Invalid service detail -> 404
    res_invalid = client.get("/api/v1/services/non_existent_service")
    assert res_invalid.status_code == 404


def test_documents_endpoints_and_toggle():
    """Test documents list retrieval and document status toggle"""
    # Get documents
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    data = res.json()
    assert len(data["documents"]) >= 4
    assert data["summary"]["total_available"] >= 2

    # Toggle vehicle_reg to available
    toggle_res = client.post(
        "/api/v1/documents/toggle",
        json={"document_type_id": "vehicle_reg", "status": "available"}
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["status"] == "available"

    # Verify summary updated
    res2 = client.get("/api/v1/documents")
    assert res2.json()["summary"]["total_available"] >= 3


def test_applications_endpoints():
    """Test applications tracking endpoints"""
    res = client.get("/api/v1/applications")
    assert res.status_code == 200
    apps = res.json()
    assert len(apps) >= 4

    # Valid app detail
    res_app = client.get("/api/v1/applications/app_addr_01")
    assert res_app.status_code == 200
    app_data = res_app.json()
    assert app_data["status"] == "completed"
    assert len(app_data["steps"]) == 3

    # Invalid app -> 404
    res_invalid = client.get("/api/v1/applications/unknown_app_id")
    assert res_invalid.status_code == 404
