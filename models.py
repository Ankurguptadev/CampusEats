# from dataclasses import dataclass, field
# from datetime import datetime, timezone

# # Price caps per restaurant tier, in paise (integers only — never floats for money).
# TIER_CAPS = {"budget": 50000, "premium": 200000}


# @dataclass
# class Restaurant:
#     id: int
#     name: str
#     area: str
#     tier: str            # "budget" | "premium"
#     active: bool = True

#     def as_json(self) -> dict:
#         return {
#             "id": self.id,
#             "name": self.name,
#             "area": self.area,
#             "tier": self.tier,
#             "active": self.active,
#         }


# @dataclass
# class MenuItem:
#     id: int
#     restaurant_id: int
#     name: str
#     price: int                     # paise, integer only
#     cost_price: int                # internal wholesale cost — NEVER exposed
#     available: bool = True
#     merchant_verified: bool = False  # internal flag set by the Payments check — NEVER exposed
#     idempotency_key: str | None = None  # NEVER exposed
#     created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

#     def as_json(self) -> dict:
#         return {
#             "id": self.id,
#             "restaurantId": self.restaurant_id,
#             "name": self.name,
#             "price": self.price,
#             "available": self.available,
#             "createdAt": self.created_at.isoformat(),
#         }  # cost_price, merchant_verified, idempotency_key deliberately not exposed


from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Restaurant:
    id: int
    name: str
    area: str
    tier: str
    active: bool

    def as_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "tier": self.tier,
            "active": self.active,
        }

@dataclass
class MenuItem:
    id: int
    restaurant_id: int
    name: str
    price: int
    cost_price: int
    merchant_verified: bool
    idempotency_key: str | None = None
    available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    def as_json(self):
        return {
            "id": self.id,
            "restaurantId": self.restaurant_id,
            "name": self.name,
            "price": self.price,
            "available": self.available,
            "createdAt": self.created_at.isoformat(),
        }

TIER_CAPS = {"budget": 50000, "premium": 200000}
