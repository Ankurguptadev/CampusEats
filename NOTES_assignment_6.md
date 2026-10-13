# CS543 Assignment 6 — CampusEats

| Name | Student Id |
|---|:---:|
| Ankur Gupta | 20252651008 |
| Kartik Karnwal | 20252651028 |
| Kirti Gautam | 20252651029 |
| Pintu | 20252651038 |

## 1. Status map

- `POST /orders`: `201 Created` when an order is created; `422` for invalid fields or an empty cart; `406` when the requested response format is unsupported; `429` when rate limited; `500` for an unexpected server failure.
- `GET /orders/{id}`: `200 OK` when found; `404` when the order does not exist; `406` when the requested response format is unsupported.
- `PATCH /orders/{id}`: `200 OK` when the status changes; `404` when the order does not exist; `409` when the requested transition is not allowed; `406` for an unsupported response format.
- `DELETE /orders/{id}`: `204 No Content` when a draft order is deleted; `404` when the order does not exist; `409` when the order is not a draft.
- Rate limiting returns `429 Too Many Requests` with `Retry-After`. A temporary service outage should return `503 Service Unavailable` with `Retry-After`.

## 2. Stable error type catalogue

- `empty-cart` — the order has no items.
- `item-unavailable` — an item cannot be ordered.
- `payment-declined` — payment is declined.
- `order-not-found` — the requested order ID does not exist.
- `illegal-transition` — the requested order status change is not allowed.
- `validation-failed` — one or more request fields are invalid.
- `not-acceptable` — the server cannot produce a representation accepted by the client.
- `rate-limit` — the client exceeded the request limit.
- `internal-error` — an unexpected server-side error occurred.

## 3. Problem Details example

```json
{
  "type": "/errors/order-not-found",
  "title": "Order not found",
  "status": 404,
  "detail": "Order does not exist"
}
```

- `type`: stable identifier for this error category.
- `title`: short human-readable summary.
- `status`: HTTP status code.
- `detail`: explanation safe to show to the client.

## 4. Field-level 422 example

Request:
```json
{"items":[{"id":7,"qty":0}]}
```

Example response (the quantity and address are both invalid):
```json
{
  "type": "/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "detail": "Correct the invalid fields",
  "errors": [
    {"field": "items[0].qty", "msg": "must be an integer >= 1"},
    {"field": "address", "msg": "required"}
  ]
}
```

## 5. Retry safety

- `GET /orders/{id}` is safe to retry because it does not modify the order.
- `DELETE /orders/{id}` is idempotent in intended effect, but a repeated request may return `404` after the first deletion.
- `POST /orders` should not be retried blindly unless an idempotency key is implemented and enforced.
- `PATCH /orders/{id}` should only be retried after checking the current order state, unless the operation is explicitly made idempotent.
- `429` and `503` responses include `Retry-After`; clients should wait before retrying transient failures. Do not retry unchanged 4xx requests.

## 6. Internal error mapping

Risky order creation is wrapped in `try/except`. The full exception is logged server-side with `logging.exception`, while the client receives a generic `500` Problem Details response. Stack traces, database messages, and internal implementation details must not be returned to the caller.

## 7. JSON and XML negotiation

Send `Accept: application/json` (or omit `Accept`) to request JSON. Send `Accept: application/xml` to request XML. If the server cannot produce any of the formats requested by `Accept`, it returns `406 Not Acceptable`.

