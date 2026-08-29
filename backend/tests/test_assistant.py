import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    client.post("/api/v1/demo/reset")
    yield
    client.post("/api/v1/demo/reset")


def test_assistant_endpoint_basic():
    """Test that assistant chat endpoint responds with 200 OK and valid schema."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What is LifeEvent?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "source" in data
    assert data["source"] == "deterministic_engine"


def test_assistant_vehicle_update_relevance():
    """
    Test 'Why do I need the vehicle update?'
    Verify response references relocation context + vehicle ownership.
    """
    # 1. Create life event and context
    evt_res = client.post("/api/v1/life-events/analyze", json={"message": "I moved from Mumbai to Pune."})
    event_id = evt_res.json()["id"]
    client.post(
        f"/api/v1/life-events/{event_id}/context",
        json={"permanent": True, "owns_vehicle": True, "receives_pds": True}
    )

    # 2. Ask assistant
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "Why do I need the vehicle update?",
            "life_event_id": event_id
        }
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "Mumbai to Pune" in answer
    assert "vehicle" in answer.lower()
    assert "Vehicle Registration" in answer or "RTO" in answer


def test_assistant_missing_documents():
    """
    Test 'What documents am I missing?'
    Verify response accurately lists the missing documents from initial state.
    """
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What documents am I missing?"}
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "Vehicle Registration" in answer or "needed" in answer.lower()


def test_assistant_what_should_i_do_next():
    """
    Test 'What should I do next?'
    Verify response gives actionable next steps based on application/checklist state.
    """
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What should I do next?"}
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "Action" in answer or "Vehicle" in answer or "Document" in answer or "application" in answer.lower()


def test_assistant_service_specific_context():
    """
    Test service-specific context: asking 'Why is this relevant to me?' with service_id='vehicle_update'.
    """
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "Why is this relevant to me?",
            "service_id": "vehicle_update"
        }
    )
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert data["service_id"] == "vehicle_update"
    assert "Vehicle" in data["answer"]


def test_assistant_service_specific_documents():
    """
    Test asking for documents on a specific service: service_id='address_update' (ready) vs 'vehicle_update' (missing).
    """
    # Address update is 100% ready in default state
    res_addr = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "What documents do I need for this?",
            "service_id": "address_update"
        }
    )
    assert res_addr.status_code == 200
    assert "Available" in res_addr.json()["answer"]

    # Vehicle update is missing RC
    res_veh = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "What documents do I need?",
            "service_id": "vehicle_update"
        }
    )
    assert res_veh.status_code == 200
    assert "Vehicle Registration" in res_veh.json()["answer"] or "needed" in res_veh.json()["answer"].lower()


def test_assistant_unknown_question_safety():
    """
    Test that questions outside the prototype scope return safe, non-hallucinated disclaimers.
    """
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What is the tax rate on luxury yachts in Pune?"}
    )
    assert chat_res.status_code == 200
    answer = chat_res.json()["answer"]
    assert "don't have enough" in answer.lower()
    assert "government portal" in answer.lower() or "official" in answer.lower()


def test_assistant_empty_message_rejection():
    """Test that empty or whitespace messages are rejected with 422."""
    res1 = client.post("/api/v1/assistant/chat", json={"message": ""})
    assert res1.status_code == 422

    res2 = client.post("/api/v1/assistant/chat", json={"message": "   "})
    assert res2.status_code == 422


def test_assistant_invalid_ids_graceful_handling():
    """Test that invalid life_event_id and service_id do not crash the assistant."""
    chat_res = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "Why is this service relevant?",
            "life_event_id": "invalid_evt_id_999",
            "service_id": "invalid_service_id_999"
        }
    )
    assert chat_res.status_code == 200
    assert "answer" in chat_res.json()
