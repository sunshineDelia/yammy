from app.modules.attraction.model import Attraction
from app.modules.food.model import Food


def _seed_food(db):
    f = Food(name="南昌拌粉", description="南昌特色小吃", avg_price=12.0)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def _seed_attraction(db):
    a = Attraction(name="滕王阁", description="江南三大名楼之一", open_time="08:00-18:00", ticket_price="50 元")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_add_favorite(client, db_session):
    f = _seed_food(db_session)
    resp = client.post(
        "/api/favorites",
        json={"target_type": "food", "target_id": f.id},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 201


def test_add_favorite_idempotent(client, db_session):
    f = _seed_food(db_session)
    h = {"X-Device-Id": "dev1"}
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers=h)
    resp = client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers=h)
    assert resp.status_code == 200


def test_add_favorite_invalid_type(client, db_session):
    resp = client.post(
        "/api/favorites",
        json={"target_type": "foo", "target_id": 1},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 400


def test_add_favorite_target_not_found(client, db_session):
    resp = client.post(
        "/api/favorites",
        json={"target_type": "food", "target_id": 999},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 404


def test_missing_device_id(client, db_session):
    resp = client.post("/api/favorites", json={"target_type": "food", "target_id": 1})
    assert resp.status_code == 400


def test_list_favorites_with_detail(client, db_session):
    f = _seed_food(db_session)
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    resp = client.get("/api/favorites", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["food"]["name"] == "南昌拌粉"


def test_delete_favorite(client, db_session):
    f = _seed_food(db_session)
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    resp = client.delete(f"/api/favorites/food/{f.id}", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 204


def test_status(client, db_session):
    f = _seed_food(db_session)
    resp = client.get("/api/favorites/status", params={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    assert resp.json() == {"favorited": False}


def test_delete_invalid_type(client, db_session):
    resp = client.delete("/api/favorites/foo/1", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 400


def test_status_invalid_type(client, db_session):
    resp = client.get("/api/favorites/status", params={"target_type": "foo", "target_id": 1}, headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 400


def test_add_attraction_favorite(client, db_session):
    a = _seed_attraction(db_session)
    resp = client.post("/api/favorites", json={"target_type": "attraction", "target_id": a.id}, headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 201
    resp = client.get("/api/favorites", headers={"X-Device-Id": "dev1"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["attraction"]["name"] == "滕王阁"


def test_status_true_after_favorite(client, db_session):
    f = _seed_food(db_session)
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    resp = client.get("/api/favorites/status", params={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    assert resp.json() == {"favorited": True}


def test_delete_nonexistent_favorite(client, db_session):
    resp = client.delete("/api/favorites/food/999", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 404
