from shop.cart import Cart
from shop.checkout import receipt


def test_exactly_100_gets_discount():
    cart = Cart([("widget", 4)])  # 4 x $25.00 = $100.00
    assert cart.subtotal() == 100.00
    assert cart.total() == 97.20


def test_small_order_receipt():
    cart = Cart([("gizmo", 2)])
    text = receipt(cart)
    assert "Subtotal: $19.98" in text
    assert "Shipping: $5.99" in text
