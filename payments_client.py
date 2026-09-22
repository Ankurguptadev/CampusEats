"""
Catalogue's one outbound call to another CampusEats service (Part D).

Why this call exists: before a restaurant is allowed to list a new paid
menu item, Catalogue checks that the restaurant's merchant/payment profile
is active, by asking Payments whether it has ever settled a payment for
that restaurant. This reuses Payments' existing GET /payments?order={id}
endpoint from Tutorial 4 as a stand-in "merchant verification" ping, as
permitted by the assignment ("the Payments service from Tutorial 4 is
fine") — it is not meant to be a realistic merchant-KYC check.

Hardening:
  - timeout on every call, so a hung dependency can never hang Catalogue
  - retry only on transport failures / 5xx, with exponential backoff + jitter
  - a 4xx from Payments is OUR bug (bad query), so it is raised immediately
    and never retried
  - this call is read-only (GET), so no Idempotency-Key is needed here —
    that only matters for retried CREATEs, which this is not
"""
import os
import time
import random
import requests

PAYMENTS_URL = os.environ.get("PAYMENTS_URL", "http://localhost:8081")


class PaymentsUnavailable(Exception):
    """Transport failure or 5xx — safe to retry."""


def _ping_payments(restaurant_id: int, timeout: float = 2.0) -> bool:
    r = requests.get(
        f"{PAYMENTS_URL}/payments",
        params={"order": restaurant_id},
        timeout=timeout,
    )
    if r.status_code >= 500:
        raise PaymentsUnavailable(f"payments returned {r.status_code}")
    r.raise_for_status()  
    return True


def verify_merchant_with_retry(restaurant_id: int, attempts: int = 3) -> bool:
    """
    Returns True if Payments confirmed the merchant is active, False if
    Payments could not be reached after all retries. Never raises for
    transport failures — the caller (app.py) decides the fallback.
    A 4xx from Payments IS raised, because that means our own request
    was malformed and retrying it would never help.
    """
    for attempt in range(attempts):
        try:
            return _ping_payments(restaurant_id)
        except requests.exceptions.HTTPError:
            raise
        except (PaymentsUnavailable, requests.exceptions.RequestException):
            if attempt == attempts - 1:
                return False
            wait = (2 ** attempt) + random.random() 
            time.sleep(wait)
    return False
