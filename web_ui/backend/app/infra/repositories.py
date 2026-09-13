from __future__ import annotations

import json
import hashlib
import uuid

from fastapi import HTTPException
from pydantic import ValidationError
from app.infra.models import GameSnapshotTable
from app.domain.schemas import GameState
from app.engine.game_engine import materialize_state, game_date
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.schemas import (
    BacktestRunListItem,
    BacktestSummary,
    PaginatedRuns,
    ScenarioDetail,
    ScenarioSummary,
)
from app.engine.game_world import GAME_WORLD
from app.infra.models import (
    BacktestRunTable,
    EquityPointTable,
    MarketSnapshotTable,
    ScenarioTable,
    TradeEventTable,
)

STORAGE_LEVELS_BY_LEVEL = {int(item["level"]): item for item in GAME_WORLD["storage_levels"]}


class ScenarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[ScenarioSummary]:
        rows = (
            self.session.execute(select(ScenarioTable).order_by(ScenarioTable.id)).scalars().all()
        )
        return [ScenarioSummary(id=row.id, name=row.name, version=row.version) for row in rows]

    def get(self, scenario_id: str) -> ScenarioDetail | None:
        row = self.session.get(ScenarioTable, scenario_id)
        if not row:
            return None
        return ScenarioDetail(
            id=row.id, name=row.name, version=row.version, payload=json.loads(row.payload_json)
        )

    def upsert(self, *, scenario_id: str, name: str, version: str, payload: dict) -> None:
        row = self.session.get(ScenarioTable, scenario_id)
        payload_json = json.dumps(payload)
        if row:
            row.name = name
            row.version = version
            row.payload_json = payload_json
        else:
            self.session.add(
                ScenarioTable(
                    id=scenario_id,
                    name=name,
                    version=version,
                    payload_json=payload_json,
                    created_at=datetime.utcnow(),
                )
            )


class BacktestRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_run(
        self, *, run_id: str, scenario_id: str, config: dict, summary: dict, duration_ms: int
    ) -> None:
        self.session.add(
            BacktestRunTable(
                id=run_id,
                scenario_id=scenario_id,
                config_json=json.dumps(config),
                summary_json=json.dumps(summary),
                duration_ms=duration_ms,
                created_at=datetime.utcnow(),
            )
        )

    def add_equity_points(self, run_id: str, points: list[dict]) -> None:
        self.session.add_all(
            [
                EquityPointTable(run_id=run_id, day=point["day"], equity=point["equity"])
                for point in points
            ]
        )

    def add_trade_events(self, run_id: str, events: list[dict]) -> None:
        self.session.add_all(
            [
                TradeEventTable(
                    run_id=run_id,
                    day=event["day"],
                    city_from=event["city_from"],
                    city_to=event.get("city_to"),
                    good=event["good"],
                    qty=event["qty"],
                    price=event["price"],
                    pnl_delta=event["pnl_delta"],
                    side=event["side"],
                )
                for event in events
            ]
        )

    def add_snapshots(self, run_id: str, snapshots: list[dict]) -> None:
        self.session.add_all(
            [
                MarketSnapshotTable(
                    run_id=run_id,
                    day=snapshot["day"],
                    city=snapshot["city"],
                    good=snapshot["good"],
                    stock=snapshot["stock"],
                    demand=snapshot["demand"],
                    price=snapshot["price"],
                )
                for snapshot in snapshots
            ]
        )

    def get_run(self, run_id: str) -> dict | None:
        run = self.session.get(BacktestRunTable, run_id)
        if not run:
            return None

        equity = (
            self.session.execute(
                select(EquityPointTable)
                .where(EquityPointTable.run_id == run_id)
                .order_by(EquityPointTable.day)
            )
            .scalars()
            .all()
        )
        trades = (
            self.session.execute(
                select(TradeEventTable)
                .where(TradeEventTable.run_id == run_id)
                .order_by(TradeEventTable.day)
            )
            .scalars()
            .all()
        )
        snapshots = (
            self.session.execute(
                select(MarketSnapshotTable)
                .where(MarketSnapshotTable.run_id == run_id)
                .order_by(MarketSnapshotTable.day)
            )
            .scalars()
            .all()
        )

        return {
            "run_id": run.id,
            "status": "completed",
            "duration_ms": run.duration_ms,
            "summary": json.loads(run.summary_json),
            "equity_curve": [{"day": row.day, "equity": row.equity} for row in equity],
            "trade_log": [
                {
                    "day": row.day,
                    "city_from": row.city_from,
                    "city_to": row.city_to,
                    "good": row.good,
                    "qty": row.qty,
                    "price": row.price,
                    "pnl_delta": row.pnl_delta,
                    "side": row.side,
                }
                for row in trades
            ],
            "city_snapshots": [
                {
                    "day": row.day,
                    "city": row.city,
                    "good": row.good,
                    "stock": row.stock,
                    "demand": row.demand,
                    "price": row.price,
                }
                for row in snapshots
            ],
            "violations": [],
        }

    def list_runs(self, page: int, page_size: int) -> PaginatedRuns:
        total = self.session.execute(
            select(func.count()).select_from(BacktestRunTable)
        ).scalar_one()
        offset = (page - 1) * page_size
        runs = (
            self.session.execute(
                select(BacktestRunTable)
                .order_by(BacktestRunTable.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            .scalars()
            .all()
        )

        items = [
            BacktestRunListItem(
                run_id=row.id,
                scenario_id=row.scenario_id,
                created_at=row.created_at,
                duration_ms=row.duration_ms,
                summary=BacktestSummary(**json.loads(row.summary_json)),
            )
            for row in runs
        ]
        return PaginatedRuns(page=page, page_size=page_size, total=int(total), items=items)


class GameRepository:
    """Complete snapshots; the caller owns the SQLite transaction and write lock."""

    def __init__(self, session: Session):
        self.session = session

    def load(self, slot_id: str = "active") -> tuple[dict, list[dict], list[dict]]:
        row = self.session.get(GameSnapshotTable, slot_id)
        if row is None:
            raise HTTPException(404, "Kein Spielstand vorhanden")
        try:
            if hashlib.sha256(row.payload_json.encode()).hexdigest() != row.checksum:
                raise ValueError("Prüfsumme stimmt nicht")
            data = json.loads(row.payload_json)
            state, markets, storages = data["state"], data["markets"], data["storages"]
            validate_snapshot(state, markets, storages)
            return state, markets, storages
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
            OverflowError,
            AttributeError,
        ) as exc:
            raise HTTPException(
                422, "Spielstand beschädigt oder inkompatibel; unverändert erhalten"
            ) from exc

    def save(
        self,
        state: dict,
        markets: list[dict],
        storages: list[dict],
        slot_id: str = "active",
        name: str = "Automatisch",
    ) -> str:
        validate_snapshot(state, markets, storages)
        payload = json.dumps(
            {"state": state, "markets": markets, "storages": storages},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        row = self.session.get(GameSnapshotTable, slot_id)
        if row is None:
            row = GameSnapshotTable(id=slot_id)
            self.session.add(row)
        row.name = name
        row.payload_json = payload
        row.checksum = hashlib.sha256(payload.encode()).hexdigest()
        row.game_date = game_date(state).isoformat()
        row.updated_at = datetime.utcnow()
        self.session.flush()
        return slot_id

    def list_saves(self) -> list[dict]:
        rows = self.session.scalars(
            select(GameSnapshotTable)
            .where(GameSnapshotTable.id != "active")
            .order_by(GameSnapshotTable.updated_at.desc())
        ).all()
        return [
            {"id": r.id, "name": r.name, "date": r.game_date, "updated_at": r.updated_at}
            for r in rows
        ]

    def archive_active(self, name: str) -> None:
        """Preserve the exact original bytes, including an unreadable autosave."""
        row = self.session.get(GameSnapshotTable, "active")
        if row is not None:
            self.session.add(
                GameSnapshotTable(
                    id=str(uuid.uuid4()),
                    name=name,
                    payload_json=row.payload_json,
                    checksum=row.checksum,
                    game_date=row.game_date,
                    updated_at=datetime.utcnow(),
                )
            )
            self.session.flush()

    def manual_save(self, name: str, overwrite_id: str | None) -> dict:
        if overwrite_id == "active":
            raise HTTPException(
                422, "Automatischen Spielstand nicht als Speicherplatz überschreiben"
            )
        if overwrite_id and self.session.get(GameSnapshotTable, overwrite_id) is None:
            raise HTTPException(404, "Speicherplatz nicht gefunden")
        state, markets, storages = self.load()
        slot_id = self.save(state, markets, storages, overwrite_id or str(uuid.uuid4()), name)
        return next(row for row in self.list_saves() if row["id"] == slot_id)


def validate_snapshot(state: dict, markets: list[dict], storages: list[dict]) -> None:
    if (state["format_version"], state["world_version"], state["rules_version"]) != (
        1,
        "alpha-world-1",
        1,
    ):
        raise ValueError("Unbekannte Version")
    cities, goods = set(GAME_WORLD["cities"]), set(GAME_WORLD["goods"])
    if type(state["cash"]) is not int or state["cash"] < 0:
        raise ValueError("Ungültiges Geldformat")
    if type(state["current_day"]) is not int or not 0 <= state["current_day"] <= 300000:
        raise ValueError("Ungültiges Datum")
    if len(markets) != len(cities) * len(goods) or {(m["city"], m["good"]) for m in markets} != {
        (c, g) for c in cities for g in goods
    }:
        raise ValueError("Unvollständige Märkte")
    if len(storages) != len(cities) or {s["city"] for s in storages} != cities:
        raise ValueError("Unvollständige Kontore")
    ids = [ship["id"] for ship in state["ships"]]
    if not ids or len(ids) != len(set(ids)) or state["active_ship_id"] not in ids:
        raise ValueError("Ungültige Flotte")
    for owner in state["ships"] + storages:
        inventory = owner.get("cargo", owner.get("stock_by_good"))
        if set(inventory) != goods or any(type(v) is not int or v < 0 for v in inventory.values()):
            raise ValueError("Ungültige Warenbestände")
        if sum(inventory.values()) > owner["capacity_total"] or any(
            v > owner["max_per_good"] for v in inventory.values()
        ):
            raise ValueError("Kapazität überschritten")
    for ship in state["ships"]:
        if ship["at_sea"]:
            if (
                ship["current_city"] is not None
                or ship["destination"] not in cities
                or ship["eta_days"] <= 0
            ):
                raise ValueError("Ungültige Reise")
        elif (
            ship["current_city"] not in cities
            or ship["eta_days"] != 0
            or ship["destination"] is not None
        ):
            raise ValueError("Ungültiger Hafen")
    for market in markets:
        if type(market["stock"]) is not int or not 0 <= market["stock"] <= 200:
            raise ValueError("Ungültiger Marktbestand")
        for key in ("base_price", "marktpreis", "stadt_ankaufspreis", "stadt_verkaufspreis"):
            if type(market[key]) is not int or market[key] <= 0:
                raise ValueError("Ungültiger Preis")
    for order in state["orders"]:
        if order["city"] not in cities or order["due_day"] <= state["current_day"]:
            raise ValueError("Ungültiger Bauauftrag")
        if order["kind"] == "ship" and order["class_id"] not in {
            s["id"] for s in GAME_WORLD["ship_catalog"]
        }:
            raise ValueError("Unbekannte Schiffsklasse")
        if order["kind"] == "storage" and not 1 <= order["level"] <= 4:
            raise ValueError("Ungültige Kontorstufe")
    for key in (
        "opening_cash",
        "trade_income",
        "trade_expenses",
        "construction_expenses",
        "asset_income",
    ):
        if type(state["month"][key]) is not int or state["month"][key] < 0:
            raise ValueError("Ungültige Monatsbuchung")
    if not isinstance(state["events"], list) or not isinstance(state["intel"], dict):
        raise ValueError("Ungültige Chronik")
    GameState.model_validate(materialize_state(state, markets, storages, include_markets=True))
