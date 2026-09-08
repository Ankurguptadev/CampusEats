from models import Restaurant, MenuItem

_restaurants: dict[int, Restaurant] = {}
_menu_items: dict[int, MenuItem] = {}
_by_key: dict[str, int] = {}   # Idempotency-Key -> menu item id
_next_restaurant_id = 1
_next_item_id = 1


def seed():
    """Demo data: three restaurants, one of them inactive, for testing 409s.
    Also seeds two fixed menu items (ids 1 and 2) so the Orders service
    has stable items to call, without depending on request order."""
    global _next_restaurant_id
    demo = [
        ("Curry Point", "North Campus", "budget", True),
        ("Sushi Central", "South Campus", "premium", True),
        ("Old Kitchen", "North Campus", "budget", False),  # inactive on purpose
    ]
    for name, area, tier, active in demo:
        r = Restaurant(id=_next_restaurant_id, name=name, area=area, tier=tier, active=active)
        _restaurants[r.id] = r
        _next_restaurant_id += 1

    create_item(1, "Veg Thali", 8000, 4800, True)       # id 1 — available
    create_item(1, "Cold Coffee", 6000, 2400, True)     # id 2 — available
    _menu_items[2].available = False                    # id 2 — marked unavailable, for the 422 demo


def reset():
    """Test-only: wipe all state and reseed. No other service may call this."""
    global _next_restaurant_id, _next_item_id
    _restaurants.clear()
    _menu_items.clear()
    _by_key.clear()
    _next_restaurant_id = 1
    _next_item_id = 1
    seed()


def find_restaurant(rid):
    return _restaurants.get(rid)


def list_restaurants(area=None):
    vals = list(_restaurants.values())
    if area:
        vals = [r for r in vals if r.area.lower() == area.lower()]
    return vals


def find_item(iid):
    return _menu_items.get(iid)


def find_item_by_key(key):
    return _menu_items.get(_by_key.get(key))


def list_items_for_restaurant(rid):
    return [m for m in _menu_items.values() if m.restaurant_id == rid]


def item_name_exists(restaurant_id, name):
    return any(
        m.restaurant_id == restaurant_id and m.name.lower() == name.lower()
        for m in _menu_items.values()
    )


def create_item(restaurant_id, name, price, cost_price, merchant_verified, key=None):
    global _next_item_id
    m = MenuItem(
        id=_next_item_id, restaurant_id=restaurant_id, name=name,
        price=price, cost_price=cost_price, merchant_verified=merchant_verified,
        idempotency_key=key,
    )
    _menu_items[m.id] = m
    if key:
        _by_key[key] = m.id
    _next_item_id += 1
    return m
