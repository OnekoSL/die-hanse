import copy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.infra.db import SessionLocal, init_db
from app.infra.models import GameSnapshotTable
from app.infra.repositories import GameRepository
from app.engine.game_world import ROUTES, GAME_WORLD


@pytest.fixture
def client():
    with TestClient(app) as client:
        assert client.post("/api/v1/game/session/new").status_code == 200
        yield client


def active(c):
    r = c.get("/api/v1/game/session/active")
    assert r.status_code == 200, r.text
    return r.json()


def action(c, name, payload=None):
    r = c.post("/api/v1/game/action/" + name, json=payload or {})
    assert r.status_code == 200, r.text
    return r.json()


def trade(c, side="buy", city="Luebeck", good="Salz", qty=10, target="ship"):
    data = {"type": side, "city": city, "good": good, "qty": qty, "counterparty": target}
    quote = action(c, "market-quote", data)
    before = active(c)
    result = action(c, "market-trade", {**data, "revision": quote["revision"]})
    assert abs(result["cash"] - before["cash"]) == quote["total"]
    assert quote["total"] == sum(quote["unit_prices"])
    return result


def market(c, city, good):
    return next(
        m for m in c.get("/api/v1/game/city-view/" + city).json()["markets"] if m["good"] == good
    )


def test_initial_world_money_and_catalog(client):
    s = active(client)
    assert s["cash"] == 100000 and s["date"] == "1400-03-01"
    assert len(s["cities"]) == 11 and len(s["ship"]["cargo"]) == 9
    assert s["city_primary_goods"]["Riga"] == "Wachs"
    assert "Pelze" in s["ship"]["cargo"]
    assert len(s["routes"]) == 110
    assert ROUTES["Luebeck", "London"] == 5
    assert all(0 < d < 30 and d == ROUTES[b, a] for (a, b), d in ROUTES.items())
    catalog = client.get("/api/v1/game/assets/catalog").json()
    assert [s["buy_price"] for s in catalog["ships"]] == [90000, 160000, 260000]
    assert [s["build_days"] for s in catalog["ships"]] == [7, 14, 21]
    assert all(s["build_days"] == 7 for s in catalog["storages"])


def test_quote_is_read_only_and_trade_matches_ledger(client):
    before = active(client)
    data = {"type": "buy", "city": "Luebeck", "good": "Salz", "qty": 10, "counterparty": "ship"}
    quote = action(client, "market-quote", data)
    assert active(client) == before
    result = action(client, "market-trade", {**data, "revision": quote["revision"]})
    assert result["current_day"] == 0 and result["ship"]["cargo"]["Salz"] == 10
    assert before["cash"] - result["cash"] == 10985 == quote["total"]
    event = client.get("/api/v1/game/events").json()["items"][0]
    assert event["payload"]["total"] == quote["total"]
    assert market(client, "Luebeck", "Salz")["stock"] == 150


@pytest.mark.parametrize("side", ["buy", "sell"])
def test_split_trades_match_combined_trade(client, side):
    if side == "sell":
        trade(client, qty=10)
    slot = client.post("/api/v1/game/saves", json={"name": "Vor Vergleich"}).json()["id"]
    combined = trade(client, side=side, qty=10)
    assert client.post(f"/api/v1/game/saves/{slot}/load").status_code == 200
    for quantity in (3, 2, 5):
        split = trade(client, side=side, qty=quantity)
    assert split["cash"] == combined["cash"]
    assert split["ships"] == combined["ships"]


@pytest.mark.parametrize(
    "changes",
    [
        {"qty": 0},
        {"qty": -1},
        {"qty": 1.5},
        {"qty": True},
        {"qty": 201},
        {"good": "Gold"},
        {"city": "Atlantis"},
        {"counterparty": "other"},
        {"qty": 21},
        {"city": "London"},
        {"type": "sell"},
    ],
)
def test_invalid_trade_has_no_side_effects(client, changes):
    before = active(client)
    payload = {
        "type": "buy",
        "city": "Luebeck",
        "good": "Salz",
        "qty": 1,
        "counterparty": "ship",
        "revision": before["revision"],
        **changes,
    }
    assert client.post("/api/v1/game/action/market-trade", json=payload).status_code == 422
    assert active(client) == before


def test_quote_conflicts_after_time_and_repeated_submission(client):
    payload = {"type": "buy", "city": "Luebeck", "good": "Salz", "qty": 1, "counterparty": "ship"}
    quote = action(client, "market-quote", payload)
    action(client, "advance-day")
    before = active(client)
    assert (
        client.post(
            "/api/v1/game/action/market-trade", json={**payload, "revision": quote["revision"]}
        ).status_code
        == 409
    )
    assert active(client) == before
    quote = action(client, "market-quote", payload)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: (
                    client.post(
                        "/api/v1/game/action/market-trade",
                        json={**payload, "revision": quote["revision"]},
                    ).status_code
                ),
                range(2),
            )
        )
    assert sorted(results) == [200, 409]
    assert active(client)["ship"]["cargo"]["Salz"] == 1


def test_transfer_roundtrip_and_capacity_guard(client):
    trade(client, qty=20)
    data = {"city": "Luebeck", "good": "Salz", "qty": 20, "direction": "ship_to_private"}
    result = action(client, "transfer", data)
    assert result["ship"]["cargo"]["Salz"] == 0
    result = action(client, "transfer", {**data, "direction": "private_to_ship"})
    assert result["ship"]["cargo"]["Salz"] == 20
    before = active(client)
    assert client.post("/api/v1/game/action/transfer", json={**data, "qty": 21}).status_code == 422
    assert active(client) == before


def test_full_market_refuses_sale_without_losing_goods(client):
    trade(client, qty=10)
    for _ in range(17):
        action(client, "advance-day")
    assert market(client, "Luebeck", "Salz")["stock"] == 200
    before = active(client)
    r = client.post(
        "/api/v1/game/action/market-trade",
        json={
            "type": "sell",
            "city": "Luebeck",
            "good": "Salz",
            "qty": 1,
            "counterparty": "ship",
            "revision": before["revision"],
        },
    )
    assert r.status_code == 422
    assert active(client) == before


def test_visiting_and_leaving_harbor_preserves_last_seen_market(client):
    unknown = client.get("/api/v1/game/city-view/London").json()
    assert unknown["markets"] is None
    action(client, "set-course", {"destination_city": "London"})
    arrived = action(client, "advance-next-event")
    assert arrived["current_day"] == 5 and arrived["ship"]["current_city"] == "London"
    live = client.get("/api/v1/game/city-view/London").json()
    assert live["has_live_visibility"]
    action(client, "set-course", {"destination_city": "Bruegge"})
    action(client, "advance-day")
    stale = client.get("/api/v1/game/city-view/London").json()
    assert stale["days_stale"] == 1 and stale["markets"] == live["markets"]
    assert not stale["has_live_visibility"]
    assert client.get("/api/v1/game/events").json()["items"]


def test_remote_office_available_only_after_construction(client):
    before = active(client)
    result = action(client, "storage-upgrade", {"city": "London"})
    assert result["current_day"] == 0 and result["cash"] == before["cash"] - 20000
    assert not next(s for s in result["private_storages"] if s["city"] == "London")["active"]
    assert (
        client.post("/api/v1/game/action/storage-upgrade", json={"city": "London"}).status_code
        == 422
    )
    result = action(client, "advance-next-event")
    assert result["current_day"] == 7
    trade(client, city="London", qty=2, target="private_storage")
    assert active(client)["ship"]["current_city"] == "Luebeck"


def test_ship_delivery_and_sale(client):
    s = action(client, "ship-buy", {"city": "Hamburg", "ship_class_id": "kogge_standard"})
    assert s["cash"] == 10000 and len(s["ships"]) == 1 and s["current_day"] == 0
    s = action(client, "advance-next-event")
    assert len(s["ships"]) == 2 and s["current_day"] == 7
    action(client, "select-ship", {"ship_id": "ship-2"})
    s = action(client, "ship-sell", {"ship_id": "ship-2", "city": "Hamburg"})
    assert s["cash"] == 55000 and s["active_ship_id"] == "ship-1"
    assert (
        client.post(
            "/api/v1/game/action/ship-sell", json={"ship_id": "ship-1", "city": "Luebeck"}
        ).status_code
        == 422
    )


def test_monthly_report_and_next_event_without_ships(client):
    trade(client, qty=10)
    s = action(client, "advance-next-event")
    assert s["date"] == "1400-04-01" and len(s["reports"]) == 1
    r = s["reports"][0]
    assert r["opening_cash"] == 100000 and r["trade_expenses"] == 10985
    assert r["closing_cash"] == 89015 and r["cash_surplus"] == -10985
    assert client.get("/api/v1/game/events").json()["items"][0]["day"] == 30
    s = action(client, "advance-day")
    assert len(s["reports"]) == 1


def test_named_save_restores_travel_orders_intel_and_reports(client):
    trade(client, qty=10)
    action(client, "storage-upgrade", {"city": "London"})
    action(client, "set-course", {"destination_city": "Nowgorod"})
    before = active(client)
    events = client.get("/api/v1/game/events").json()
    slot = client.post("/api/v1/game/saves", json={"name": "Auf See"}).json()["id"]
    action(client, "advance-next-event")
    loaded = client.post(f"/api/v1/game/saves/{slot}/load").json()
    assert loaded["revision"] != before["revision"]
    for key in before.keys() - {"revision"}:
        assert loaded[key] == before[key]
    assert client.get("/api/v1/game/events").json() == events
    assert len(client.get("/api/v1/game/saves").json()) >= 2
    assert (
        client.post(
            "/api/v1/game/saves", json={"name": "Ersetzt", "overwrite_id": slot}
        ).status_code
        == 200
    )


@pytest.mark.parametrize("kind", ["checksum", "version", "shape"])
def test_corrupt_save_does_not_replace_active(client, kind):
    slot = client.post("/api/v1/game/saves", json={"name": "Defekt"}).json()["id"]
    with SessionLocal() as session:
        row = session.get(GameSnapshotTable, slot)
        data = json.loads(row.payload_json)
        if kind == "version":
            data["state"]["format_version"] = 999
        if kind == "shape":
            data["markets"] = []
        row.payload_json = json.dumps(data)
        if kind != "checksum":
            row.checksum = hashlib.sha256(row.payload_json.encode()).hexdigest()
        session.commit()
    before = active(client)
    assert client.post(f"/api/v1/game/saves/{slot}/load").status_code == 422
    assert active(client) == before
    with SessionLocal() as session:
        assert session.get(GameSnapshotTable, slot) is not None


def test_restart_and_reinitialization_preserve_saves(client):
    trade(client, qty=3)
    slot = client.post("/api/v1/game/saves", json={"name": "Neustart"}).json()["id"]
    before = active(client)
    init_db()
    with TestClient(app) as restarted:
        assert active(restarted) == before
        assert any(s["id"] == slot for s in restarted.get("/api/v1/game/saves").json())


def test_insufficient_cash_and_storage_downgrade_are_atomic(client):
    before = active(client)
    assert (
        client.post(
            "/api/v1/game/action/ship-buy",
            json={"city": "Luebeck", "ship_class_id": "fernhaendler"},
        ).status_code
        == 422
    )
    assert active(client) == before
    trade(client, qty=10, target="private_storage")
    before = active(client)
    assert (
        client.post("/api/v1/game/action/storage-sell", json={"city": "Luebeck"}).status_code == 422
    )
    assert active(client) == before


def test_every_city_reachable_and_each_market_has_nine_goods(client):
    for city in GAME_WORLD["cities"]:
        if active(client)["ship"]["current_city"] != city:
            action(client, "set-course", {"destination_city": city})
            while active(client)["ship"]["at_sea"]:
                action(client, "advance-next-event")
        view = client.get("/api/v1/game/city-view/" + city).json()
        assert len(view["markets"]) == 9
        assert view["has_live_visibility"]


def test_daily_and_skip_ordering_on_month_boundary(client):
    # Arrange a valid April 1 coincidence: ship construction, office construction, arrival.
    from app.engine import game_engine as g

    with SessionLocal() as session:
        repo = GameRepository(session)
        state, markets, storages = repo.load()
        state["cash"] = state["month"]["opening_cash"] = 300000
        for _ in range(24):
            state, markets, _ = g.advance_day(
                state=state, markets=markets, private_storages=storages
            )
        state, markets, e = g.buy_ship(
            state=state,
            markets=markets,
            action={"city": "London", "ship_class_id": "kogge_standard"},
        )
        g.record_events(state, e)
        state, markets, storages, e = g.upgrade_storage(
            state=state, markets=markets, private_storages=storages, action={"city": "London"}
        )
        g.record_events(state, e)
        state, markets, _ = g.advance_day(state=state, markets=markets, private_storages=storages)
        state, e = g.set_course(state=state, routes=ROUTES, destination_city="Riga")
        g.record_events(state, [e])
        daily = copy.deepcopy((state, markets, storages))
        for _ in range(6):
            daily_state, daily_markets, _ = g.advance_day(
                state=daily[0], markets=daily[1], private_storages=daily[2]
            )
            daily = (daily_state, daily_markets, daily[2])
        state, markets, _ = g.advance_to_next_event(
            state=state, markets=markets, private_storages=storages
        )
        assert (state, markets, storages) == daily
        assert [e["event_type"] for e in state["events"][-4:]] == [
            "month_closed",
            "construction_completed",
            "construction_completed",
            "ship_arrival",
        ]
        assert state["current_day"] == 31
        assert next(s for s in storages if s["city"] == "London")["level"] == 1


@pytest.mark.parametrize("replacement", ["new", "load"])
def test_corrupt_active_is_preserved_when_replaced(client, replacement):
    slot = client.post("/api/v1/game/saves", json={"name": "Intakt"}).json()["id"]
    broken = '{"broken": true}'
    with SessionLocal() as session:
        row = session.get(GameSnapshotTable, "active")
        row.payload_json = broken
        row.checksum = "original-checksum"
        session.commit()
    assert client.get("/api/v1/game/session/active").status_code == 422
    path = "/session/new" if replacement == "new" else f"/saves/{slot}/load"
    assert client.post("/api/v1/game" + path).status_code == 200
    assert active(client)["cash"] == 100000
    with SessionLocal() as session:
        from sqlalchemy import select

        rows = session.scalars(select(GameSnapshotTable)).all()
        assert any(
            row.payload_json == broken
            and row.checksum == "original-checksum"
            and row.id != "active"
            for row in rows
        )


def test_commit_failure_is_not_reported_as_success_and_rolls_back(client, monkeypatch):
    from sqlalchemy.orm import Session

    before = active(client)

    def fail_commit(self):
        raise RuntimeError("Simulated disk failure")

    with TestClient(app, raise_server_exceptions=False) as failing:
        with monkeypatch.context() as patch:
            patch.setattr(Session, "commit", fail_commit)
            result = failing.post("/api/v1/game/action/advance-day")
            assert result.status_code == 500
    assert active(client) == before
