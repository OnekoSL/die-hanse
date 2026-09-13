from fastapi.testclient import TestClient

from app.main import create_app
from app.infra.db import SessionLocal
from app.infra.repositories import ScenarioRepository


def test_run_response_schema():
    app = create_app()
    with TestClient(app) as client:
        scenarios = client.get("/api/v1/scenarios")
        assert scenarios.status_code == 200
        first = scenarios.json()[0]["id"]

        payload = {
            "scenario_id": first,
            "start_day": 1,
            "end_day": 30,
            "initial_cash": 5000,
            "strategy": {"type": "rule_based_v1", "params": {}},
            "risk_limits": {"max_position_per_good": 20, "min_cash_buffer": 100},
        }
        res = client.post("/api/v1/backtests/run", json=payload)
        assert res.status_code == 200
        body = res.json()
        assert "run_id" in body
        assert "summary" in body
        assert "equity_curve" in body


def test_run_unknown_scenario():
    app = create_app()
    with TestClient(app) as client:
        payload = {
            "scenario_id": "unknown",
            "start_day": 1,
            "end_day": 30,
            "initial_cash": 5000,
            "strategy": {"type": "rule_based_v1", "params": {}},
            "risk_limits": {"max_position_per_good": 20, "min_cash_buffer": 100},
        }
        res = client.post("/api/v1/backtests/run", json=payload)
        assert res.status_code == 404


def test_invalid_range():
    app = create_app()
    with TestClient(app) as client:
        scenarios = client.get("/api/v1/scenarios")
        first = scenarios.json()[0]["id"]
        payload = {
            "scenario_id": first,
            "start_day": 10,
            "end_day": 9,
            "initial_cash": 5000,
            "strategy": {"type": "rule_based_v1", "params": {}},
            "risk_limits": {"max_position_per_good": 20, "min_cash_buffer": 100},
        }
        res = client.post("/api/v1/backtests/run", json=payload)
        assert res.status_code == 422


def test_run_with_legacy_scenario_without_production_field():
    app = create_app()
    with SessionLocal() as session:
        ScenarioRepository(session).upsert(
            scenario_id="legacy_no_production",
            name="Legacy ohne Produktion",
            version="0.9.0",
            payload={
                "id": "legacy_no_production",
                "name": "Legacy ohne Produktion",
                "version": "0.9.0",
                "max_day": 120,
                "goods": ["Getreide", "Holz"],
                "ship": {"start_city": "Luebeck", "capacity": 20},
                "cities": [
                    {
                        "name": "Luebeck",
                        "goods": {
                            "Getreide": {
                                "initial_stock": 100,
                                "target_stock": 100,
                                "base_price": 10,
                                "demand_per_day": 3,
                            },
                            "Holz": {
                                "initial_stock": 80,
                                "target_stock": 80,
                                "base_price": 12,
                                "demand_per_day": 2,
                            },
                        },
                    },
                    {
                        "name": "London",
                        "goods": {
                            "Getreide": {
                                "initial_stock": 90,
                                "target_stock": 100,
                                "base_price": 11,
                                "demand_per_day": 3,
                            },
                            "Holz": {
                                "initial_stock": 70,
                                "target_stock": 80,
                                "base_price": 13,
                                "demand_per_day": 2,
                            },
                        },
                    },
                ],
                "routes": [
                    {"from": "Luebeck", "to": "London", "days": 2},
                    {"from": "London", "to": "Luebeck", "days": 2},
                ],
            },
        )
        session.commit()

    with TestClient(app) as client:
        payload = {
            "scenario_id": "legacy_no_production",
            "start_day": 1,
            "end_day": 30,
            "initial_cash": 5000,
            "strategy": {"type": "rule_based_v1", "params": {}},
            "risk_limits": {"max_position_per_good": 20, "min_cash_buffer": 100},
        }
        res = client.post("/api/v1/backtests/run", json=payload)
        assert res.status_code == 200
        body = res.json()
        assert body["run_id"]
        assert len(body["equity_curve"]) == 30
