import pytest
import app as application
import store
import payments_client


@pytest.fixture
def client(monkeypatch):
    # Stub the outbound Payments call so tests are fast and don't need a
    # real Payments service running. The retry/backoff logic itself is
    # exercised separately (see payments_client), not re-tested here.
    monkeypatch.setattr(payments_client, "verify_merchant_with_retry", lambda rid, attempts=3: True)
    store.reset()  # each test starts from the same clean, seeded state
    return application.app.test_client()


NEW_ITEM = {"name": "Paneer Wrap", "price": 12000}


def test_add_item_creates_it(client):
    r = client.post("/restaurants/1/menu-items", json=NEW_ITEM)
    assert r.status_code == 201
    assert r.headers["Location"] == f"/menu-items/{r.json['id']}"
    assert "costPrice" not in r.json and "merchantVerified" not in r.json


def test_same_key_does_not_duplicate(client):
    headers = {"Idempotency-Key": "k-1"}
    a = client.post("/restaurants/1/menu-items", json=NEW_ITEM, headers=headers)
    b = client.post("/restaurants/1/menu-items", json=NEW_ITEM, headers=headers)
    assert (a.status_code, b.status_code) == (201, 200)
    assert a.json["id"] == b.json["id"]


def test_invalid_price_is_400(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Bad Item", "price": -5})
    assert r.status_code == 400


def test_unknown_item_is_404(client):
    assert client.get("/menu-items/999").status_code == 404


# --- bonus tests, beyond the required four ---

def test_price_exceeds_tier_cap_is_422(client):
    r = client.post("/restaurants/1/menu-items", json={"name": "Gold Thali", "price": 999999})
    assert r.status_code == 422


def test_marking_available_on_inactive_restaurant_is_409(client):
    add = client.post("/restaurants/3/menu-items", json={"name": "Ghost Dish", "price": 5000})
    item_id = add.json["id"]
    r = client.post(f"/menu-items/{item_id}/availability", json={"available": True})
    assert r.status_code == 409
