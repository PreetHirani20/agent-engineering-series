PRODUCTS = {
    "widget": {"name": "Widget", "price": 25.00, "weight_kg": 0.4},
    "gadget": {"name": "Gadget", "price": 33.33, "weight_kg": 1.2},
    "gizmo": {"name": "Gizmo", "price": 9.99, "weight_kg": 0.1},
    "doohickey": {"name": "Doohickey", "price": 120.00, "weight_kg": 3.5},
}


def get_price(sku):
    return PRODUCTS[sku]["price"]


def get_weight(sku):
    return PRODUCTS[sku]["weight_kg"]
