from app.domain.schemas import BacktestRunRequest
from app.engine.simulation import run_backtest


def test_ship_arrives_and_sells_after_route_days(scenario_payload):
    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=5,
        initial_cash=10_000,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 30, "min_cash_buffer": 50},
    )
    result = run_backtest(scenario_payload, req)
    sells = [e for e in result.trade_log if e["side"] == "sell"]
    assert len(sells) >= 1


def test_rejects_when_cash_buffer_too_high(scenario_payload):
    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=2,
        initial_cash=100,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 30, "min_cash_buffer": 99},
    )
    result = run_backtest(scenario_payload, req)
    assert any("Cash Buffer" in v for v in result.violations) or len(result.trade_log) == 0


def test_deterministic_for_same_input(scenario_payload_clone):
    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=20,
        initial_cash=5_000,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 20, "min_cash_buffer": 50},
    )
    r1 = run_backtest(scenario_payload_clone, req)
    r2 = run_backtest(scenario_payload_clone, req)
    assert r1.summary == r2.summary
    assert r1.equity_curve == r2.equity_curve
    assert r1.trade_log == r2.trade_log


def test_fallback_production_uses_demand_when_missing(scenario_payload_clone):
    payload = scenario_payload_clone
    for city in payload["cities"]:
        for good_cfg in city["goods"].values():
            if "production_per_day" in good_cfg:
                del good_cfg["production_per_day"]

    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=30,
        initial_cash=5_000,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 20, "min_cash_buffer": 50},
    )
    result = run_backtest(payload, req)
    assert result.status == "completed"
    assert len(result.equity_curve) == 30


def test_negative_production_is_clamped_and_recorded(scenario_payload_clone):
    payload = scenario_payload_clone
    payload["cities"][0]["goods"]["Getreide"]["production_per_day"] = -5

    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=5,
        initial_cash=5_000,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 20, "min_cash_buffer": 50},
    )
    result = run_backtest(payload, req)
    assert any("production_per_day < 0" in item for item in result.violations)
    assert all(point["equity"] >= 0 for point in result.equity_curve)


def test_ship_max_per_good_limits_order_size(scenario_payload_clone):
    payload = scenario_payload_clone
    payload["ship"]["capacity_total"] = 30
    payload["ship"]["max_per_good"] = 12
    payload["ship"]["capacity"] = 30

    req = BacktestRunRequest(
        scenario_id="hanse_seed_v1",
        start_day=1,
        end_day=2,
        initial_cash=5_000,
        strategy={"type": "rule_based_v1", "params": {}},
        risk_limits={"max_position_per_good": 30, "min_cash_buffer": 50},
    )
    result = run_backtest(payload, req)
    buys = [event for event in result.trade_log if event["side"] == "buy"]
    assert buys
    assert max(event["qty"] for event in buys) <= 12
