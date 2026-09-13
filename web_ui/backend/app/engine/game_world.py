from __future__ import annotations

GAME_WORLD_VERSION = "alpha-world-1"

DEFAULT_AVATAR_ID = "merchant"
AVATAR_ITEMS = [{"id": "merchant", "label": "Kaufmann", "filename": "merchant.svg"}]
AVATAR_BY_ID = {item["id"]: item for item in AVATAR_ITEMS}

GOODS = ["Salz", "Getreide", "Holz", "Tuch", "Pelze", "Fisch"]

PRIMARY_GOOD_BY_CITY = {
    "Luebeck": "Salz",
    "London": "Tuch",
    "Rostock": "Holz",
    "Danzig": "Getreide",
    "Riga": "Pelze",
    "Visby": "Fisch",
}

BASE_PRICE_BY_GOOD = {
    "Salz": 17.0,
    "Getreide": 10.0,
    "Holz": 12.0,
    "Tuch": 19.0,
    "Pelze": 22.0,
    "Fisch": 11.0,
}

PRICE_MATRIX = {
    "Luebeck": {
        "Salz": 0.80,
        "Getreide": 1.00,
        "Holz": 1.00,
        "Tuch": 1.15,
        "Pelze": 1.15,
        "Fisch": 0.90,
    },
    "London": {
        "Salz": 1.30,
        "Getreide": 1.30,
        "Holz": 1.15,
        "Tuch": 0.80,
        "Pelze": 1.30,
        "Fisch": 1.15,
    },
    "Rostock": {
        "Salz": 0.90,
        "Getreide": 1.00,
        "Holz": 0.80,
        "Tuch": 1.15,
        "Pelze": 1.15,
        "Fisch": 1.00,
    },
    "Danzig": {
        "Salz": 1.10,
        "Getreide": 0.80,
        "Holz": 0.90,
        "Tuch": 1.15,
        "Pelze": 1.15,
        "Fisch": 1.00,
    },
    "Riga": {
        "Salz": 1.10,
        "Getreide": 0.90,
        "Holz": 0.90,
        "Tuch": 1.15,
        "Pelze": 0.80,
        "Fisch": 1.00,
    },
    "Visby": {
        "Salz": 1.10,
        "Getreide": 1.15,
        "Holz": 1.00,
        "Tuch": 1.15,
        "Pelze": 1.15,
        "Fisch": 0.80,
    },
}

GAME_WORLD = {
    "home_city": "Luebeck",
    "cities": ["Luebeck", "London", "Rostock", "Danzig", "Riga", "Visby"],
    "goods": GOODS,
    "city_goods": PRIMARY_GOOD_BY_CITY,
    "start": {
        "cash": 1000.0,
        "ship_capacity": 40,
        "ship_class_id": "kogge_standard",
        "ship_city": "Luebeck",
        "private_storage_start_level_home": 1,
        "private_storage_start_level_other": 0,
    },
    "ship_catalog": [
        {
            "id": "kogge_standard",
            "name": "Kogge Standard",
            "capacity_total": 40,
            "max_per_good": 20,
            "buy_price": 900.0,
        },
        {
            "id": "grosse_kogge",
            "name": "Grosse Kogge",
            "capacity_total": 70,
            "max_per_good": 35,
            "buy_price": 1600.0,
        },
        {
            "id": "fernhaendler",
            "name": "Fernhaendler",
            "capacity_total": 100,
            "max_per_good": 50,
            "buy_price": 2600.0,
        },
    ],
    "storage_levels": [
        {"level": 1, "capacity_total": 80, "max_per_good": 30, "buy_price": 200.0},
        {"level": 2, "capacity_total": 140, "max_per_good": 50, "buy_price": 350.0},
        {"level": 3, "capacity_total": 220, "max_per_good": 80, "buy_price": 600.0},
        {"level": 4, "capacity_total": 320, "max_per_good": 120, "buy_price": 950.0},
    ],
    "market_defaults": {
        "primary_stock": 160,
        "secondary_stock": 80,
        "primary_production": 3,
        "secondary_production": 0,
        "consumption": 2,
        "primary_delta_per_day": 3,
        "secondary_delta_per_day": -2,
        "target_primary": 140,
        "target_secondary": 90,
    },
    "base_price_by_good": BASE_PRICE_BY_GOOD,
    "price_matrix": PRICE_MATRIX,
    # Hook fuer spaetere saisonale Reisezeitfaktoren.
    "travel_seasonality": {
        "enabled": False,
        "mode": "normal",
        "profiles": {
            "normal": 1.0,
            "summer": 1.0,
            "winter": 1.0,
            "storm": 1.0,
        },
    },
    "routes": [
        {"from": "Luebeck", "to": "London", "days": 5},
        {"from": "London", "to": "Luebeck", "days": 5},
        {"from": "Luebeck", "to": "Rostock", "days": 2},
        {"from": "Rostock", "to": "Luebeck", "days": 2},
        {"from": "Luebeck", "to": "Danzig", "days": 4},
        {"from": "Danzig", "to": "Luebeck", "days": 4},
        {"from": "Luebeck", "to": "Riga", "days": 6},
        {"from": "Riga", "to": "Luebeck", "days": 6},
        {"from": "Luebeck", "to": "Visby", "days": 4},
        {"from": "Visby", "to": "Luebeck", "days": 4},
        {"from": "London", "to": "Rostock", "days": 5},
        {"from": "Rostock", "to": "London", "days": 5},
        {"from": "London", "to": "Danzig", "days": 6},
        {"from": "Danzig", "to": "London", "days": 6},
        {"from": "London", "to": "Riga", "days": 7},
        {"from": "Riga", "to": "London", "days": 7},
        {"from": "London", "to": "Visby", "days": 6},
        {"from": "Visby", "to": "London", "days": 6},
        {"from": "Rostock", "to": "Danzig", "days": 3},
        {"from": "Danzig", "to": "Rostock", "days": 3},
        {"from": "Rostock", "to": "Riga", "days": 5},
        {"from": "Riga", "to": "Rostock", "days": 5},
        {"from": "Rostock", "to": "Visby", "days": 4},
        {"from": "Visby", "to": "Rostock", "days": 4},
        {"from": "Danzig", "to": "Riga", "days": 4},
        {"from": "Riga", "to": "Danzig", "days": 4},
        {"from": "Danzig", "to": "Visby", "days": 4},
        {"from": "Visby", "to": "Danzig", "days": 4},
        {"from": "Riga", "to": "Visby", "days": 3},
        {"from": "Visby", "to": "Riga", "days": 3},
    ],
}

# Alpha data, intentionally independent of the backtest scenario catalogue.
GOODS.extend(["Malz", "Eisen", "Wachs"])
PRIMARY_GOOD_BY_CITY.update(
    {
        "Riga": "Wachs",
        "Hamburg": "Malz",
        "Stockholm": "Eisen",
        "Bergen": "Fisch",
        "Bruegge": "Tuch",
        "Nowgorod": "Pelze",
    }
)
BASE_PRICE_BY_GOOD.update({"Malz": 8, "Eisen": 15, "Wachs": 20})
GAME_WORLD["cities"] = list(PRIMARY_GOOD_BY_CITY)
PRICE_MATRIX["Riga"]["Pelze"] = 1.0
for city, primary in PRIMARY_GOOD_BY_CITY.items():
    row = PRICE_MATRIX.setdefault(city, {})
    for good in GOODS:
        row.setdefault(good, 1.0)
    row[primary] = 0.8
# All monetary game values are integer hundredths of a Mark.
GAME_WORLD["start"]["cash"] = 100000
for good in BASE_PRICE_BY_GOOD:
    BASE_PRICE_BY_GOOD[good] = int(BASE_PRICE_BY_GOOD[good] * 100)
for item, days in zip(GAME_WORLD["ship_catalog"], [7, 14, 21], strict=True):
    item["buy_price"] = int(item["buy_price"] * 100)
    item["build_days"] = days
for item in GAME_WORLD["storage_levels"]:
    item["buy_price"] = int(item["buy_price"] * 100)
    item["build_days"] = 7
GAME_WORLD["market_defaults"]["primary_production"] = 5

NEW_EDGES = [
    ("Hamburg", "Luebeck", 2),
    ("Hamburg", "London", 4),
    ("Bruegge", "London", 2),
    ("Bruegge", "Hamburg", 3),
    ("Bergen", "Hamburg", 4),
    ("Bergen", "London", 4),
    ("Stockholm", "Visby", 2),
    ("Stockholm", "Riga", 3),
    ("Nowgorod", "Riga", 3),
]
ROUTES = {(r["from"], r["to"]): r["days"] for r in GAME_WORLD["routes"]}
for origin, destination, days in NEW_EDGES:
    ROUTES[origin, destination] = days
    ROUTES[destination, origin] = days
_distances = dict(ROUTES)
for city in GAME_WORLD["cities"]:
    _distances[city, city] = 0
for via in GAME_WORLD["cities"]:
    for origin in GAME_WORLD["cities"]:
        for destination in GAME_WORLD["cities"]:
            _distances[origin, destination] = min(
                _distances.get((origin, destination), 100000),
                _distances.get((origin, via), 100000) + _distances.get((via, destination), 100000),
            )
for pair, days in _distances.items():
    if pair[0] != pair[1]:
        ROUTES.setdefault(pair, days)
GAME_WORLD["routes"] = [
    {"from": a, "to": b, "days": days} for (a, b), days in sorted(ROUTES.items())
]
