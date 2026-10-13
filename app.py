from flask import Flask, request, jsonify, make_response
import hashlib
import json
import gzip
from functools import wraps
import store
from errors import problem
from models import TIER_CAPS
from payments_client import verify_merchant_with_retry
import logging
from xml.sax.saxutils import escape


app = Flask(__name__)
store.seed()

RATE_LIMIT = 10
_rate = {}

def client_id():
    return request.headers.get("Authorization") or request.remote_addr or "anonymous"

def etag(item):
    raw = json.dumps(item.as_json(), sort_keys=True, separators=(",", ":")).encode()
    return '"' + hashlib.sha256(raw).hexdigest()[:16] + '"'

def auth_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if not token.startswith("Bearer ") or not token[7:].strip():
            return problem(401, "unauthorized", "Authorization: Bearer <token> is required")
        return fn(*args, **kwargs)
    return wrapped


@app.before_request
def common_request_checks():
    if request.method == "OPTIONS":
        return None

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        key = client_id()
        used = _rate.get(key, 0)

        if used >= RATE_LIMIT:
            response = problem(
                429, "rate-limit", "Request limit exceeded"
            )
            response.headers["Retry-After"] = "60"
            return response

        _rate[key] = used + 1


@app.after_request
def common_headers(response):
    if request.blueprint == "orders":
         return response
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    used = _rate.get(client_id(), 0)
    response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT - used))
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Authorization, Content-Type, Idempotency-Key, If-Match, If-None-Match, X-HTTP-Method-Override"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    if request.method in {"GET", "OPTIONS"}:
        response.headers.setdefault("Cache-Control", "public, max-age=60")
    else:
        response.headers.setdefault("Cache-Control", "no-store")
    if response.is_json:
        if response.status_code >= 400:
            response.headers.setdefault(
            "Content-Type",
            "application/problem+json; charset=utf-8"
            )
        else:
            response.headers["Content-Type"] = (
            "application/json; charset=utf-8")
        if "gzip" in request.headers.get("Accept-Encoding", ""):
            data = response.get_data()
            if len(data) >= 100:
                response.set_data(gzip.compress(data))
                response.headers["Content-Encoding"] = "gzip"
                response.headers["Content-Length"] = str(len(response.get_data()))
    return response

def wants_json():
    accept = request.headers.get("Accept", "application/json")
    return "application/json" in accept or "*/*" in accept

def check_accept():
    if not wants_json():
        return problem(406, "not-acceptable", "only application/json is supported")
    return None

def get_json_body():
    if request.content_length and not request.is_json:
        return None
    return request.get_json(silent=True) or {}

def validate_new_item(body):
    errors = []
    name = body.get("name")
    price = body.get("price")
    if not isinstance(name, str) or not name.strip():
        errors.append(["name", "required non-empty string"])
    if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
        errors.append(["price", "positive integer, in paise"])
    return errors

def validate_availability(body):
    if not isinstance(body.get("available"), bool):
        return [["available", "required boolean"]]
    return []

def apply_override():
    override = request.headers.get("X-HTTP-Method-Override", "").upper()
    if request.method == "POST" and override in {"PUT", "PATCH", "DELETE"}:
        return override
    return request.method

@app.route("/", methods=["GET", "OPTIONS"])
def home():
    if request.method == "OPTIONS":
        return options_response("GET, OPTIONS")
    bad = check_accept()
    if bad: return bad
    return jsonify({"message": "Restaurant API is running!"}), 200

@app.route("/restaurants", methods=["GET", "OPTIONS"])
def list_restaurants():
    if request.method == "OPTIONS":
        return options_response("GET, OPTIONS")
    bad = check_accept()
    if bad: return bad
    area = request.args.get("area")
    if area is not None and not area.strip():
        return problem(400, "invalid-request", "area must not be blank")
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        return problem(400, "invalid-request", "page and limit must be integers")
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")
    if order not in {"asc", "desc"}:
        return problem(400, "invalid-request", "order must be asc or desc")
    items = store.list_restaurants(area, sort, order, page, limit)
    response = jsonify([r.as_json() for r in items])
    response.headers["X-Total-Count"] = str(store.restaurant_count(area))
    return response, 200

@app.route("/restaurants/<int:rid>/menu-items", methods=["GET", "POST", "OPTIONS"])
def restaurant_menu(rid):
    method = apply_override()
    if request.method == "OPTIONS":
        return options_response("GET, POST, OPTIONS")
    bad = check_accept()
    if bad: return bad
    restaurant = store.find_restaurant(rid)
    if restaurant is None:
        return problem(404, "restaurant-not-found", f"No restaurant {rid}")
    if method == "GET":
        try:
            page = max(1, int(request.args.get("page", 1)))
            limit = min(50, max(1, int(request.args.get("limit", 10))))
        except ValueError:
            return problem(400, "invalid-request", "page and limit must be integers")
        sort = request.args.get("sort")
        order = request.args.get("order", "asc")
        if order not in {"asc", "desc"}:
            return problem(400, "invalid-request", "order must be asc or desc")
        items = store.list_items_for_restaurant(rid, sort, order, page, limit)
        response = jsonify([m.as_json() for m in items])
        response.headers["X-Total-Count"] = str(store.item_count_for_restaurant(rid))
        return response, 200
    if method != "POST":
        return problem(405, "method-not-allowed", "use POST to create menu items")
    auth = auth_required(lambda: None)()
    if auth: return auth
    body = get_json_body()
    errs = validate_new_item(body)
    if errs:
        return problem(400, "invalid-request", errors=errs)
    key = request.headers.get("Idempotency-Key")
    if key:
        prior = store.find_item_by_key(key)
        if prior:
            return jsonify(prior.as_json()), 200
    if store.item_name_exists(rid, body["name"]):
        return problem(409, "duplicate-item", f"{body['name']} already on this menu")
    cap = TIER_CAPS[restaurant.tier]
    if body["price"] > cap:
        return problem(422, "price-exceeds-cap", f"{restaurant.tier} cap is {cap} paise")
    verified = verify_merchant_with_retry(rid)
    item = store.create_item(rid, body["name"], body["price"], int(body["price"] * .6), verified, key)
    response = jsonify(item.as_json())
    response.status_code = 201
    response.headers["Location"] = f"/menu-items/{item.id}"
    return response

@app.route("/menu-items/<int:iid>", methods=["GET", "PUT", "PATCH", "DELETE", "OPTIONS", "POST"])
def menu_item(iid):
    method = apply_override()
    if request.method == "OPTIONS":
        return options_response("GET, PUT, PATCH, DELETE, OPTIONS")
    bad = check_accept()
    if bad: return bad
    item = store.find_item(iid)
    if item is None:
        return problem(404, "item-not-found", f"No menu item {iid}")
    if method == "GET":
        tag = etag(item)
        if request.headers.get("If-None-Match") == tag:
            response = make_response("", 304)
            response.headers["ETag"] = tag
            return response
        response = jsonify(item.as_json())
        response.headers["ETag"] = tag
        return response, 200
    if method not in {"PUT", "PATCH", "DELETE"}:
        return problem(405, "method-not-allowed", "use GET, PUT, PATCH or DELETE")
    auth = auth_required(lambda: None)()
    if auth: return auth
    if method == "DELETE":
        old = store.delete_item(iid)
        return "", 204
    current_tag = etag(item)
    if request.headers.get("If-Match") != current_tag:
        return problem(412, "precondition-failed", "If-Match does not match the current ETag")
    body = get_json_body()
    if method == "PUT":
        errs = validate_new_item(body)
        if errs:
            return problem(400, "invalid-request", errors=errs)
        if store.item_name_exists(item.restaurant_id, body["name"], iid):
            return problem(409, "duplicate-item", f"{body['name']} already on this menu")
        restaurant = store.find_restaurant(item.restaurant_id)
        if body["price"] > TIER_CAPS[restaurant.tier]:
            return problem(422, "price-exceeds-cap", f"{restaurant.tier} cap is {TIER_CAPS[restaurant.tier]} paise")
        item.name = body["name"].strip()
        item.price = body["price"]
    else:
        if "name" in body:
            if not isinstance(body["name"], str) or not body["name"].strip():
                return problem(400, "invalid-request", errors=[["name", "non-empty string"]])
            if store.item_name_exists(item.restaurant_id, body["name"], iid):
                return problem(409, "duplicate-item", f"{body['name']} already on this menu")
            item.name = body["name"].strip()
        if "price" in body:
            if not isinstance(body["price"], int) or isinstance(body["price"], bool) or body["price"] <= 0:
                return problem(400, "invalid-request", errors=[["price", "positive integer, in paise"]])
            restaurant = store.find_restaurant(item.restaurant_id)
            if body["price"] > TIER_CAPS[restaurant.tier]:
                return problem(422, "price-exceeds-cap", f"{restaurant.tier} cap is {TIER_CAPS[restaurant.tier]} paise")
            item.price = body["price"]
        if "available" in body:
            if not isinstance(body["available"], bool):
                return problem(400, "invalid-request", errors=[["available", "boolean"]])
            restaurant = store.find_restaurant(item.restaurant_id)
            if body["available"] and not restaurant.active:
                return problem(409, "restaurant-inactive", "cannot list items while the restaurant is inactive")
            item.available = body["available"]
    item.version += 1
    return jsonify(item.as_json()), 200

@app.route("/menu-items/<int:iid>/availability", methods=["POST", "OPTIONS"])
def availability(iid):
    if request.method == "OPTIONS":
        return options_response("POST, OPTIONS")
    auth = auth_required(lambda: None)()
    if auth: return auth
    item = store.find_item(iid)
    if item is None:
        return problem(404, "item-not-found", f"No menu item {iid}")
    body = get_json_body()
    errs = validate_availability(body)
    if errs:
        return problem(400, "invalid-request", errors=errs)
    restaurant = store.find_restaurant(item.restaurant_id)
    if body["available"] and not restaurant.active:
        return problem(409, "restaurant-inactive", "cannot list items while the restaurant is inactive")
    item.available = body["available"]
    item.version += 1
    return jsonify(item.as_json()), 200

def options_response(allow):
    response = make_response("", 204)
    response.headers["Allow"] = allow
    return response


orders = {}
next_order_id = 1

logging.basicConfig(level=logging.INFO)


def order_response(order, status=200):
    accept = request.headers.get("Accept", "application/json")

    if "application/xml" in accept and (
        "application/json" not in accept and "*/*" not in accept
    ):
        items = "".join(
            f'<item><id>{i["id"]}</id><qty>{i["qty"]}</qty></item>'
            for i in order["items"]
        )
        xml = (
            f'<order><id>{order["id"]}</id>'
            f'<status>{escape(order["status"])}</status>'
            f'<address>{escape(order["address"])}</address>'
            f'<items>{items}</items></order>'
        )
        response = make_response(xml, status)
        response.headers["Content-Type"] = "application/xml; charset=utf-8"
        return response

    if "application/json" not in accept and "*/*" not in accept:
        return problem(406, "not-acceptable", "Use JSON or XML")

    response = jsonify(order)
    response.status_code = status
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


def validate_order(body):
    errors = []

    if not isinstance(body, dict):
        return [{"field": "body", "msg": "must be a JSON object"}]

    items = body.get("items")
    if not isinstance(items, list) or not items:
        errors.append({"field": "items", "msg": "must be non-empty"})
    else:
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append({
                    "field": f"items[{index}]",
                    "msg": "must be an object"
                })
                continue

            if not isinstance(item.get("id"), int) or isinstance(
                item.get("id"), bool
            ):
                errors.append({
                    "field": f"items[{index}].id",
                    "msg": "must be an integer"
                })

            qty = item.get("qty")
            if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
                errors.append({
                    "field": f"items[{index}].qty",
                    "msg": "must be an integer >= 1"
                })

    address = body.get("address")
    if not isinstance(address, str) or not address.strip():
        errors.append({"field": "address", "msg": "required"})

    return errors


@app.route("/orders", methods=["POST"])
def create_order():
    global next_order_id

    accept = request.headers.get("Accept", "application/json")
    if "application/xml" not in accept and (
        "application/json" not in accept and "*/*" not in accept
    ):
        return problem(406, "not-acceptable", "Use JSON or XML")

    body = request.get_json(silent=True)
    if body is None:
        body = {}

    errors = validate_order(body)
    if errors:
        code = (
            "empty-cart"
            if isinstance(body, dict)
            and body.get("items") == []
            else "validation-failed"
        )
        response = problem(422, code, "Correct the invalid fields", errors)
        return response

    try:
        order = {
            "id": next_order_id,
            "items": body["items"],
            "address": body["address"].strip(),
            "status": "draft"
        }
        orders[next_order_id] = order
        next_order_id += 1

        response = order_response(order, 201)
        response.headers["Location"] = f"/orders/{order['id']}"
        return response
    except Exception:
        logging.exception("Failed to create order")
        return problem(500, "internal-error", "Could not create order")


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if order is None:
        return problem(404, "order-not-found", "Order does not exist")

    return order_response(order)


@app.route("/orders/<int:order_id>", methods=["PATCH"])
def update_order(order_id):
    order = orders.get(order_id)
    if order is None:
        return problem(404, "order-not-found", "Order does not exist")

    body = request.get_json(silent=True) or {}
    new_status = body.get("status")

    allowed = {
        "draft": {"placed", "cancelled"},
        "placed": {"preparing", "cancelled"},
        "preparing": {"delivered"},
        "delivered": set(),
        "cancelled": set()
    }

    if new_status not in allowed.get(order["status"], set()):
        return problem(
            409, "illegal-transition",
            f"Cannot change {order['status']} to {new_status}"
        )

    order["status"] = new_status
    return order_response(order)


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = orders.get(order_id)
    if order is None:
        return problem(404, "order-not-found", "Order does not exist")

    if order["status"] != "draft":
        return problem(
            409, "illegal-transition", "Only draft orders can be cancelled"
        )

    del orders[order_id]
    return make_response("", 204)


if __name__ == "__main__":
    app.run(port=8080)
