from flask import Flask, request, jsonify
import store
from errors import problem
from models import TIER_CAPS
from payments_client import verify_merchant_with_retry

app = Flask(__name__)
store.seed()


def validate_new_item(body):
    errors = []
    name = body.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(["name", "required non-empty string"])
    price = body.get("price")
    if not isinstance(price, int) or price <= 0:
        errors.append(["price", "positive integer, in paise"])
    return errors


def validate_availability(body):
    errors = []
    if not isinstance(body.get("available"), bool):
        errors.append(["available", "required boolean"])
    return errors


@app.get("/")
def home():
    return jsonify({"message": "Restaurant API is running!"}), 200

@app.get("/restaurants")
def list_restaurants():
    area = request.args.get("area")
    if area is not None and not area.strip():
        return problem(400, "invalid-request", "area must not be blank")
    items = store.list_restaurants(area)
    return jsonify([r.as_json() for r in items]), 200


@app.get("/restaurants/<int:rid>/menu-items")
def get_menu(rid):
    r = store.find_restaurant(rid)
    if r is None:
        return problem(404, "restaurant-not-found", f"No restaurant {rid}")
    items = store.list_items_for_restaurant(rid)
    return jsonify([m.as_json() for m in items]), 200


@app.get("/menu-items/<int:iid>")
def get_item(iid):
    m = store.find_item(iid)
    if m is None:
        return problem(404, "item-not-found", f"No menu item {iid}")
    return jsonify(m.as_json()), 200


@app.post("/restaurants/<int:rid>/menu-items")
def add_menu_item(rid):
    restaurant = store.find_restaurant(rid)
    if restaurant is None:
        return problem(404, "restaurant-not-found", f"No restaurant {rid}")

    body = request.get_json(silent=True) or {}
    errs = validate_new_item(body)          # 1. bad message
    if errs:
        return problem(400, "invalid-request", errors=errs)

    key = request.headers.get("Idempotency-Key")
    if key:                                  # 2. already done?
        prior = store.find_item_by_key(key)
        if prior:
            return jsonify(prior.as_json()), 200

    if store.item_name_exists(rid, body["name"]):   # 3. state conflict
        return problem(409, "duplicate-item", f"{body['name']} already on this menu")

    cap = TIER_CAPS[restaurant.tier]                # 4. domain refuses a valid request
    if body["price"] > cap:
        return problem(422, "price-exceeds-cap", f"{restaurant.tier} cap is {cap} paise")

    verified = verify_merchant_with_retry(rid)       # 5. the outbound call, hardened
    # Payments unreachable -> verified is False. We degrade (see NOTES.md D3):
    # the item is still created; merchant_verified stays internal, never exposed.

    cost_price = int(body["price"] * 0.6)            # invented internal cost figure
    item = store.create_item(rid, body["name"], body["price"], cost_price, verified, key)
    return jsonify(item.as_json()), 201, {"Location": f"/menu-items/{item.id}"}


@app.post("/menu-items/<int:iid>/availability")
def set_availability(iid):
    item = store.find_item(iid)
    if item is None:
        return problem(404, "item-not-found", f"No menu item {iid}")

    body = request.get_json(silent=True) or {}
    errs = validate_availability(body)
    if errs:
        return problem(400, "invalid-request", errors=errs)

    wants_available = body["available"]
    restaurant = store.find_restaurant(item.restaurant_id)
    if wants_available and not restaurant.active:
        return problem(409, "restaurant-inactive", "cannot list items while the restaurant is inactive")

    item.available = wants_available
    return jsonify(item.as_json()), 200


if __name__ == "__main__":
    app.run(port=8080)
