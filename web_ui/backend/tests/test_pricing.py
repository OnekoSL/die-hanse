from app.engine.pricing import compute_price


def test_price_increases_when_stock_low():
    low = compute_price(base_price=10, stock=10, target_stock=100, day=1, city="Luebeck")
    high = compute_price(base_price=10, stock=200, target_stock=100, day=1, city="Luebeck")
    assert low > high


def test_price_is_clamped():
    p = compute_price(
        base_price=10, stock=10000, target_stock=100, day=1, city="Luebeck", min_factor=0.5
    )
    assert p >= 5.0
