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


def test_list_attractions_search_by_description(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions", params={"keyword": "名楼"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "滕王阁"


def test_list_attractions_pagination(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions", params={"page": 2, "page_size": 1})
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "八一广场"


def test_list_attractions_empty(client, db_session):
    resp = client.get("/api/attractions")
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_attractions_invalid_page(client, db_session):
    resp = client.get("/api/attractions", params={"page": 0})
    assert resp.status_code == 422


def test_list_attractions_sort_by_rating(client, db_session):
    a1 = Attraction(name="高分景点", description="测试", open_time="全天", ticket_price="免费", rating=4.8, rating_count=200)
    a2 = Attraction(name="低分景点", description="测试", open_time="全天", ticket_price="免费", rating=4.0, rating_count=50)
    db_session.add_all([a1, a2])
    db_session.commit()
    resp = client.get("/api/attractions", params={"sort": "rating"})
    data = resp.json()
    assert data["items"][0]["name"] == "高分景点"
    assert data["items"][1]["name"] == "低分景点"


def test_list_attractions_invalid_sort(client, db_session):
    resp = client.get("/api/attractions", params={"sort": "foo"})
    assert resp.status_code == 422
