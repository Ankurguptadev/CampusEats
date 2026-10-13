
from flask import jsonify, request

TITLES = {
    "empty-cart": "Empty cart",
    "item-unavailable": "Item unavailable",
    "payment-declined": "Payment declined",
    "order-not-found": "Order not found",
    "illegal-transition": "Illegal transition",
    "validation-failed": "Validation failed",
    "invalid-request": "Invalid request",
    "not-acceptable": "Not acceptable",
    "internal-error": "Internal server error",
    "rate-limit": "Too many requests",
}

def problem(status, code, detail="", errors=None):
    body = {
        "type": f"/errors/{code}",
        "title": TITLES.get(code, code.replace("-", " ").title()),
        "status": status,
        "detail": detail,
    }

    if errors is not None:
        body["errors"] = errors

    response = jsonify(body)
    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json; charset=utf-8"

    if status in (429, 503):
        response.headers["Retry-After"] = "60"

    return response
