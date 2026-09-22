import pytest
import app as application
import store
import payments_client


@pytest.fixture
def client(monkeypatch):
    # Avoid calling an external merchant/payment service during tests.
    monkeypatch.setattr(
        payments_client,
        "verify_merchant_with_retry",
        lambda rid, attempts=3: True
    )

    # Reset the in-memory database before every test.
    store.reset()

    # Reset the rate-limit counter.
    application._rate.clear()

    return application.app.test_client()


AUTH = {
    "Authorization": "Bearer test-token"
}


def test_create_has_location_and_json(client):
    response = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Paneer Wrap",
            "price": 12000
        },
        headers=AUTH
    )

    assert response.status_code == 201
    assert response.headers["Location"] == f"/menu-items/{response.json['id']}"
    assert response.headers["Content-Type"].startswith("application/json")


def test_same_key_is_idempotent(client):
    headers = {
        **AUTH,
        "Idempotency-Key": "k-1"
    }

    first = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Paneer Wrap",
            "price": 12000
        },
        headers=headers
    )

    second = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Paneer Wrap",
            "price": 12000
        },
        headers=headers
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json["id"] == second.json["id"]


def test_conditional_get_returns_304(client):
    response = client.get("/menu-items/1")

    assert response.status_code == 200

    etag = response.headers["ETag"]

    second_response = client.get(
        "/menu-items/1",
        headers={
            "If-None-Match": etag
        }
    )

    assert second_response.status_code == 304
    assert second_response.data == b""


def test_if_match_rejects_stale_write(client):
    first = client.get("/menu-items/1")

    old_etag = first.headers["ETag"]

    # First update succeeds using the current ETag.
    update = client.patch(
        "/menu-items/1",
        json={
            "price": 9000
        },
        headers={
            **AUTH,
            "If-Match": old_etag
        }
    )

    assert update.status_code == 200

    # Try using the old ETag again.
    stale_update = client.patch(
        "/menu-items/1",
        json={
            "price": 9500
        },
        headers={
            **AUTH,
            "If-Match": old_etag
        }
    )

    assert stale_update.status_code == 412


def test_accept_406(client):
    response = client.get(
        "/menu-items/1",
        headers={
            "Accept": "text/html"
        }
    )

    assert response.status_code == 406


def test_missing_auth_401(client):
    response = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Tea",
            "price": 1000
        }
    )

    assert response.status_code == 401


def test_bad_body_400(client):
    response = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Bad Item"
        },
        headers=AUTH
    )

    assert response.status_code == 400


def test_missing_item_404(client):
    response = client.get("/menu-items/999")

    assert response.status_code == 404


def test_price_cap_422(client):
    response = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Gold Thali",
            "price": 999999
        },
        headers=AUTH
    )

    assert response.status_code == 422


def test_options_has_allow_and_cors(client):
    response = client.options("/menu-items/1")

    assert response.status_code == 204
    assert "GET" in response.headers["Allow"]
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_delete_is_204(client):
    response = client.post(
        "/restaurants/1/menu-items",
        json={
            "name": "Delete Me",
            "price": 1000
        },
        headers=AUTH
    )

    assert response.status_code == 201

    item_id = response.json["id"]

    delete_response = client.delete(
        f"/menu-items/{item_id}",
        headers=AUTH
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/menu-items/{item_id}"
    )

    assert get_response.status_code == 404


def test_query_pagination(client):
    response = client.get(
        "/restaurants?page=1&limit=2&sort=name&order=asc"
    )

    assert response.status_code == 200
    assert len(response.json) == 2


def test_override_patch(client):
    first = client.get("/menu-items/1")

    etag = first.headers["ETag"]

    response = client.post(
        "/menu-items/1",
        json={
            "price": 9000
        },
        headers={
            **AUTH,
            "If-Match": etag,
            "X-HTTP-Method-Override": "PATCH"
        }
    )

    assert response.status_code == 200