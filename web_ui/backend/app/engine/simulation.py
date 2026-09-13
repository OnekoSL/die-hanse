from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from app.domain.schemas import BacktestRunRequest
from app.engine.pricing import compute_price
from app.engine.strategy import choose_order


@dataclass
class ShipState:
    city: str
    destination: str | None = None
    eta: int = 0
    cargo_good: str | None = None
    cargo_qty: int = 0
    buy_cost: float = 0.0
    origin_city: str | None = None


@dataclass
class SimulationOutput:
    run_id: str
    status: str
    duration_ms: int
    summary: dict
    equity_curve: list[dict]
    city_snapshots: list[dict]
    trade_log: list[dict]
    violations: list[str]


@dataclass
class MarketState:
    cash: float
    inventory: dict[str, int] = field(default_factory=dict)


def _max_drawdown(points: list[dict]) -> float:
    peak = points[0]["equity"] if points else 0.0
    max_dd = 0.0
    for p in points:
        eq = p["equity"]
        peak = max(peak, eq)
        if peak > 0:
            max_dd = max(max_dd, (peak - eq) / peak)
    return round(max_dd, 4)


def _portfolio_value(
    cash: float, inventory: dict[str, int], city_prices: dict[str, dict[str, float]]
) -> float:
    # Mark-to-market uses average city price per good.
    avg_price: dict[str, float] = {}
    for city in city_prices.values():
        for good, price in city.items():
            avg_price.setdefault(good, 0.0)
            avg_price[good] += price
    city_count = len(city_prices)
    for good in avg_price:
        avg_price[good] /= max(city_count, 1)
    inv_val = sum(avg_price.get(g, 0) * q for g, q in inventory.items())
    return round(cash + inv_val, 2)


def run_backtest(payload: dict, config: BacktestRunRequest) -> SimulationOutput:
    started = time.perf_counter()
    run_id = str(uuid.uuid4())

    goods = payload["goods"]
    cities = payload["cities"]
    routes = {(r["from"], r["to"]): int(r["days"]) for r in payload["routes"]}
    ship_cfg = payload["ship"]
    ship_capacity_total = int(ship_cfg.get("capacity_total", ship_cfg["capacity"]))
    ship_max_per_good = int(ship_cfg.get("max_per_good", ship_capacity_total))

    stocks = {c["name"]: {g: int(c["goods"][g]["initial_stock"]) for g in goods} for c in cities}
    demand = {c["name"]: {g: int(c["goods"][g]["demand_per_day"]) for g in goods} for c in cities}
    production = {}
    violations: list[str] = []
    for city_entry in cities:
        city_name = city_entry["name"]
        production[city_name] = {}
        for good in goods:
            demand_value = int(city_entry["goods"][good]["demand_per_day"])
            production_value = int(
                city_entry["goods"][good].get("production_per_day", demand_value)
            )
            if production_value < 0:
                production_value = 0
                violations.append(
                    f"Start: production_per_day < 0 fuer {city_name}/{good}; auf 0 geklemmt"
                )
            production[city_name][good] = production_value
    target = {c["name"]: {g: int(c["goods"][g]["target_stock"]) for g in goods} for c in cities}
    base_price = {c["name"]: {g: float(c["goods"][g]["base_price"]) for g in goods} for c in cities}

    ship = ShipState(city=ship_cfg["start_city"])
    state = MarketState(cash=config.initial_cash, inventory={g: 0 for g in goods})

    trade_log: list[dict] = []
    city_snapshots: list[dict] = []
    equity_curve: list[dict] = []
    turnover = 0.0
    wins = 0
    closed_trades = 0

    for day in range(config.start_day, config.end_day + 1):
        for city in stocks:
            for good in goods:
                stocks[city][good] = max(
                    0,
                    stocks[city][good] + production[city][good] - demand[city][good],
                )

        prices = {
            city: {
                good: compute_price(
                    base_price=base_price[city][good],
                    stock=stocks[city][good],
                    target_stock=target[city][good],
                    day=day,
                    city=city,
                )
                for good in goods
            }
            for city in stocks
        }

        if ship.destination:
            ship.eta -= 1
            if ship.eta <= 0:
                ship.city = ship.destination
                ship.destination = None
                if ship.cargo_good and ship.cargo_qty > 0:
                    sell_price = prices[ship.city][ship.cargo_good]
                    revenue = sell_price * ship.cargo_qty
                    buy_cost = ship.buy_cost
                    pnl = revenue - buy_cost
                    state.cash += revenue
                    state.inventory[ship.cargo_good] -= ship.cargo_qty
                    trade_log.append(
                        {
                            "day": day,
                            "city_from": ship.origin_city or ship.city,
                            "city_to": ship.city,
                            "good": ship.cargo_good,
                            "qty": ship.cargo_qty,
                            "price": sell_price,
                            "pnl_delta": round(pnl, 2),
                            "side": "sell",
                        }
                    )
                    turnover += revenue
                    closed_trades += 1
                    if pnl > 0:
                        wins += 1
                    ship.cargo_good = None
                    ship.cargo_qty = 0
                    ship.buy_cost = 0.0
                    ship.origin_city = None

        if ship.destination is None:
            intent = choose_order(
                city=ship.city,
                prices=prices,
                stocks=stocks,
                routes=routes,
                goods=goods,
                capacity_total=ship_capacity_total,
                max_per_good=ship_max_per_good,
                cash=state.cash - config.risk_limits.min_cash_buffer,
            )
            if intent:
                if intent.qty > config.risk_limits.max_position_per_good:
                    intent.qty = config.risk_limits.max_position_per_good
                buy_price = prices[ship.city][intent.good]
                cost = round(intent.qty * buy_price, 2)
                if cost <= 0:
                    violations.append(f"Tag {day}: Ungueltige Kaufkosten fuer {intent.good}")
                elif state.cash - cost < config.risk_limits.min_cash_buffer:
                    violations.append(f"Tag {day}: Cash Buffer verletzt fuer {intent.good}")
                elif stocks[ship.city][intent.good] < intent.qty:
                    violations.append(
                        f"Tag {day}: Nicht genug Bestand in {ship.city} fuer {intent.good}"
                    )
                elif (ship.city, intent.destination) not in routes:
                    violations.append(f"Tag {day}: Route fehlt {ship.city}->{intent.destination}")
                else:
                    state.cash -= cost
                    stocks[ship.city][intent.good] -= intent.qty
                    state.inventory[intent.good] += intent.qty
                    trade_log.append(
                        {
                            "day": day,
                            "city_from": ship.city,
                            "city_to": intent.destination,
                            "good": intent.good,
                            "qty": intent.qty,
                            "price": buy_price,
                            "pnl_delta": 0.0,
                            "side": "buy",
                        }
                    )
                    turnover += cost
                    ship.destination = intent.destination
                    ship.eta = routes[(ship.city, intent.destination)]
                    ship.origin_city = ship.city
                    ship.cargo_good = intent.good
                    ship.cargo_qty = intent.qty
                    ship.buy_cost = cost

        for city in stocks:
            for good in goods:
                city_snapshots.append(
                    {
                        "day": day,
                        "city": city,
                        "good": good,
                        "stock": stocks[city][good],
                        "demand": demand[city][good],
                        "price": prices[city][good],
                    }
                )

        equity_curve.append(
            {"day": day, "equity": _portfolio_value(state.cash, state.inventory, prices)}
        )

    final_equity = equity_curve[-1]["equity"] if equity_curve else config.initial_cash
    pnl = round(final_equity - config.initial_cash, 2)
    roi = round((pnl / config.initial_cash) if config.initial_cash else 0.0, 4)
    summary = {
        "roi": roi,
        "pnl": pnl,
        "max_drawdown": _max_drawdown(equity_curve),
        "win_rate_trades": round((wins / closed_trades) if closed_trades else 0.0, 4),
        "turnover": round(turnover, 2),
    }

    duration_ms = int((time.perf_counter() - started) * 1000)
    return SimulationOutput(
        run_id=run_id,
        status="completed",
        duration_ms=duration_ms,
        summary=summary,
        equity_curve=equity_curve,
        city_snapshots=city_snapshots,
        trade_log=trade_log,
        violations=violations,
    )
