from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OrderIntent:
    good: str
    qty: int
    destination: str


def choose_order(
    *,
    city: str,
    prices: dict[str, dict[str, float]],
    stocks: dict[str, dict[str, int]],
    routes: dict[tuple[str, str], int],
    goods: list[str],
    capacity_total: int,
    max_per_good: int,
    cash: float,
) -> OrderIntent | None:
    best: tuple[float, str, str, int] | None = None
    for good in goods:
        buy_price = prices[city][good]
        if buy_price <= 0:
            continue
        max_qty = min(capacity_total, max_per_good, stocks[city][good], int(cash // buy_price))
        if max_qty <= 0:
            continue
        for target_city, city_prices in prices.items():
            if target_city == city:
                continue
            if (city, target_city) not in routes:
                continue
            spread = city_prices[good] - buy_price
            if spread <= 0:
                continue
            expected = spread * max_qty
            if not best or expected > best[0]:
                best = (expected, good, target_city, max_qty)

    if not best:
        return None
    _, good, target_city, qty = best
    return OrderIntent(good=good, qty=qty, destination=target_city)
