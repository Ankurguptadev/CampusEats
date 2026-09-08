from flask import jsonify

TITLES = {
    "invalid-request": "Invalid request",
    "restaurant-not-found": "Restaurant not found",
    "item-not-found": "Menu item not found",
    "duplicate-item": "Menu item already exists",
    "price-exceeds-cap": "Price exceeds tier cap",
    "restaurant-inactive": "Restaurant is inactive",
}


def problem(status, code, detail="", errors=None):
    body = {
        "type": f"/errors/{code}",
        "title": TITLES[code],
        "status": status,
        "detail": detail,
    }
    if errors:
        body["errors"] = errors
    return jsonify(body), status
