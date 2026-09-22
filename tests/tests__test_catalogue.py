import pytest
import app as application
import store
import payments_client

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(payments_client, "verify_merchant_with_retry", lambda rid, attempts=3: True)
    store.reset()
    application._rate.clear()
    return application.app.test_client()

AUTH = {"Authorization": "Bearer test-token"}

def test_create_has_location_and_json(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Paneer Wrap", "price": 12000}, headers=AUTH)
    assert r.status_code == 201
    assert r.headers["Location"] == f"/menu-items/{r.json['id']}"
    assert r.headers["Content-Type"].startswith("application/json")

def test_same_key_is_idempotent(client):
    h = {**AUTH, "Idempotency-Key": "k-1"}
    a = client.post("/restaurants/1/menu-items", json={"name": "Paneer Wrap", "price": 12000}, headers=h)
    b = client.post("/restaurants/1/menu-items", json={"name": "Paneer Wrap", "price": 12000}, headers=h)
    assert (a.status_code, b.status_code) == (201, 200)
    assert a.json["id"] == b.json["id"]

def test_conditional_get_returns_304(client):
    r = client.get("/menu-items/1")
    tag = r.headers["ETag"]
    r2 = client.get("/menu-items/1", headers={"If-None-Match": tag})
    assert r2.status_code == 304
    assert r2.data == b""

def test_if_match_rejects_stale_write(client):
    old = client.get("/menu-items/1").headers["ETag"]
    client.patch("/menu-items/1", json={"price": 9000}, headers={**AUTH, "If-Match": old})
    r = client.patch("/menu-items/1", json={"price": 9500}, headers={**AUTH, "If-Match": old})
    assert r.status_code == 412

def test_accept_406(client):
    r = client.get("/menu-items/1", headers={"Accept": "text/html"})
    assert r.status_code == 406

def test_missing_auth_401(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Tea", "price": 1000})
    assert r.status_code == 401

def test_bad_body_400(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Bad"}, headers=AUTH)
    assert r.status_code == 400

def test_missing_item_404(client):
    assert client.get("/menu-items/999").status_code == 404

def test_price_cap_422(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Gold Thali", "price": 999999}, headers=AUTH)
    assert r.status_code == 422

def test_options_has_allow_and_cors(client):
    r = client.options("/menu-items/1")
    assert r.status_code == 204
    assert "GET" in r.headers["Allow"]
    assert r.headers["Access-Control-Allow-Origin"] == "*"

def test_delete_is_204(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Delete Me", "price": 1000}, headers=AUTH)
    item_id = r.json["id"]
    r2 = client.delete(f"/menu-items/{item_id}", headers=AUTH)
    assert r2.status_code == 204
    assert client.get(f"/menu-items/{item_id}").status_code == 404

def test_query_pagination(client):
    r = client.get("/restaurants?page=1&limit=2&sort=name&order=asc")
    assert r.status_code == 200
    assert len(r.json) == 2

def test_override_patch(client):
    tag = client.get("/menu-items/1").headers["ETag"]
    h = {**AUTH, "If-Match": tag, "X-HTTP-Method-Override": "PATCH"}
    r = client.post("/menu-items/1", json={"price": 9000}, headers=h)
    assert r.status_code == 200
