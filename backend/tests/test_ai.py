from unittest.mock import patch

from app.modules.ai.deepseek_client import DeepSeekClient, DeepSeekError
from app.modules.food.model import Food


def _seed(db):
    f = Food(name="南昌拌粉", description="南昌特色小吃", avg_price=12.0)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_consult_returns_answer_and_reference(client, db_session):
    _seed(db_session)
    with patch.object(DeepSeekClient, "chat", return_value="建议你去吃南昌拌粉"):
        resp = client.post("/api/ai/consult", json={"question": "南昌拌粉在哪里吃"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "建议你去吃南昌拌粉"
    assert data["references"]["foods"][0]["name"] == "南昌拌粉"


def test_consult_injects_local_context(client, db_session):
    _seed(db_session)
    captured = {}

    def fake_chat(self, messages):
        captured["messages"] = messages
        return "ok"

    with patch.object(DeepSeekClient, "chat", fake_chat):
        client.post("/api/ai/consult", json={"question": "南昌拌粉怎么样"})
    assert "【美食】" in captured["messages"][1]["content"]


def test_consult_fallback_search(client, db_session):
    _seed(db_session)
    with patch.object(DeepSeekClient, "chat", return_value="ok"):
        resp = client.post("/api/ai/consult", json={"question": "拌粉"})
    assert resp.status_code == 200
    assert resp.json()["references"]["foods"][0]["name"] == "南昌拌粉"


def test_consult_empty_references(client, db_session):
    with patch.object(DeepSeekClient, "chat", return_value="ok"):
        resp = client.post("/api/ai/consult", json={"question": "随便聊聊"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["references"]["foods"] == []
    assert data["references"]["attractions"] == []


def test_consult_empty_question(client, db_session):
    resp = client.post("/api/ai/consult", json={"question": ""})
    assert resp.status_code == 422


def test_consult_deepseek_failure(client, db_session):
    with patch.object(DeepSeekClient, "chat", side_effect=DeepSeekError("boom")):
        resp = client.post("/api/ai/consult", json={"question": "test"})
    assert resp.status_code == 502
