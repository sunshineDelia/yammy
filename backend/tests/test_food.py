from app.modules.food.model import Food, Store


def _seed(db):
    f1 = Food(name="南昌拌粉", description="南昌最具代表性的小吃", avg_price=12.0)
    f1.stores = [Store(name="黄记拌粉", address="中山路1号")]
    f2 = Food(name="瓦罐汤", description="南昌传统煨汤", avg_price=20.0)
    db.add_all([f1, f2])
    db.commit()
    for f in (f1, f2):
        db.refresh(f)
    return f1, f2


def test_list_foods(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_list_foods_search(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods", params={"keyword": "瓦罐"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "瓦罐汤"


def test_get_food_detail_with_stores(client, db_session):
    f1, _ = _seed(db_session)
    resp = client.get(f"/api/foods/{f1.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "南昌拌粉"
    assert data["stores"][0]["name"] == "黄记拌粉"


def test_get_food_not_found(client, db_session):
    resp = client.get("/api/foods/999")
    assert resp.status_code == 404


def test_list_foods_search_by_description(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods", params={"keyword": "代表"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "南昌拌粉"


def test_list_foods_pagination(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods", params={"page": 2, "page_size": 1})
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "瓦罐汤"


def test_list_foods_empty(client, db_session):
    resp = client.get("/api/foods")
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_foods_invalid_page(client, db_session):
    resp = client.get("/api/foods", params={"page": 0})
    assert resp.status_code == 422


def test_list_foods_sort_by_rating(client, db_session):
    f1 = Food(name="高分菜", description="测试", avg_price=10.0, rating=4.9, rating_count=100)
    f2 = Food(name="低分菜", description="测试", avg_price=10.0, rating=4.0, rating_count=50)
    db_session.add_all([f1, f2])
    db_session.commit()
    resp = client.get("/api/foods", params={"sort": "rating"})
    data = resp.json()
    assert data["items"][0]["name"] == "高分菜"
    assert data["items"][1]["name"] == "低分菜"


def test_list_foods_invalid_sort(client, db_session):
    resp = client.get("/api/foods", params={"sort": "foo"})
    assert resp.status_code == 422
