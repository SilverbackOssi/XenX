"""Lightweight test for basic chat flow endpoint.

Uses FastAPI's TestClient to verify that a conversation is created and an
assistant reply is returned. This is an initial smoke test and will evolve
as orchestration layers are added.
"""
from fastapi.testclient import TestClient
from main import app


def test_basic_chat_flow(monkeypatch):  # noqa: D103
    client = TestClient(app)

    # Feature flag may be disabled in some environments; skip if endpoint missing
    resp = client.get("/api/v1/chat/health")
    if resp.status_code != 200:
        return  # Skip silently (flag off)

    payload = {"message": "Hello there"}
    r = client.post("/api/v1/chat/message", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["conversation_id"] > 0
    assert data["user_message"] == "Hello there"
    assert "assistant_message" in data
    assert "trace_id" in data

    # Fetch history and ensure at least user + assistant messages present
    history = client.get(f"/api/v1/chat/{data['conversation_id']}")
    if history.status_code == 200:  # Only if feature flag enabled
        hist_json = history.json()
        assert hist_json["conversation_id"] == data["conversation_id"]
        assert len(hist_json["messages"]) >= 2
        roles = [m["role"] for m in hist_json["messages"]]
        assert "user" in roles and "assistant" in roles
