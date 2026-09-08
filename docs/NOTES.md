# CampusEats — Assignment 4 — Catalogue Service

| Name | Student Id |
|---|:---:|
| Ankur Gupta | 20252651008 |
| Kartik Karnwal | 20252651028 |
| Kirti Gautam | 20252651029 |
| Pintu | 20252651038 |

We picked **Catalogue** (restaurants, menu items, prices).

---

## A2 — The old SOAP-style operations

Before turning this into a REST API, here's what it would have looked like as SOAP calls (full version in `catalogue.wsdl`):

- `listRestaurants(area?)` → list of restaurants
- `getMenu(restaurantId)` → list of items
- `checkItem(itemId)` → is it available, and the price
- `addMenuItem(restaurantId, name, price)` → new item's id
- `setAvailability(itemId, available)` → status

---

## A4 — Resource table

| Method | URL | What it does | Success | Failure |
|---|---|---|---|---|
| GET | `/restaurants?area={area}` | list restaurants, can filter by area | 200 | 400 |
| GET | `/restaurants/{restaurantId}/menu-items` | get one restaurant's menu | 200 | 404 |
| GET | `/menu-items/{id}` | get one menu item | 200 | 404 |
| POST | `/restaurants/{restaurantId}/menu-items` | add a new menu item | 201 | 400 · 404 · 409 · 422 |
| POST | `/menu-items/{id}/availability` | turn an item on/off | 200 | 400 · 404 · 409 |

The 5 old SOAP operations became 3 URLs. `setAvailability` got its own mini-URL instead of staying a separate operation.

---

## A5 — The one that didn't fit nicely

`setAvailability` was the awkward one. It's not really a "thing" — it's an action (turn an item on or off). We had two choices: make it a small edit (`PATCH`) on the menu item, or give it its own URL. We went with its own URL — `POST /menu-items/{id}/availability` — because turning an item on has a rule attached to it (you can't turn on an item if the restaurant itself is inactive), and it felt cleaner to keep that rule in its own spot instead of hiding it inside a generic edit.

---

## D3 — What happens if Payments is down

When we add a menu item, we also ping Payments to check the restaurant is a real paying merchant. If Payments doesn't answer, we still create the menu item — we just quietly mark it as "not checked yet" behind the scenes (the customer never sees this). We chose to let it go through instead of blocking it, because adding a menu item has nothing to do with whether Payments is working right now. Stopping restaurants from updating their menu just because a different, unrelated service is down would be a dumb way to fail.

---

## Answers

### 1. Line counts

```
174 lines — catalogue.wsdl
208 lines — openapi.yaml
```

Quick note: our actual Assignment 3 was about a different partner (the SMS gateway), not Catalogue, so comparing that file directly wouldn't really mean anything. So we wrote `catalogue.wsdl` fresh, in the same old SOAP style, just so this comparison is fair.

Surprise: the OpenAPI file is actually longer, not shorter. That's because OpenAPI repeats itself — every single response code needs its own little block, even if it's just pointing to the same schema. The WSDL says each field's shape once and moves on.

Two things WSDL had that OpenAPI doesn't need:
- **binding** — a whole section just to say "this uses SOAP over HTTP." A plain URL already means HTTP, no need to say it again.
- **service/port** — a whole section just to hold the address. OpenAPI just has one line: `servers: - url: ...`

### 2. A fault, before and after

Old way (SOAP), if you tried to add a duplicate item:

```xml
<soap:Fault>
  <faultcode>soap:Client</faultcode>
  <faultstring>Menu item already exists</faultstring>
  <detail><cat:error code="duplicate_item"/></detail>
</soap:Fault>
```

New way (from our real curl test):

```
HTTP/1.1 409 CONFLICT
{"type":"/errors/duplicate-item","title":"Menu item already exists",
 "status":409,"detail":"Paneer Wrap already on this menu"}
```

Why hiding an error inside a "200 OK" is bad: things like caches, load balancers, and monitoring tools only check the status code — they don't read the message inside. If everything says "200 OK," they all think it worked, even when it didn't. A "409" tells them the truth without them having to open the box.

### 3. What happened to UDDI

**Find** — still happens, just simpler. We read `PAYMENTS_URL` from an environment variable instead of asking a registry "who offers payments?"

**Publish** — still happens, but we don't do it by hand anymore. Whatever starts the Payments service (Docker, etc.) makes its name work automatically.

**Bind** — gone completely. There's no extra step to "connect" to it — it's just a normal web request.

### 4. What replaced the schema check

In the code, `validate_new_item()` and `validate_availability()` do this job now. They check the request before anything else touches it.

Example of what would break without them: someone sends `"price": "twelve"` (text instead of a number). Nothing would stop that from reaching our code, and it would either crash the app or save a broken price nobody can charge or show properly.

### 5. Where we'd still pick SOAP

Not "nowhere" — somewhere. If CampusEats ever talks to a bank (like in Assignment 3's SMS/payment partner work), we'd still pick SOAP there. Why: a bank needs a real, provable guarantee that a payment either goes through completely or not at all, with the message itself locked and signed — not just "we promise not to charge twice" using a header like we do here. That's a much stronger guarantee than what plain REST + an idempotency key gives you.
