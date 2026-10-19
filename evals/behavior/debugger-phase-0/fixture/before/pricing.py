"""Order pricing for the widget shop. All amounts are in cents."""

BULK_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 10
FLAT_SHIPPING_CENTS = 499
FREE_SHIPPING_FROM_CENTS = 5000


def line_total_cents(unit_price_cents: int, quantity: int) -> int:
    """Price one order line. Orders of BULK_THRESHOLD or more units get the bulk discount."""
    subtotal = unit_price_cents * quantity
    if quantity > BULK_THRESHOLD:
        subtotal -= subtotal * BULK_DISCOUNT_PERCENT // 100
    return subtotal


def shipping_cents(goods_cents: int) -> int:
    return 0 if goods_cents >= FREE_SHIPPING_FROM_CENTS else FLAT_SHIPPING_CENTS


def invoice_total_cents(lines: list[tuple[int, int]]) -> int:
    """Total an invoice of (unit_price_cents, quantity) lines, shipping included."""
    goods = sum(line_total_cents(price, qty) for price, qty in lines)
    return goods + shipping_cents(goods)
