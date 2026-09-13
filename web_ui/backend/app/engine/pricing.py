from __future__ import annotations

import math


def seasonal_factor(day: int, city: str) -> float:
    phase = (sum(ord(ch) for ch in city) % 30) / 30.0
    return 1.0 + 0.03 * math.sin((2 * math.pi * day / 30.0) + phase)


def compute_price(
    *,
    base_price: float,
    stock: int,
    target_stock: int,
    day: int,
    city: str,
    min_factor: float = 0.5,
    max_factor: float = 2.0,
) -> float:
    safe_target = max(target_stock, 1)
    stock_ratio = max(stock, 0) / safe_target
    raw_factor = 1.2 - 0.7 * stock_ratio
    clamped = max(min_factor, min(max_factor, raw_factor))
    price = base_price * clamped * seasonal_factor(day, city)
    return round(max(0.01, price), 2)
