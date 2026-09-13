from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from copy import deepcopy

from fastapi import HTTPException

from app.engine.game_world import AVATAR_BY_ID, AVATAR_ITEMS, DEFAULT_AVATAR_ID, GAME_WORLD

MIN_SPREAD = 0.08
MAX_SPREAD = 0.25
MAX_STOCK = 200
ZERO_DAYS_CAP = 30
STORAGE_MAX_LEVEL = 4
SELL_FACTOR = 0.5
SHIP_CATALOG = {item["id"]: item for item in GAME_WORLD["ship_catalog"]}
STORAGE_LEVELS = {int(item["level"]): item for item in GAME_WORLD["storage_levels"]}


def _init_stock_by_goods() -> dict[str, int]:
    return {good: 0 for good in GAME_WORLD["goods"]}


def _inventory_total(inventory: dict[str, int]) -> int:
    return int(sum(int(value) for value in inventory.values()))


def _good_amount(inventory: dict[str, int], good: str) -> int:
    return int(inventory.get(good, 0))


def _storage_total(storage: dict) -> int:
    return _inventory_total(storage["stock_by_good"])


def _ship_total(ship: dict) -> int:
    return _inventory_total(ship["cargo"])


def _market_map(markets: list[dict]) -> dict[tuple[str, str], dict]:
    return {(item["city"], item["good"]): item for item in markets}


def _storage_map(storages: list[dict]) -> dict[str, dict]:
    return {item["city"]: item for item in storages}


def _storage_capacity_for_level(level: int) -> int:
    if level <= 0:
        return 0
    return int(STORAGE_LEVELS[level]["capacity_total"])


def _storage_max_per_good_for_level(level: int) -> int:
    if level <= 0:
        return 0
    return int(STORAGE_LEVELS[level]["max_per_good"])


def _storage_price_for_level(level: int) -> int:
    if level <= 0:
        return 0
    return int(STORAGE_LEVELS[level]["buy_price"])


def _catalog_sell_price(buy_price: int) -> int:
    return int(buy_price) // 2


def _ship_capacity_total(ship: dict) -> int:
    if "capacity_total" in ship:
        return int(ship["capacity_total"])
    return int(ship.get("capacity", GAME_WORLD["start"]["ship_capacity"]))


def _ship_max_per_good(ship: dict) -> int:
    if "max_per_good" in ship:
        return int(ship["max_per_good"])
    class_id = ship.get("class_id")
    ship_class = SHIP_CATALOG.get(class_id, {})
    if "max_per_good" in ship_class:
        return int(ship_class["max_per_good"])
    return _ship_capacity_total(ship)


def _storage_capacity_total(storage: dict) -> int:
    if "capacity_total" in storage:
        return int(storage["capacity_total"])
    return int(storage.get("capacity", 0))


def _storage_max_per_good(storage: dict) -> int:
    if "max_per_good" in storage:
        return int(storage["max_per_good"])
    level = int(storage.get("level", 0))
    if level > 0:
        level_item = STORAGE_LEVELS.get(level)
        if level_item and "max_per_good" in level_item:
            return int(level_item["max_per_good"])
    return _storage_capacity_total(storage)


def _remaining_total(capacity_total: int, inventory: dict[str, int]) -> int:
    return max(0, int(capacity_total) - _inventory_total(inventory))


def _remaining_per_good(max_per_good: int, inventory: dict[str, int], good: str) -> int:
    return max(0, int(max_per_good) - _good_amount(inventory, good))


def _validate_add_to_ship(ship: dict, good: str, qty: int) -> None:
    total_remaining = _remaining_total(_ship_capacity_total(ship), ship["cargo"])
    if qty > total_remaining:
        raise HTTPException(status_code=422, detail="Schiffskapazitaet gesamt erreicht")
    good_remaining = _remaining_per_good(_ship_max_per_good(ship), ship["cargo"], good)
    if qty > good_remaining:
        raise HTTPException(status_code=422, detail="Schifflimit pro Ware erreicht")


def _validate_add_to_storage(storage: dict, good: str, qty: int) -> None:
    total_remaining = _remaining_total(_storage_capacity_total(storage), storage["stock_by_good"])
    if qty > total_remaining:
        raise HTTPException(status_code=422, detail="Kontorkapazitaet gesamt erreicht")
    good_remaining = _remaining_per_good(
        _storage_max_per_good(storage), storage["stock_by_good"], good
    )
    if qty > good_remaining:
        raise HTTPException(status_code=422, detail="Kontorlimit pro Ware erreicht")


def _resolve_travel_days(base_days: int, state: dict) -> int:
    seasonality = GAME_WORLD.get("travel_seasonality", {})
    enabled = bool(seasonality.get("enabled", False))
    if not enabled:
        return max(1, int(base_days))

    mode = str(seasonality.get("mode", "normal"))
    profiles = seasonality.get("profiles", {})
    factor = float(profiles.get(mode, 1.0))
    adjusted = round(base_days * factor)
    return max(1, int(adjusted))


def _ship_map(state: dict) -> dict[str, dict]:
    _normalize_state(state)
    return {item["id"]: item for item in state["ships"]}


def _active_ship(state: dict) -> dict:
    _normalize_state(state)
    ship = _ship_map(state).get(state["active_ship_id"])
    if not ship:
        raise HTTPException(status_code=422, detail="Aktives Schiff nicht gefunden")
    return ship


def _get_ship(state: dict, ship_id_opt: str | None) -> dict:
    _normalize_state(state)
    ship_id = ship_id_opt or state["active_ship_id"]
    ship = _ship_map(state).get(ship_id)
    if not ship:
        raise HTTPException(status_code=422, detail="Unbekanntes Schiff")
    return ship


def _normalize_state(state: dict) -> None:
    if "ships" in state and "active_ship_id" in state:
        for ship in state["ships"]:
            ship_class = SHIP_CATALOG.get(ship.get("class_id"))
            capacity_total = int(
                ship.get(
                    "capacity_total", ship.get("capacity", GAME_WORLD["start"]["ship_capacity"])
                )
            )
            max_per_good = int(
                ship.get(
                    "max_per_good",
                    ship_class["max_per_good"]
                    if ship_class and "max_per_good" in ship_class
                    else capacity_total,
                )
            )
            ship["capacity_total"] = capacity_total
            ship["max_per_good"] = max_per_good
            ship["capacity"] = capacity_total
            ship.setdefault("cargo", _init_stock_by_goods())
            for good in GAME_WORLD["goods"]:
                ship["cargo"].setdefault(good, 0)
        return
    old_ship = state.get("ship")
    if not isinstance(old_ship, dict):
        raise HTTPException(status_code=422, detail="Ungueltiger Spielstand")
    ship_class = SHIP_CATALOG.get(
        old_ship.get("class_id", "kogge_standard"), SHIP_CATALOG["kogge_standard"]
    )
    capacity_total = int(
        old_ship.get("capacity_total", old_ship.get("capacity", ship_class["capacity_total"]))
    )
    max_per_good = int(old_ship.get("max_per_good", ship_class.get("max_per_good", capacity_total)))
    migrated = {
        "id": "ship-1",
        "name": "Kogge I",
        "class_id": ship_class["id"],
        "buy_price": int(old_ship.get("buy_price", ship_class["buy_price"])),
        "current_city": old_ship.get("current_city"),
        "at_sea": bool(old_ship.get("at_sea", False)),
        "destination": old_ship.get("destination"),
        "eta_days": int(old_ship.get("eta_days", 0)),
        "cargo": old_ship.get("cargo", _init_stock_by_goods()),
        "capacity_total": capacity_total,
        "max_per_good": max_per_good,
        "capacity": capacity_total,
    }
    for good in GAME_WORLD["goods"]:
        migrated["cargo"].setdefault(good, 0)
    state["ships"] = [migrated]
    state["active_ship_id"] = "ship-1"


def _normalize_storage(storage: dict) -> None:
    level = int(storage.get("level", 0))
    capacity_total = int(
        storage.get("capacity_total", storage.get("capacity", _storage_capacity_for_level(level)))
    )
    max_per_good = int(
        storage.get("max_per_good", _storage_max_per_good_for_level(level) or capacity_total)
    )
    storage["level"] = level
    storage["active"] = level > 0
    storage["capacity_total"] = capacity_total
    storage["max_per_good"] = max_per_good
    storage["capacity"] = capacity_total
    storage.setdefault("stock_by_good", _init_stock_by_goods())
    for good in GAME_WORLD["goods"]:
        storage["stock_by_good"].setdefault(good, 0)


def _normalize_private_storages(private_storages: list[dict]) -> None:
    for storage in private_storages:
        _normalize_storage(storage)


def _clamp_stock(stock: int) -> int:
    return max(0, min(MAX_STOCK, int(stock)))


def _city_price_factor(city: str, good: str) -> float:
    matrix = GAME_WORLD["price_matrix"]
    city_row = matrix.get(city, {})
    return float(city_row.get(good, 1.0))


def _stock_factor(stock: int) -> float:
    clamped_stock = _clamp_stock(stock)
    return 1.5 - (clamped_stock / 200.0)


def _zero_days_factor(zero_days: int) -> float:
    return 1.5 + (min(max(0, int(zero_days)), ZERO_DAYS_CAP) * (0.5 / ZERO_DAYS_CAP))


def _spread_for_stock(stock: int) -> float:
    clamped_stock = _clamp_stock(stock)
    spread = MIN_SPREAD + (1.0 - (clamped_stock / 200.0)) * (MAX_SPREAD - MIN_SPREAD)
    return max(MIN_SPREAD, min(MAX_SPREAD, spread))


def _compute_prices(
    *, base_price: int, stock: int, city: str, good: str, zero_days: int
) -> tuple[int, int, int]:
    stock = _clamp_stock(stock)
    factor = Decimal("1.5") - Decimal(stock) / 200
    if stock == 0:
        factor = max(factor, Decimal("1.5") + Decimal(min(zero_days, 30)) / 60)
    city_factor = Decimal(str(_city_price_factor(city, good)))
    midpoint = max(
        1,
        int(
            (Decimal(base_price) * city_factor * factor).quantize(
                Decimal(1), rounding=ROUND_HALF_UP
            )
        ),
    )
    spread = Decimal("0.08") + (1 - Decimal(stock) / 200) * Decimal("0.17")
    bid = max(1, int((midpoint * (1 - spread)).quantize(Decimal(1), ROUND_HALF_UP)))
    ask = max(2, int((midpoint * (1 + spread)).quantize(Decimal(1), ROUND_HALF_UP)))
    return midpoint, min(bid, ask - 1), ask


def refresh_price(market: dict) -> None:
    prices = _compute_prices(
        base_price=market["base_price"],
        stock=market["stock"],
        city=market["city"],
        good=market["good"],
        zero_days=market["zero_days"],
    )
    for key, value in zip(
        ["marktpreis", "stadt_ankaufspreis", "stadt_verkaufspreis"], prices, strict=True
    ):
        market[key] = value


def trade_total(market: dict, side: str, qty: int) -> tuple[int, list[int]]:
    copy = deepcopy(market)
    prices = []
    for _ in range(qty):
        refresh_price(copy)
        prices.append(copy["stadt_verkaufspreis" if side == "buy" else "stadt_ankaufspreis"])
        copy["stock"] += -1 if side == "buy" else 1
        if copy["stock"] > 0:
            copy["zero_days"] = 0
    return sum(prices), prices


def create_initial_state() -> tuple[str, dict, list[dict], list[dict]]:
    session_id = str(uuid.uuid4())
    start = GAME_WORLD["start"]
    defaults = GAME_WORLD["market_defaults"]

    start_class = SHIP_CATALOG[start["ship_class_id"]]
    ships = [
        {
            "id": "ship-1",
            "name": "Kogge I",
            "class_id": start_class["id"],
            "buy_price": int(start_class["buy_price"]),
            "current_city": start["ship_city"],
            "at_sea": False,
            "destination": None,
            "eta_days": 0,
            "cargo": _init_stock_by_goods(),
            "capacity_total": int(start_class["capacity_total"]),
            "max_per_good": int(start_class["max_per_good"]),
            "capacity": int(start_class["capacity_total"]),
        }
    ]

    private_storages = []
    for city in GAME_WORLD["cities"]:
        level = (
            int(start["private_storage_start_level_home"])
            if city == GAME_WORLD["home_city"]
            else int(start["private_storage_start_level_other"])
        )
        private_storages.append(
            {
                "city": city,
                "level": level,
                "active": level > 0,
                "capacity_total": _storage_capacity_for_level(level),
                "max_per_good": _storage_max_per_good_for_level(level),
                "capacity": _storage_capacity_for_level(level),
                "stock_by_good": _init_stock_by_goods(),
            }
        )

    markets: list[dict] = []
    for city in GAME_WORLD["cities"]:
        primary_good = GAME_WORLD["city_goods"][city]
        for good in GAME_WORLD["goods"]:
            is_primary = good == primary_good
            stock = int(defaults["primary_stock"] if is_primary else defaults["secondary_stock"])
            production_rate = int(
                defaults["primary_production"] if is_primary else defaults["secondary_production"]
            )
            consumption_rate = int(defaults["consumption"])
            target_stock = int(
                defaults["target_primary"] if is_primary else defaults["target_secondary"]
            )
            base_price = int(GAME_WORLD["base_price_by_good"][good])
            marktpreis, stadt_ankaufspreis, stadt_verkaufspreis = _compute_prices(
                base_price=base_price,
                stock=stock,
                city=city,
                good=good,
                zero_days=0,
            )
            markets.append(
                {
                    "city": city,
                    "good": good,
                    "stock": stock,
                    "marktpreis": marktpreis,
                    "stadt_ankaufspreis": stadt_ankaufspreis,
                    "stadt_verkaufspreis": stadt_verkaufspreis,
                    "production_rate": production_rate,
                    "consumption_rate": consumption_rate,
                    "target_stock": target_stock,
                    "base_price": base_price,
                    "zero_days": 0,
                }
            )

    state = {
        "session_id": session_id,
        "status": "active",
        "current_day": 0,
        "cash": int(start["cash"]),
        "avatar_id": DEFAULT_AVATAR_ID,
        "ships": ships,
        "active_ship_id": "ship-1",
        "revision": str(uuid.uuid4()),
        "format_version": 1,
        "world_version": "alpha-world-1",
        "rules_version": 1,
        "orders": [],
        "reports": [],
        "intel": {},
        "events": [],
        "month": {
            "opening_cash": int(start["cash"]),
            "trade_income": 0,
            "trade_expenses": 0,
            "construction_expenses": 0,
            "asset_income": 0,
        },
    }
    return session_id, state, markets, private_storages


def avatar_url(avatar_id: str) -> str:
    avatar = AVATAR_BY_ID.get(avatar_id)
    if not avatar:
        avatar = AVATAR_BY_ID[DEFAULT_AVATAR_ID]
    return f"/avatars/{avatar['filename']}"


def avatars_catalog() -> dict:
    return {
        "items": [
            {
                "id": item["id"],
                "label": item["label"],
                "url": f"/avatars/{item['filename']}",
            }
            for item in AVATAR_ITEMS
        ]
    }


def _pending_hint(state: dict) -> str:
    _normalize_state(state)
    at_sea = [ship for ship in state["ships"] if ship["at_sea"]]
    if not at_sea:
        return "Schiff im Hafen"
    next_ship = min(at_sea, key=lambda item: int(item["eta_days"]))
    return f"Naechste Ankunft in {next_ship['eta_days']} Tagen ({next_ship['destination']}, {next_ship['name']})"


def materialize_state(
    state: dict, markets: list[dict], private_storages: list[dict], include_markets: bool = False
) -> dict:
    _normalize_state(state)
    _normalize_private_storages(private_storages)
    ships = sorted(state["ships"], key=lambda item: item["id"])
    active = _active_ship(state)
    data = {
        **state,
        "ship": active,
        "date": game_date(state).isoformat(),
        "routes": GAME_WORLD["routes"],
        "ships": ships,
        "cities": list(GAME_WORLD["cities"]),
        "city_primary_goods": dict(GAME_WORLD["city_goods"]),
        "travel_mode": str(GAME_WORLD.get("travel_seasonality", {}).get("mode", "normal")),
        "player_profile": {
            "avatar_id": state.get("avatar_id", DEFAULT_AVATAR_ID),
            "avatar_url": avatar_url(state.get("avatar_id", DEFAULT_AVATAR_ID)),
        },
        "private_storages": sorted(private_storages, key=lambda item: item["city"]),
        "pending_event_hint": _pending_hint(state),
    }
    if include_markets:
        data["markets"] = sorted(markets, key=lambda item: (item["city"], item["good"]))
    return data


def _ships_in_city(state: dict, city: str) -> list[dict]:
    _normalize_state(state)
    return [
        ship for ship in state["ships"] if not ship["at_sea"] and ship.get("current_city") == city
    ]


def _has_active_storage(private_storages: list[dict], city: str) -> bool:
    storage = _storage_map(private_storages).get(city)
    if not storage:
        return False
    return int(storage.get("level", 0)) > 0


def _visibility_level(state: dict, private_storages: list[dict], city: str) -> str:
    has_ship = len(_ships_in_city(state, city)) > 0
    has_kontor = _has_active_storage(private_storages, city)
    if has_ship and has_kontor:
        return "live_both"
    if has_ship:
        return "live_ship"
    if has_kontor:
        return "live_kontor"
    return "none"


def _capture_city_snapshot(state: dict, markets: list[dict], city: str) -> dict:
    city_markets = sorted(
        [item for item in markets if item["city"] == city],
        key=lambda item: item["good"],
    )
    market_snapshot = [
        {
            "city": item["city"],
            "good": item["good"],
            "stock": int(item["stock"]),
            "marktpreis": int(item["marktpreis"]),
            "stadt_ankaufspreis": int(item["stadt_ankaufspreis"]),
            "stadt_verkaufspreis": int(item["stadt_verkaufspreis"]),
            "production_rate": int(item["production_rate"]),
            "consumption_rate": int(item["consumption_rate"]),
            "zero_days": int(item.get("zero_days", 0)),
        }
        for item in city_markets
    ]
    ships = [
        {"id": ship["id"], "name": ship.get("name", ship["id"])}
        for ship in _ships_in_city(state, city)
    ]
    return {
        "captured_day": int(state["current_day"]),
        "markets": market_snapshot,
        "ships_in_harbor": ships,
    }


def build_city_view(
    *,
    state: dict,
    markets: list[dict],
    private_storages: list[dict],
    city: str,
    intel: dict | None,
) -> tuple[dict, dict | None, int | None]:
    if city not in GAME_WORLD["cities"]:
        raise HTTPException(status_code=404, detail="Unbekannte Stadt")

    level = _visibility_level(state, private_storages, city)
    primary_good = GAME_WORLD["city_goods"][city]
    has_live = level in {"live_ship", "live_kontor", "live_both"}

    if has_live:
        snapshot = _capture_city_snapshot(state, markets, city)
        if level == "live_ship":
            status = "Live-Daten durch eigenes Schiff."
            hint = "Eure Kogge meldet den aktuellen Markt."
        elif level == "live_kontor":
            status = "Live-Daten durch Kontor."
            hint = "Euer Kontor meldet die aktuelle Marktlage."
        else:
            status = "Live-Daten durch Schiff und Kontor."
            hint = "Schiff und Kontor berichten aus erster Hand."
        return (
            {
                "city": city,
                "primary_good": primary_good,
                "visibility_level": level,
                "has_live_visibility": True,
                "last_seen_day": int(state["current_day"]),
                "days_stale": 0,
                "status_hint": status,
                "markets": snapshot["markets"],
                "ships_in_harbor": snapshot["ships_in_harbor"],
                "latest_city_event_hint": hint,
            },
            snapshot,
            int(state["current_day"]),
        )

    if intel:
        last_seen_day = int(intel["last_seen_day"])
        days_stale = max(0, int(state["current_day"]) - last_seen_day)
        return (
            {
                "city": city,
                "primary_good": primary_good,
                "visibility_level": "stale",
                "has_live_visibility": False,
                "last_seen_day": last_seen_day,
                "days_stale": days_stale,
                "status_hint": f"Marktdaten veraltet. Letzte Sichtung vor {days_stale} Tagen.",
                "markets": intel["snapshot"].get("markets", []),
                "ships_in_harbor": None,
                "latest_city_event_hint": None,
            },
            None,
            None,
        )

    return (
        {
            "city": city,
            "primary_good": primary_good,
            "visibility_level": "none",
            "has_live_visibility": False,
            "last_seen_day": None,
            "days_stale": None,
            "status_hint": "Keine aktuelle Praesenz in dieser Stadt.",
            "markets": None,
            "ships_in_harbor": None,
            "latest_city_event_hint": None,
        },
        None,
        None,
    )


def apply_market_trade(
    *, state: dict, markets: list[dict], private_storages: list[dict], action: dict
) -> tuple[dict, list[dict], list[dict], dict]:
    _normalize_private_storages(private_storages)
    ship_trade = action["counterparty"] == "ship"
    ship = _get_ship(state, action.get("ship_id")) if ship_trade else None
    if ship_trade:
        if ship["at_sea"]:
            raise HTTPException(status_code=422, detail="Schiffhandel nur im Hafen moeglich")
        if ship["current_city"] != action["city"]:
            raise HTTPException(
                status_code=422, detail="Schiffhandel nur in aktueller Schiffsstadt moeglich"
            )

    qty = int(action["qty"])
    if qty <= 0 or action["good"] not in GAME_WORLD["goods"]:
        raise HTTPException(status_code=422, detail="Ungültige Ware oder Menge")
    market = _market_map(markets).get((action["city"], action["good"]))
    if not market:
        raise HTTPException(status_code=422, detail="Ware in dieser Stadt nicht vorhanden")

    storage = _storage_map(private_storages).get(action["city"])
    if not storage:
        raise HTTPException(status_code=422, detail="Kontor der Stadt nicht gefunden")
    if action["counterparty"] == "private_storage" and int(storage.get("level", 0)) <= 0:
        raise HTTPException(status_code=422, detail="Kein aktives Kontor in dieser Stadt")

    if ship is not None:
        ship["cargo"].setdefault(action["good"], 0)
    storage["stock_by_good"].setdefault(action["good"], 0)
    stock_before = int(market["stock"])

    if action["type"] == "buy":
        if market["stock"] < qty:
            raise HTTPException(status_code=422, detail="Nicht genug Stadtbestand")
        total_cost, unit_prices = trade_total(market, "buy", qty)
        if state["cash"] < total_cost:
            raise HTTPException(status_code=422, detail="Nicht genug Mark")

        if ship_trade:
            _validate_add_to_ship(ship, action["good"], qty)
            ship["cargo"][action["good"]] += qty
        else:
            _validate_add_to_storage(storage, action["good"], qty)
            storage["stock_by_good"][action["good"]] += qty

        market["stock"] = _clamp_stock(int(market["stock"]) - qty)
        state["cash"] = round(state["cash"] - total_cost, 2)

    else:
        if market["stock"] + qty > MAX_STOCK:
            raise HTTPException(status_code=422, detail="Der Stadtmarkt hat nicht genug Platz")
        total_income, unit_prices = trade_total(market, "sell", qty)
        if ship_trade:
            if ship["cargo"].get(action["good"], 0) < qty:
                raise HTTPException(status_code=422, detail="Nicht genug Ware im Schiff")
            ship["cargo"][action["good"]] -= qty
        else:
            if storage["stock_by_good"].get(action["good"], 0) < qty:
                raise HTTPException(status_code=422, detail="Nicht genug Ware im Kontor")
            storage["stock_by_good"][action["good"]] -= qty

        market["stock"] = _clamp_stock(int(market["stock"]) + qty)
        state["cash"] = round(state["cash"] + total_income, 2)

    stock_after = _clamp_stock(int(market["stock"]))
    market["stock"] = stock_after
    market["zero_days"] = int(market.get("zero_days", 0))
    if stock_after == 0:
        market["zero_days"] = min(ZERO_DAYS_CAP, market["zero_days"])
    else:
        market["zero_days"] = 0
    marktpreis, stadt_ankaufspreis, stadt_verkaufspreis = _compute_prices(
        base_price=int(market["base_price"]),
        stock=stock_after,
        city=market["city"],
        good=market["good"],
        zero_days=int(market.get("zero_days", 0)),
    )
    market["marktpreis"] = marktpreis
    market["stadt_ankaufspreis"] = stadt_ankaufspreis
    market["stadt_verkaufspreis"] = stadt_verkaufspreis

    payload = {
        "type": action["type"],
        "city": action["city"],
        "good": action["good"],
        "qty": qty,
        "counterparty": action["counterparty"],
        "stock_before": stock_before,
        "stock_after": stock_after,
        "mode": "ship" if ship_trade else "kontor",
        "total": sum(unit_prices),
        "unit_prices": unit_prices,
    }
    if ship_trade:
        payload["ship_id"] = ship["id"]
    state["month"]["trade_expenses" if action["type"] == "buy" else "trade_income"] += sum(
        unit_prices
    )
    event = {"event_type": "market_trade_executed", "payload": payload}
    return state, markets, private_storages, event


def apply_transfer(
    *, state: dict, private_storages: list[dict], action: dict
) -> tuple[dict, list[dict], dict]:
    _normalize_private_storages(private_storages)
    ship = _get_ship(state, action.get("ship_id"))
    if ship["at_sea"]:
        raise HTTPException(status_code=422, detail="Transfer nur im Hafen moeglich")
    if ship["current_city"] != action["city"]:
        raise HTTPException(
            status_code=422, detail="Transfer nur in aktueller Schiffsstadt moeglich"
        )

    storage = _storage_map(private_storages).get(action["city"])
    if not storage:
        raise HTTPException(status_code=422, detail="Kontor der Stadt nicht gefunden")
    if int(storage.get("level", 0)) <= 0:
        raise HTTPException(status_code=422, detail="Kein aktives Kontor in dieser Stadt")

    qty = int(action["qty"])
    if qty <= 0 or action["good"] not in GAME_WORLD["goods"]:
        raise HTTPException(status_code=422, detail="Ungültige Ware oder Menge")
    good = action["good"]
    ship["cargo"].setdefault(good, 0)
    storage["stock_by_good"].setdefault(good, 0)

    if action["direction"] == "ship_to_private":
        if ship["cargo"][good] < qty:
            raise HTTPException(status_code=422, detail="Nicht genug Ware im Schiff")
        _validate_add_to_storage(storage, good, qty)
        ship["cargo"][good] -= qty
        storage["stock_by_good"][good] += qty
    else:
        if storage["stock_by_good"][good] < qty:
            raise HTTPException(status_code=422, detail="Nicht genug Ware im Kontor")
        _validate_add_to_ship(ship, good, qty)
        storage["stock_by_good"][good] -= qty
        ship["cargo"][good] += qty

    event = {
        "event_type": "transfer_executed",
        "payload": {
            "city": action["city"],
            "good": good,
            "qty": qty,
            "direction": action["direction"],
            "ship_id": ship["id"],
        },
    }
    return state, private_storages, event


def set_course(
    *,
    state: dict,
    destination_city: str,
    routes: dict[tuple[str, str], int],
    ship_id: str | None = None,
) -> tuple[dict, dict]:
    ship = _get_ship(state, ship_id)
    if ship["at_sea"]:
        raise HTTPException(status_code=422, detail="Schiff ist bereits auf See")

    origin = ship["current_city"]
    if destination_city == origin:
        raise HTTPException(status_code=422, detail="Zielstadt darf nicht identisch sein")

    route = (origin, destination_city)
    if route not in routes:
        raise HTTPException(status_code=422, detail="Route nicht verfuegbar")

    ship["at_sea"] = True
    ship["destination"] = destination_city
    resolved_days = _resolve_travel_days(int(routes[route]), state)
    ship["eta_days"] = resolved_days
    ship["current_city"] = None

    return state, {
        "event_type": "course_set",
        "payload": {
            "from": origin,
            "to": destination_city,
            "eta_days": resolved_days,
            "ship_id": ship["id"],
        },
    }


def _advance_markets(markets: list[dict], day: int) -> list[dict]:
    next_markets: list[dict] = []
    for item in markets:
        delta = item["production_rate"] - item["consumption_rate"]
        stock = _clamp_stock(int(item["stock"]) + delta)
        zero_days = int(item.get("zero_days", 0))
        if stock == 0:
            zero_days = min(ZERO_DAYS_CAP, zero_days + 1)
        else:
            zero_days = 0
        marktpreis, stadt_ankaufspreis, stadt_verkaufspreis = _compute_prices(
            base_price=int(item["base_price"]),
            stock=stock,
            city=item["city"],
            good=item["good"],
            zero_days=zero_days,
        )
        next_markets.append(
            {
                **item,
                "stock": stock,
                "zero_days": zero_days,
                "marktpreis": marktpreis,
                "stadt_ankaufspreis": stadt_ankaufspreis,
                "stadt_verkaufspreis": stadt_verkaufspreis,
            }
        )
    return next_markets


def game_date(state: dict) -> date:
    return date(1400, 3, 1) + timedelta(days=state["current_day"])


def refresh_intel(state: dict, markets: list[dict], private_storages: list[dict]) -> None:
    for city in GAME_WORLD["cities"]:
        if _visibility_level(state, private_storages, city) != "none":
            state["intel"][city] = {
                "snapshot": _capture_city_snapshot(state, markets, city),
                "last_seen_day": state["current_day"],
            }


def record_events(state: dict, events: list[dict]) -> None:
    for event in events:
        state["events"].append(
            {
                "id": len(state["events"]) + 1,
                "day": state["current_day"],
                "created_at": game_date(state).isoformat() + "T00:00:00",
                **event,
            }
        )


def advance_day(
    *, state: dict, markets: list[dict], private_storages: list[dict] | None = None
) -> tuple[dict, list[dict], list[dict]]:
    private_storages = private_storages if private_storages is not None else []
    current = game_date(state)
    tomorrow = current + timedelta(days=1)
    events = []
    if tomorrow.month != current.month:
        report = {
            "month": current.strftime("%Y-%m"),
            **state["month"],
            "closing_cash": state["cash"],
            "cash_surplus": state["cash"] - state["month"]["opening_cash"],
        }
        state["reports"].append(report)
        events.append({"event_type": "month_closed", "payload": report})
        record_events(state, events)
        state["month"] = {key: 0 for key in state["month"]}
        state["month"]["opening_cash"] = state["cash"]
    state["current_day"] += 1
    markets = _advance_markets(markets, state["current_day"])
    today_events = []
    for order in sorted(state["orders"], key=lambda o: (o["due_day"], o["id"])):
        if order["due_day"] > state["current_day"]:
            continue
        if order["kind"] == "ship":
            item = SHIP_CATALOG[order["class_id"]]
            number = _next_ship_number(state)
            state["ships"].append(
                {
                    "id": f"ship-{number}",
                    "name": f"Kogge {number}",
                    "class_id": item["id"],
                    "buy_price": item["buy_price"],
                    "current_city": order["city"],
                    "at_sea": False,
                    "destination": None,
                    "eta_days": 0,
                    "cargo": _init_stock_by_goods(),
                    "capacity_total": item["capacity_total"],
                    "capacity": item["capacity_total"],
                    "max_per_good": item["max_per_good"],
                }
            )
        else:
            storage = _storage_map(private_storages)[order["city"]]
            level = order["level"]
            storage.update(
                level=level,
                active=True,
                capacity_total=_storage_capacity_for_level(level),
                capacity=_storage_capacity_for_level(level),
                max_per_good=_storage_max_per_good_for_level(level),
            )
        today_events.append({"event_type": "construction_completed", "payload": dict(order)})
    state["orders"] = [o for o in state["orders"] if o["due_day"] > state["current_day"]]
    for ship in state["ships"]:
        if ship["at_sea"]:
            ship["eta_days"] -= 1
            if ship["eta_days"] == 0:
                ship.update(at_sea=False, current_city=ship["destination"], destination=None)
                today_events.append(
                    {
                        "event_type": "ship_arrival",
                        "payload": {"city": ship["current_city"], "ship_id": ship["id"]},
                    }
                )
    refresh_intel(state, markets, private_storages)
    record_events(state, today_events)
    return state, markets, events + today_events


def advance_to_next_event(
    *, state: dict, markets: list[dict], private_storages: list[dict] | None = None
) -> tuple[dict, list[dict], list[dict]]:
    events = []
    for _ in range(31):
        state, markets, day_events = advance_day(
            state=state, markets=markets, private_storages=private_storages
        )
        events.extend(day_events)
        if day_events:
            break
    return state, markets, events


def assets_catalog() -> dict:
    return {
        "ships": [
            {
                "id": item["id"],
                "name": item["name"],
                "capacity_total": int(item["capacity_total"]),
                "max_per_good": int(item["max_per_good"]),
                "capacity": int(item["capacity_total"]),
                "buy_price": int(item["buy_price"]),
                "sell_price": _catalog_sell_price(int(item["buy_price"])),
                "build_days": item["build_days"],
            }
            for item in GAME_WORLD["ship_catalog"]
        ],
        "storages": [
            {
                "level": int(item["level"]),
                "capacity_total": int(item["capacity_total"]),
                "max_per_good": int(item["max_per_good"]),
                "capacity": int(item["capacity_total"]),
                "buy_price": int(item["buy_price"]),
                "sell_price": _catalog_sell_price(int(item["buy_price"])),
                "build_days": item["build_days"],
            }
            for item in GAME_WORLD["storage_levels"]
        ],
    }


def _next_ship_number(state: dict) -> int:
    ids = []
    for ship in state["ships"]:
        parts = str(ship["id"]).split("-")
        if len(parts) == 2 and parts[0] == "ship" and parts[1].isdigit():
            ids.append(int(parts[1]))
    return (max(ids) if ids else 0) + 1


def buy_ship(
    *, state: dict, markets: list[dict], action: dict
) -> tuple[dict, list[dict], list[dict]]:
    ship_class = SHIP_CATALOG.get(action["ship_class_id"])
    if not ship_class:
        raise HTTPException(status_code=422, detail="Unbekannte Schiffsklasse")
    if action["city"] not in GAME_WORLD["cities"]:
        raise HTTPException(status_code=422, detail="Unbekannte Stadt")
    price = int(ship_class["buy_price"])
    if int(state["cash"]) < price:
        raise HTTPException(status_code=422, detail="Nicht genug Mark")

    order = {
        "id": len(state["events"]) + 1,
        "kind": "ship",
        "city": action["city"],
        "class_id": ship_class["id"],
        "due_day": state["current_day"] + ship_class["build_days"],
        "price": price,
    }
    state["orders"].append(order)
    state["cash"] -= price
    state["month"]["construction_expenses"] += price
    return state, markets, [{"event_type": "construction_ordered", "payload": dict(order)}]


def sell_ship(*, state: dict, action: dict) -> tuple[dict, list[dict]]:
    _normalize_state(state)
    ships = _ship_map(state)
    ship = ships.get(action["ship_id"])
    if not ship:
        raise HTTPException(status_code=422, detail="Unbekanntes Schiff")
    if len(state["ships"]) <= 1:
        raise HTTPException(status_code=422, detail="Mindestens ein Schiff muss verbleiben")
    if ship["at_sea"]:
        raise HTTPException(status_code=422, detail="Schiff auf See kann nicht verkauft werden")
    if ship["current_city"] != action["city"]:
        raise HTTPException(status_code=422, detail="Schiff ist nicht in dieser Stadt")
    if _ship_total(ship) > 0:
        raise HTTPException(status_code=422, detail="Schiff mit Ladung kann nicht verkauft werden")

    buy_price = int(
        ship.get("buy_price") or SHIP_CATALOG.get(ship.get("class_id"), {}).get("buy_price", 0.0)
    )
    payout = _catalog_sell_price(buy_price)
    state["cash"] += payout
    state["month"]["asset_income"] += payout
    state["ships"] = [item for item in state["ships"] if item["id"] != ship["id"]]
    if state["active_ship_id"] == ship["id"]:
        state["active_ship_id"] = state["ships"][0]["id"]
    event = {
        "event_type": "ship_sold",
        "payload": {
            "city": action["city"],
            "ship_id": ship["id"],
            "ship_name": ship["name"],
            "price": payout,
        },
    }
    return state, [event]


def upgrade_storage(
    *, state: dict, markets: list[dict], private_storages: list[dict], action: dict
) -> tuple[dict, list[dict], list[dict], list[dict]]:
    _normalize_private_storages(private_storages)
    storage = _storage_map(private_storages).get(action["city"])
    if not storage:
        raise HTTPException(status_code=422, detail="Kontor der Stadt nicht gefunden")
    current_level = int(storage.get("level", 0))
    target_level = current_level + 1
    if target_level > STORAGE_MAX_LEVEL:
        raise HTTPException(status_code=422, detail="Kontor ist bereits maximal ausgebaut")
    price = _storage_price_for_level(target_level)
    if int(state["cash"]) < price:
        raise HTTPException(status_code=422, detail="Nicht genug Mark")

    if any(o["kind"] == "storage" and o["city"] == action["city"] for o in state["orders"]):
        raise HTTPException(status_code=422, detail="In dieser Stadt läuft bereits ein Kontorbau")
    order = {
        "id": len(state["events"]) + 1,
        "kind": "storage",
        "city": action["city"],
        "level": target_level,
        "due_day": state["current_day"] + 7,
        "price": price,
    }
    state["orders"].append(order)
    state["cash"] -= price
    state["month"]["construction_expenses"] += price
    return (
        state,
        markets,
        private_storages,
        [{"event_type": "construction_ordered", "payload": dict(order)}],
    )


def sell_storage(
    *, state: dict, private_storages: list[dict], action: dict
) -> tuple[dict, list[dict], list[dict]]:
    _normalize_private_storages(private_storages)
    storage = _storage_map(private_storages).get(action["city"])
    if not storage:
        raise HTTPException(status_code=422, detail="Kontor der Stadt nicht gefunden")
    current_level = int(storage.get("level", 0))
    if current_level <= 0:
        raise HTTPException(status_code=422, detail="Kein aktives Kontor in dieser Stadt")
    if any(o["kind"] == "storage" and o["city"] == action["city"] for o in state["orders"]):
        raise HTTPException(status_code=422, detail="Kontor wird gerade ausgebaut")
    next_level = current_level - 1
    next_capacity = _storage_capacity_for_level(next_level)
    next_max_per_good = _storage_max_per_good_for_level(next_level)
    if _storage_total(storage) > next_capacity:
        raise HTTPException(status_code=422, detail="Kontorbestand zu hoch fuer Rueckbau")
    for good, qty in storage["stock_by_good"].items():
        if int(qty) > next_max_per_good:
            raise HTTPException(
                status_code=422, detail="Kontorbestand pro Ware zu hoch fuer Rueckbau"
            )

    payout = _catalog_sell_price(_storage_price_for_level(current_level))
    storage["level"] = next_level
    storage["active"] = next_level > 0
    storage["capacity_total"] = next_capacity
    storage["max_per_good"] = next_max_per_good
    storage["capacity"] = next_capacity
    state["cash"] += payout
    state["month"]["asset_income"] += payout
    event = {
        "event_type": "storage_sold",
        "payload": {
            "city": action["city"],
            "level": next_level,
            "capacity_total": next_capacity,
            "max_per_good": next_max_per_good,
            "capacity": next_capacity,
            "price": payout,
        },
    }
    return state, private_storages, [event]
