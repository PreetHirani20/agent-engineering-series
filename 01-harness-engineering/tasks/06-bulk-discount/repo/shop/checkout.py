from .cart import Cart
from .formatting import money
from .shipping import shipping_cost


def receipt(cart: Cart) -> str:
    sub = cart.subtotal()
    ship = shipping_cost(cart.items, sub)
    lines = [
        f"Items: {sum(q for _, q in cart.items)}",
        f"Subtotal: {money(sub)}",
        f"Discount: {money(cart.discount())}",
        f"Total: {money(cart.total())}",
        f"Shipping: {money(ship)}",
    ]
    return "\n".join(lines)
