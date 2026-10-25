from shop.cart import Cart
from shop.checkout import receipt


def test_under_threshold_no_discount():
    cart = Cart([("gadget", 3)])  # $99.99
    assert cart.discount() == 0
    assert cart.total() == 107.99


def test_over_threshold():
    cart = Cart([("widget", 6)])  # $150.00
    assert cart.discount() == 15.00
    assert cart.total() == 145.80
    assert "Total: $145.80" in receipt(cart)


def test_exact_threshold_receipt():
    text = receipt(Cart([("widget", 4)]))
    assert "Discount: $10.00" in text and "Total: $97.20" in text
