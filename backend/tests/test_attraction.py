from app.modules.attraction.model import Attraction


def _seed(db):
    a1 = Attraction(name="滕王阁", description="江南三大名楼之一", open_time="08:00-18:00", ticket_price="50 元")
    a2 = Attraction(name="八一广场", description="南昌城市中心广场", open_time="全天开放", ticket_price="免费")
    db.add_all([a1, a2])
    db.commit()
    for a in (a1, a2):
        db.refresh(a)
    return a1, a2


def test_list_attractions(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_attractions_search(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions", params={"keyword": "滕王阁"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "滕王阁"


def test_get_attraction_detail(client, db_session):
    a1, _ = _seed(db_session)
    resp = client.get(f"/api/attractions/{a1.id}")
    assert resp.status_code == 200
    assert resp.json()["ticket_price"] == "50 元"


def test_get_attraction_not_found(client, db_session):
    resp = client.get("/api/attractions/999")
    assert resp.status_code == 404
