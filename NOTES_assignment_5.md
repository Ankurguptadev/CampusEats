# CampusEats — Assignment 5 — HTTP Methods & Headers

| Name | Student Id |
|---|:---:|
| Ankur Gupta | 20252651008 |
| Kartik Karnwal | 20252651028 |
| Kirti Gautam | 20252651029 |
| Pintu | 20252651038 |

This is a **continuation of Assignment 4 Catalogue Service**. The existing REST resources were kept and extended with HTTP methods, headers, caching, safe retries, conditional requests, CORS, authorization and rate-limit signalling.

## A1 — CampusEats method map

| Action | Method | URL |
|---|---|---|
| List restaurants | GET | `/restaurants?area=North%20Campus&page=1&limit=10&sort=name&order=asc` |
| Read restaurant menu | GET | `/restaurants/{restaurantId}/menu-items` |
| Create menu item | POST | `/restaurants/{restaurantId}/menu-items` |
| Read one menu item | GET | `/menu-items/{id}` |
| Replace menu item | PUT | `/menu-items/{id}` |
| Partially modify menu item | PATCH | `/menu-items/{id}` |
| Remove menu item | DELETE | `/menu-items/{id}` |
| Change availability action | POST | `/menu-items/{id}/availability` |
| Discover allowed methods | OPTIONS | `/menu-items/{id}` |

The list endpoints use query parameters for filtering, sorting and pagination. No GET changes state.

## A2 — Non-CRUD action

Changing availability remains an action, so it is represented as:

`POST /menu-items/{id}/availability`

This avoids an action name such as `/setAvailability` in the URL.

## A3 — Safe and idempotent

| Endpoint | Safe? | Idempotent? | Reason |
|---|---|---|---|
| GET `/restaurants` | Yes | Yes | Read only |
| GET `/restaurants/{id}/menu-items` | Yes | Yes | Read only |
| GET `/menu-items/{id}` | Yes | Yes | Read only |
| POST create | No | No by default | A repeated request can create another item |
| POST create + same Idempotency-Key | No | Yes for that key | Same key returns the original result |
| POST availability | No | Yes for same target value | Repeating the same state change gives the same state |
| PUT `/menu-items/{id}` | No | Yes | Replaces the resource with the same representation |
| PATCH `/menu-items/{id}` | No | Not guaranteed | A patch can depend on the current state |
| DELETE `/menu-items/{id}` | No | Yes | Repeating delete leaves it deleted |
| OPTIONS | Yes | Yes | Metadata only |

The create endpoint is neither safe nor naturally idempotent. `Idempotency-Key` makes retries safe by returning the first created resource instead of creating a duplicate.

## A4 — Query parameters

Example:

`GET /restaurants?area=North%20Campus&page=1&limit=10&sort=name&order=asc`

POST is not used for ordinary filtering because this is a safe read and query parameters keep the operation cacheable and visible as a GET.

## A5 — OPTIONS, Allow and method override

`OPTIONS /menu-items/1` returns an `Allow` header such as:

`GET, PUT, PATCH, DELETE, OPTIONS`

CORS preflight headers are also returned.

For constrained clients, `X-HTTP-Method-Override: PATCH` is accepted on a POST request to a menu-item resource. It is documented as a fallback, not a replacement for normal HTTP methods.

## B1 — Content negotiation

JSON is the API representation. Every response carrying a JSON body uses:

`Content-Type: application/json`

The service accepts `Accept: application/json` (and `*/*`). An unsupported requested representation such as `Accept: text/html` returns:

`406 Not Acceptable`

Large JSON responses can be gzip encoded when the client sends `Accept-Encoding: gzip`.

## B2 — Status and Location

- `201 Created` is used for a new menu item and includes `Location: /menu-items/{id}`.
- `200 OK` is used for successful reads and updates.
- `204 No Content` is used for DELETE.
- `400 Bad Request` is used for malformed/invalid request data.
- `404 Not Found` is used for missing resources.
- `409 Conflict` is used for duplicate names and inactive-restaurant availability conflicts.
- `422 Unprocessable Entity` is used when the request is structurally valid but violates the restaurant tier price rule.
- `412 Precondition Failed` is used for a stale `If-Match`.

## B3 — Authorization

Protected write endpoints require:

`Authorization: Bearer <token>`

There is no real token system. The assignment only requires header handling, so any non-empty Bearer token is accepted. Missing or empty tokens return `401 Unauthorized`.

## B4 — Cache-Control and ETag

`GET /menu-items/{id}` returns an ETag and cacheable response:

`ETag: "..."`

When the resource changes, its representation changes and therefore its ETag changes.

A matching:

`If-None-Match: "..."`

returns `304 Not Modified` with no body.

## B5 — Rate-limit signalling

The service returns:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`

The budget is per client identity (Authorization header or remote address), not global. When the write budget is exceeded, the response is:

`429 Too Many Requests`

with:

`Retry-After: 60`

## B6 — CORS

The service returns:

`Access-Control-Allow-Origin: *`

and answers OPTIONS preflight requests with the allowed methods and request headers. This lets a browser application on another origin make the API call when the browser's CORS rules permit it.

## B7 — Security and general headers

The service sends:

- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security: max-age=31536000`
- `Date` and `Server` are supplied by the Flask/Werkzeug server.

Production deployment should use HTTPS so HSTS has the intended effect.

## C1 — Conditional GET

Example:

1. `GET /menu-items/1`
2. Response contains `ETag: "abc..."`
3. Client sends `If-None-Match: "abc..."`
4. If unchanged, server returns `304 Not Modified` with no body.

This saves the response body and bandwidth when the cached representation is still current.

## C2 — Conditional write

Updates require `If-Match`.

If the client sends an old ETag after another editor has changed the item, the service returns:

`412 Precondition Failed`

This prevents one editor from overwriting another editor's newer representation.

## C3 — Idempotency key

The create request supports `Idempotency-Key`.

The first request creates the item. A repeated request with the same key returns the original item with `200` instead of creating another item.

A duplicate order/payment could cause real damage because a retry could otherwise create or charge twice. The key provides retry protection for this kind of operation.

## C4 — Safe-retry plan

| Risky endpoint | Mechanism | Why |
|---|---|---|
| POST create menu item | Idempotency-Key | Prevent duplicate creation on network retry |
| PUT menu item | If-Match | Prevent stale replacement |
| PATCH menu item | If-Match | Prevent stale partial modification |
| DELETE menu item | HTTP idempotence | Repeating delete has the same final state |
| GET menu item | If-None-Match | Avoid transferring unchanged data |

## D2 — Headers table

| Endpoint | Request headers | Response headers |
|---|---|---|
| GET `/restaurants` | Accept | Content-Type, Cache-Control, CORS, rate-limit |
| GET `/menu-items/{id}` | Accept, If-None-Match | Content-Type, ETag, Cache-Control, security |
| POST create | Authorization, Content-Type, Accept, Idempotency-Key | Content-Type, Location, no-store, rate-limit |
| PUT/PATCH | Authorization, Content-Type, Accept, If-Match | Content-Type, no-store, rate-limit |
| DELETE | Authorization, Accept | no-store, rate-limit |
| OPTIONS | Origin, Access-Control-Request-Method, Access-Control-Request-Headers | Allow, CORS headers |
| Availability POST | Authorization, Content-Type, Accept | Content-Type, no-store, rate-limit |

## D3 — curl verification

See `curl-transcript.txt`. It contains the required successful create, repeated idempotent create, 304, 412, 400, 404 and 401 exchanges, plus OPTIONS and override examples.

## Eight answers

### 1. Three endpoints: method, success status and important response header

**Create menu item:** POST `/restaurants/1/menu-items` → `201 Created` → `Location`. It tells the client where the new resource lives.

**Read menu item:** GET `/menu-items/1` → `200 OK` → `ETag`. It identifies the representation for cache validation and conditional writes.

**Delete menu item:** DELETE `/menu-items/1` → `204 No Content` → `X-RateLimit-Remaining`. It tells the client how much of its current request budget remains.

### 2. Safe and idempotent endpoints

The GET and OPTIONS operations are safe because they do not change application state. GET, OPTIONS, PUT and DELETE are idempotent by their defined behavior here. A normal POST create is neither. It becomes retry-safe when an `Idempotency-Key` is supplied and reused. PATCH is not treated as naturally idempotent because the result can depend on the current representation.

### 3. ETag, 304 and 412

Example ETag:

`ETag: "7a9b3c2d..."`

A request with `If-None-Match` equal to that ETag returns `304 Not Modified`, saving a response body and bandwidth.

A write with an old `If-Match` returns `412 Precondition Failed`, preventing a stale editor from overwriting a newer resource.

### 4. 422 versus 400

**400 example:**

`POST /restaurants/1/menu-items` with body `{"name":"Tea"}`.

The required `price` field is missing, so the message is malformed for this API.

**422 example:**

`POST /restaurants/1/menu-items` with body `{"name":"Premium Thali","price":60000}`.

The JSON shape is valid, but the budget restaurant's domain rule rejects a price above 50000 paise.

### 5. CORS

The browser enforces the same-origin/CORS policy. A server can log and return `200`, but the browser can still prevent JavaScript from reading the response. `Access-Control-Allow-Origin` is the response header that authorizes the requesting origin. This service uses `*`.

### 6. Cacheable and no-store responses

A single-item GET can use `Cache-Control: public, max-age=60` because it is a read and has an ETag for validation.

A create/update/delete response uses `Cache-Control: no-store` because it is a state-changing operation and should not be reused from a cache.

### 7. When POST is right for search

GET is appropriate when search/filter parameters are small and can safely appear in the URL.

POST can be justified when the search is complex or the criteria are too large/sensitive to fit comfortably in a query string. The trade-off is that POST is not a safe read method, so normal GET caching, bookmarking and straightforward URL sharing become less convenient.

### 8. Location on 201 and 3xx

On `201 Created`, `Location` points to the newly created resource, for example `/menu-items/6`.

On a `3xx` redirect, `Location` points to the URI the client should request next.

## Run

```text
cd docs
pip install -r requirements.txt
python app.py
```

Run tests:

```text
pytest -q
```

The service listens on `http://localhost:8080`.
