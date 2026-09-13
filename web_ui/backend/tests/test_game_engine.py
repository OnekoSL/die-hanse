from fastapi import HTTPException

from app.engine.game_engine import (
    _resolve_travel_days,
    _compute_prices,
    assets_catalog,
    advance_day,
    advance_to_next_event,
    apply_market_trade,
    apply_transfer,
    buy_ship,
    create_initial_state,
    sell_ship,
    sell_storage,
    set_course,
    upgrade_storage,
)
from app.engine.game_world import GAME_WORLD


def test_luebeck_primary_good_is_salz():
    assert GAME_WORLD["city_goods"]["Luebeck"] == "Salz"
    assert GAME_WORLD["city_goods"]["London"] == "Tuch"
    assert GAME_WORLD["city_goods"]["Danzig"] == "Getreide"


def test_market_contains_all_goods_in_all_cities():
    _, _, markets, _ = create_initial_state()
    expected = len(GAME_WORLD["cities"]) * len(GAME_WORLD["goods"])
    assert len(markets) == expected


def test_price_relation_is_valid_for_all_market_rows():
    _, _, markets, _ = create_initial_state()
    for row in markets:
        assert row["stadt_ankaufspreis"] < row["stadt_verkaufspreis"]
        assert row["stadt_ankaufspreis"] > 0


def test_base_price_at_stock_100_for_non_primary_city_good():
    marktpreis, _, _ = _compute_prices(
        base_price=1000,
        stock=100,
        city="Luebeck",
        good="Getreide",
        zero_days=0,
    )
    assert marktpreis == 1000


def test_city_matrix_applies_at_stock_100():
    marktpreis, _, _ = _compute_prices(
        base_price=1700,
        stock=100,
        city="Luebeck",
        good="Salz",
        zero_days=0,
    )
    assert marktpreis == 1360


def test_transfer_respects_capacity():
    _, state, _, private_storages = create_initial_state()
    storage = [item for item in private_storages if item["city"] == "Luebeck"][0]
    storage["stock_by_good"]["Salz"] = storage["capacity"]
    active_ship = [item for item in state["ships"] if item["id"] == state["active_ship_id"]][0]
    active_ship["cargo"]["Salz"] = 1

    try:
        apply_transfer(
            state=state,
            private_storages=private_storages,
            action={"city": "Luebeck", "good": "Salz", "qty": 1, "direction": "ship_to_private"},
        )
        assert False, "Expected capacity validation"
    except HTTPException as exc:
        assert exc.status_code == 422


def test_ship_buy_rejects_when_total_capacity_reached():
    _, state, markets, private_storages = create_initial_state()
    active_ship = [item for item in state["ships"] if item["id"] == state["active_ship_id"]][0]
    active_ship["cargo"]["Salz"] = 20
    active_ship["cargo"]["Holz"] = 20

    try:
        apply_market_trade(
            state=state,
            markets=markets,
            private_storages=private_storages,
            action={
                "type": "buy",
                "city": "Luebeck",
                "good": "Getreide",
                "qty": 1,
                "counterparty": "ship",
            },
        )
        assert False, "Expected ship total-capacity validation"
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "gesamt" in exc.detail


def test_ship_buy_rejects_when_per_good_capacity_reached():
    _, state, markets, private_storages = create_initial_state()
    active_ship = [item for item in state["ships"] if item["id"] == state["active_ship_id"]][0]
    active_ship["cargo"]["Salz"] = 20

    try:
        apply_market_trade(
            state=state,
            markets=markets,
            private_storages=private_storages,
            action={
                "type": "buy",
                "city": "Luebeck",
                "good": "Salz",
                "qty": 1,
                "counterparty": "ship",
            },
        )
        assert False, "Expected ship per-good validation"
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "pro Ware" in exc.detail


def test_storage_buy_rejects_when_per_good_capacity_reached():
    _, state, markets, private_storages = create_initial_state()
    storage = [item for item in private_storages if item["city"] == "Luebeck"][0]
    storage["stock_by_good"]["Salz"] = storage["max_per_good"]

    try:
        apply_market_trade(
            state=state,
            markets=markets,
            private_storages=private_storages,
            action={
                "type": "buy",
                "city": "Luebeck",
                "good": "Salz",
                "qty": 1,
                "counterparty": "private_storage",
            },
        )
        assert False, "Expected storage per-good validation"
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "pro Ware" in exc.detail


def test_market_trade_books_stock_and_mark():
    _, state, markets, private_storages = create_initial_state()
    row = [item for item in markets if item["city"] == "Luebeck" and item["good"] == "Salz"][0]
    old_cash = state["cash"]
    old_stock = row["stock"]

    state, markets, private_storages, event = apply_market_trade(
        state=state,
        markets=markets,
        private_storages=private_storages,
        action={"type": "buy", "city": "Luebeck", "good": "Salz", "qty": 2, "counterparty": "ship"},
    )

    row_after = [item for item in markets if item["city"] == "Luebeck" and item["good"] == "Salz"][
        0
    ]
    assert state["cash"] < old_cash
    assert row_after["stock"] == old_stock - 2
    assert event["payload"]["stock_before"] == old_stock
    assert event["payload"]["stock_after"] == old_stock - 2


def test_sell_increases_city_stock_immediately():
    _, state, markets, private_storages = create_initial_state()
    active_ship = [item for item in state["ships"] if item["id"] == state["active_ship_id"]][0]
    active_ship["cargo"]["Salz"] = 3
    row = [item for item in markets if item["city"] == "Luebeck" and item["good"] == "Salz"][0]
    old_stock = row["stock"]

    state, markets, _, event = apply_market_trade(
        state=state,
        markets=markets,
        private_storages=private_storages,
        action={
            "type": "sell",
            "city": "Luebeck",
            "good": "Salz",
            "qty": 2,
            "counterparty": "ship",
        },
    )

    row_after = [item for item in markets if item["city"] == "Luebeck" and item["good"] == "Salz"][
        0
    ]
    assert row_after["stock"] == old_stock + 2
    assert event["payload"]["stock_before"] == old_stock
    assert event["payload"]["stock_after"] == old_stock + 2


def test_advance_day_applies_primary_plus_three_secondary_minus_two():
    _, state, markets, _ = create_initial_state()
    before = {(item["city"], item["good"]): item["stock"] for item in markets}
    state, markets, events = advance_day(state=state, markets=markets)

    assert state["current_day"] == 1
    assert events == []  # Ordinary days do not crowd the business ledger.
    for row in markets:
        city = row["city"]
        good = row["good"]
        expected_delta = 3 if GAME_WORLD["city_goods"][city] == good else -2
        expected_stock = max(0, before[(city, good)] + expected_delta)
        assert row["stock"] == expected_stock
        assert row["stadt_ankaufspreis"] < row["stadt_verkaufspreis"]


def test_advance_day_clamps_stock_at_zero_for_secondary_goods():
    _, state, markets, _ = create_initial_state()
    for row in markets:
        if row["city"] == "Luebeck" and row["good"] == "Getreide":
            row["stock"] = 1
            break

    _, markets, _ = advance_day(state=state, markets=markets)
    row = [item for item in markets if item["city"] == "Luebeck" and item["good"] == "Getreide"][0]
    assert row["stock"] == 0


def test_stock_factor_linear_for_0_100_200():
    assert (
        _compute_prices(base_price=1100, stock=0, city="Rostock", good="Fisch", zero_days=0)[0]
        == 1650
    )
    assert (
        _compute_prices(base_price=1000, stock=100, city="Luebeck", good="Getreide", zero_days=0)[0]
        == 1000
    )
    assert (
        _compute_prices(base_price=1200, stock=200, city="Luebeck", good="Holz", zero_days=0)[0]
        == 600
    )


def test_zero_stock_factor_reaches_200_percent_after_30_days():
    _, state, markets, _ = create_initial_state()
    row = [item for item in markets if item["city"] == "London" and item["good"] == "Salz"][0]
    row["stock"] = 0
    row["zero_days"] = 0
    for _ in range(30):
        state, markets, _ = advance_day(state=state, markets=markets)
        row = [item for item in markets if item["city"] == "London" and item["good"] == "Salz"][0]
        row["stock"] = 0
    state, markets, _ = advance_day(state=state, markets=markets)
    row = [item for item in markets if item["city"] == "London" and item["good"] == "Salz"][0]
    assert row["zero_days"] == 30
    assert row["marktpreis"] == 4420


def test_spread_is_8_to_25_percent_between_stock_200_and_0():
    low_market, _, low_sell = _compute_prices(
        base_price=1000,
        stock=0,
        city="Luebeck",
        good="Getreide",
        zero_days=0,
    )
    high_market, _, high_sell = _compute_prices(
        base_price=1200,
        stock=200,
        city="Luebeck",
        good="Holz",
        zero_days=0,
    )
    low_spread = round((low_sell / low_market) - 1, 2)
    high_spread = round((high_sell / high_market) - 1, 2)
    assert low_spread == 0.25
    assert high_spread == 0.08


def test_remote_kontor_trade_allowed_without_ship_in_city():
    _, state, markets, private_storages = create_initial_state()
    active_ship = [item for item in state["ships"] if item["id"] == state["active_ship_id"]][0]
    assert active_ship["current_city"] == "Luebeck"
    old_cash = state["cash"]
    row_before = [
        item for item in markets if item["city"] == "London" and item["good"] == "Getreide"
    ][0]["stock"]

    state, markets, private_storages, _ = upgrade_storage(
        state=state, markets=markets, private_storages=private_storages, action={"city": "London"}
    )
    for _ in range(7):
        state, markets, _ = advance_day(
            state=state, markets=markets, private_storages=private_storages
        )
    state, markets, private_storages, event = apply_market_trade(
        state=state,
        markets=markets,
        private_storages=private_storages,
        action={
            "type": "buy",
            "city": "London",
            "good": "Getreide",
            "qty": 2,
            "counterparty": "private_storage",
        },
    )

    row_after = [
        item for item in markets if item["city"] == "London" and item["good"] == "Getreide"
    ][0]["stock"]
    storage = [item for item in private_storages if item["city"] == "London"][0]
    assert row_after == row_before - 14 - 2
    assert storage["stock_by_good"]["Getreide"] == 2
    assert state["cash"] < old_cash
    assert event["payload"]["mode"] == "kontor"


def test_ship_trade_blocked_outside_current_ship_city():
    _, state, markets, private_storages = create_initial_state()

    try:
        apply_market_trade(
            state=state,
            markets=markets,
            private_storages=private_storages,
            action={
                "type": "buy",
                "city": "London",
                "good": "Getreide",
                "qty": 1,
                "counterparty": "ship",
            },
        )
        assert False, "Expected ship city validation"
    except HTTPException as exc:
        assert exc.status_code == 422


def test_session_starts_with_one_ship_and_active_ship_id():
    _, state, _, _ = create_initial_state()
    assert state["active_ship_id"] == "ship-1"
    assert len(state["ships"]) == 1
    assert {item["id"] for item in state["ships"]} == {"ship-1"}


def test_set_course_works_for_active_ship():
    _, state, _, _ = create_initial_state()
    routes = {
        ("Luebeck", "London"): 2,
        ("London", "Luebeck"): 2,
    }
    state, event = set_course(
        state=state, destination_city="London", routes=routes, ship_id="ship-1"
    )

    ship_1 = [item for item in state["ships"] if item["id"] == "ship-1"][0]
    assert ship_1["at_sea"] is True
    assert ship_1["destination"] == "London"
    assert event["payload"]["ship_id"] == "ship-1"


def test_set_course_uses_new_world_eta_values():
    _, state, _, _ = create_initial_state()
    routes = {(item["from"], item["to"]): item["days"] for item in GAME_WORLD["routes"]}

    state, event = set_course(
        state=state, destination_city="London", routes=routes, ship_id="ship-1"
    )
    assert event["payload"]["eta_days"] == 5
    ship_1 = [item for item in state["ships"] if item["id"] == "ship-1"][0]
    assert ship_1["eta_days"] == 5


def test_travel_resolver_is_neutral_when_seasonality_disabled():
    _, state, _, _ = create_initial_state()
    assert _resolve_travel_days(7, state) == 7


def test_advance_day_reduces_eta_for_ship():
    _, state, _, _ = create_initial_state()
    routes = {
        ("Luebeck", "London"): 2,
    }
    state, _ = set_course(state=state, destination_city="London", routes=routes, ship_id="ship-1")

    state, _, _ = advance_day(state=state, markets=[])
    ship_1 = [item for item in state["ships"] if item["id"] == "ship-1"][0]
    assert ship_1["eta_days"] == 1


def test_advance_to_next_event_returns_ship_arrival():
    _, state, _, _ = create_initial_state()
    routes = {
        ("Luebeck", "London"): 2,
    }
    state, _ = set_course(state=state, destination_city="London", routes=routes, ship_id="ship-1")

    state, _, events = advance_to_next_event(state=state, markets=[])
    arrivals = [event for event in events if event["event_type"] == "ship_arrival"]
    assert len(arrivals) == 1
    assert arrivals[0]["payload"]["ship_id"] == "ship-1"
    assert arrivals[0]["payload"]["city"] == "London"


def test_transfer_wrong_city_is_validated_for_selected_ship():
    _, state, _, private_storages = create_initial_state()
    ship_1 = [item for item in state["ships"] if item["id"] == "ship-1"][0]
    ship_1["current_city"] = "London"
    for item in private_storages:
        if item["city"] == "London":
            item["level"] = 1
            item["active"] = True
            item["capacity_total"] = 80
            item["max_per_good"] = 30
            item["capacity"] = 80

    try:
        apply_transfer(
            state=state,
            private_storages=private_storages,
            action={
                "city": "Luebeck",
                "good": "Salz",
                "qty": 1,
                "direction": "ship_to_private",
                "ship_id": "ship-1",
            },
        )
        assert False, "Expected selected ship city validation"
    except HTTPException as exc:
        assert exc.status_code == 422


def test_assets_catalog_contains_expected_prices_and_capacities():
    catalog = assets_catalog()
    assert len(catalog["ships"]) == 3
    assert len(catalog["storages"]) == 4
    assert catalog["ships"][0]["buy_price"] == 90000
    assert catalog["ships"][0]["sell_price"] == 45000
    assert catalog["ships"][0]["capacity_total"] == 40
    assert catalog["ships"][0]["max_per_good"] == 20
    assert catalog["storages"][0]["capacity_total"] == 80
    assert catalog["storages"][0]["max_per_good"] == 30


def test_ship_order_is_time_neutral_and_delivered_after_seven_days():
    _, state, markets, _ = create_initial_state()
    day_before = state["current_day"]
    cash_before = state["cash"]
    state, markets, events = buy_ship(
        state=state, markets=markets, action={"city": "Luebeck", "ship_class_id": "kogge_standard"}
    )
    assert state["current_day"] == day_before
    assert len(state["ships"]) == 1
    assert state["orders"][0]["due_day"] == day_before + 7
    for _ in range(7):
        state, markets, _ = advance_day(state=state, markets=markets)
    assert len(state["ships"]) == 2
    assert state["cash"] == cash_before - 90000
    assert any(item["event_type"] == "construction_ordered" for item in events)


def test_sell_ship_is_instant_and_returns_half_price():
    _, state, markets, _ = create_initial_state()
    state, markets, _ = buy_ship(
        state=state, markets=markets, action={"city": "Luebeck", "ship_class_id": "kogge_standard"}
    )
    for _ in range(7):
        state, markets, _ = advance_day(state=state, markets=markets)
    day_before = state["current_day"]
    cash_before = state["cash"]
    state, events = sell_ship(state=state, action={"city": "Luebeck", "ship_id": "ship-2"})
    assert state["current_day"] == day_before
    assert state["cash"] == cash_before + 45000
    assert any(item["event_type"] == "ship_sold" for item in events)


def test_storage_upgrade_and_sell_follow_levels_and_prices():
    _, state, markets, storages = create_initial_state()
    london = [item for item in storages if item["city"] == "London"][0]
    assert london["level"] == 0
    state, markets, storages, events = upgrade_storage(
        state=state, markets=markets, private_storages=storages, action={"city": "London"}
    )
    for _ in range(7):
        state, markets, _ = advance_day(state=state, markets=markets, private_storages=storages)
    london = [item for item in storages if item["city"] == "London"][0]
    assert london["level"] == 1
    assert london["capacity"] == 80
    assert london["capacity_total"] == 80
    assert london["max_per_good"] == 30
    assert any(item["event_type"] == "construction_ordered" for item in events)
    day_before = state["current_day"]
    state, storages, events = sell_storage(
        state=state, private_storages=storages, action={"city": "London"}
    )
    london = [item for item in storages if item["city"] == "London"][0]
    assert state["current_day"] == day_before
    assert london["level"] == 0
    assert london["capacity"] == 0
    assert any(item["event_type"] == "storage_sold" for item in events)


def test_storage_sell_blocks_if_next_level_per_good_limit_would_be_exceeded():
    _, state, markets, storages = create_initial_state()
    state, markets, storages, _ = upgrade_storage(
        state=state, markets=markets, private_storages=storages, action={"city": "London"}
    )
    for _ in range(7):
        state, markets, _ = advance_day(state=state, markets=markets, private_storages=storages)
    state, markets, storages, _ = upgrade_storage(
        state=state, markets=markets, private_storages=storages, action={"city": "London"}
    )
    for _ in range(7):
        state, markets, _ = advance_day(state=state, markets=markets, private_storages=storages)
    london = [item for item in storages if item["city"] == "London"][0]
    london["stock_by_good"]["Salz"] = 40

    try:
        sell_storage(state=state, private_storages=storages, action={"city": "London"})
        assert False, "Expected per-good downgrade guard"
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "pro Ware" in exc.detail
