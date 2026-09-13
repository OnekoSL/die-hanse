import os

if not os.environ.get("HANSE_DB_PATH"):
    raise RuntimeError("Tests benötigen eine eigene temporäre HANSE_DB_PATH-Datenbank.")

import copy

import pytest


@pytest.fixture
def scenario_payload():
    return {
        "id": "hanse_seed_v1",
        "name": "Hanse Kernszenario",
        "version": "1.0.0",
        "max_day": 365,
        "goods": ["Getreide", "Holz", "Tuch"],
        "ship": {"start_city": "Luebeck", "capacity_total": 30, "max_per_good": 30, "capacity": 30},
        "cities": [
            {
                "name": "Luebeck",
                "goods": {
                    "Getreide": {
                        "initial_stock": 120,
                        "target_stock": 100,
                        "base_price": 10,
                        "demand_per_day": 4,
                        "production_per_day": 4,
                    },
                    "Holz": {
                        "initial_stock": 70,
                        "target_stock": 100,
                        "base_price": 14,
                        "demand_per_day": 3,
                        "production_per_day": 3,
                    },
                    "Tuch": {
                        "initial_stock": 40,
                        "target_stock": 80,
                        "base_price": 20,
                        "demand_per_day": 2,
                        "production_per_day": 2,
                    },
                },
            },
            {
                "name": "London",
                "goods": {
                    "Getreide": {
                        "initial_stock": 40,
                        "target_stock": 120,
                        "base_price": 11,
                        "demand_per_day": 5,
                        "production_per_day": 5,
                    },
                    "Holz": {
                        "initial_stock": 140,
                        "target_stock": 100,
                        "base_price": 12,
                        "demand_per_day": 2,
                        "production_per_day": 2,
                    },
                    "Tuch": {
                        "initial_stock": 60,
                        "target_stock": 80,
                        "base_price": 19,
                        "demand_per_day": 3,
                        "production_per_day": 3,
                    },
                },
            },
        ],
        "routes": [
            {"from": "Luebeck", "to": "London", "days": 2},
            {"from": "London", "to": "Luebeck", "days": 2},
        ],
    }


@pytest.fixture
def scenario_payload_clone(scenario_payload):
    return copy.deepcopy(scenario_payload)
