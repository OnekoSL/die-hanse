from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from copy import deepcopy
import uuid

from sqlalchemy import text
from app.domain.schemas import (
    BacktestResult,
    BacktestRunRequest,
    PaginatedRuns,
    ScenarioDetail,
    ScenarioSummary,
    GameState,
    GameCityView,
    GameEventsResponse,
    MarketTradeAction,
    TransferAction,
    SetCourseAction,
    ShipBuyAction,
    ShipSellAction,
    StorageUpgradeAction,
    StorageSellAction,
    AssetCatalogResponse,
    AvatarCatalogResponse,
    SaveRequest,
    SaveSlot,
    TradeQuote,
    SelectShipAction,
)
from app.engine import game_engine as game
from app.engine.game_world import ROUTES
from app.engine.simulation import run_backtest
from app.infra.db import get_session, SessionLocal
from app.infra.repositories import BacktestRepository, GameRepository, ScenarioRepository

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "application": "die-hanse", "version": "0.1.0-alpha.1"}


@router.get("/scenarios", response_model=list[ScenarioSummary])
def list_scenarios(session: Session = Depends(get_session)):
    return ScenarioRepository(session).list()


@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetail)
def get_scenario(scenario_id: str, session: Session = Depends(get_session)):
    scenario = ScenarioRepository(session).get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario nicht gefunden")
    return scenario


@router.post("/backtests/run", response_model=BacktestResult)
def run(request: BacktestRunRequest, session: Session = Depends(get_session)):
    scenario_repo = ScenarioRepository(session)
    scenario = scenario_repo.get(request.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario nicht gefunden")

    if request.end_day > int(scenario.payload.get("max_day", 365)):
        raise HTTPException(status_code=422, detail="end_day ausserhalb Szenario")

    output = run_backtest(scenario.payload, request)
    repo = BacktestRepository(session)
    repo.create_run(
        run_id=output.run_id,
        scenario_id=request.scenario_id,
        config=request.model_dump(),
        summary=output.summary,
        duration_ms=output.duration_ms,
    )
    repo.add_equity_points(output.run_id, output.equity_curve)
    repo.add_trade_events(output.run_id, output.trade_log)
    repo.add_snapshots(output.run_id, output.city_snapshots)
    session.commit()

    return BacktestResult(
        run_id=output.run_id,
        status=output.status,
        duration_ms=output.duration_ms,
        summary=output.summary,
        equity_curve=output.equity_curve,
        city_snapshots=output.city_snapshots,
        trade_log=output.trade_log,
        violations=output.violations,
    )


@router.get("/backtests/{run_id}", response_model=BacktestResult)
def get_run(run_id: str, session: Session = Depends(get_session)):
    row = BacktestRepository(session).get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run nicht gefunden")
    return BacktestResult(**row)


@router.get("/backtests", response_model=PaginatedRuns)
def list_runs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    return BacktestRepository(session).list_runs(page=page, page_size=page_size)


def game_session():
    # BEGIN IMMEDIATE serializes read/modify/write across threads and processes.
    with SessionLocal() as session:
        session.execute(text("BEGIN IMMEDIATE"))
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def response(state, markets, storages):
    return GameState(**game.materialize_state(state, markets, storages))


def persist(repo, state, markets, storages):
    game.refresh_intel(state, markets, storages)
    state["revision"] = str(uuid.uuid4())
    repo.save(state, markets, storages)
    return response(state, markets, storages)


@router.post("/game/session/new", response_model=GameState)
def game_session_new(session: Session = Depends(game_session, scope="function")):
    repo = GameRepository(session)
    repo.archive_active("Vor neuem Spiel")
    _, state, markets, storages = game.create_initial_state()
    game.record_events(state, [{"event_type": "session_started", "payload": {"city": "Luebeck"}}])
    return persist(repo, state, markets, storages)


@router.get("/game/session/active", response_model=GameState)
def game_session_active(session: Session = Depends(game_session, scope="function")):
    return response(*GameRepository(session).load())


@router.get("/game/city-view/{city}", response_model=GameCityView)
def game_city_view(city: str, session: Session = Depends(game_session, scope="function")):
    state, markets, storages = GameRepository(session).load()
    view, _, _ = game.build_city_view(
        state=state,
        markets=markets,
        private_storages=storages,
        city=city,
        intel=state["intel"].get(city),
    )
    return GameCityView(**view)


@router.get("/game/events", response_model=GameEventsResponse)
def game_events(
    limit: int = Query(default=100, ge=1, le=10000),
    session: Session = Depends(game_session, scope="function"),
):
    state, _, _ = GameRepository(session).load()
    return {"items": list(reversed(state["events"][-limit:]))}


@router.get("/game/assets/catalog", response_model=AssetCatalogResponse)
def game_assets_catalog():
    return game.assets_catalog()


@router.get("/game/avatars", response_model=AvatarCatalogResponse)
def game_avatars():
    return game.avatars_catalog()


@router.post("/game/action/market-quote", response_model=TradeQuote)
def game_market_quote(
    action: MarketTradeAction, session: Session = Depends(game_session, scope="function")
):
    state, markets, storages = GameRepository(session).load()
    _, _, _, event = game.apply_market_trade(
        state=deepcopy(state),
        markets=deepcopy(markets),
        private_storages=deepcopy(storages),
        action=action.model_dump(),
    )
    return {
        "revision": state["revision"],
        "total": event["payload"]["total"],
        "unit_prices": event["payload"]["unit_prices"],
        "action": action,
    }


@router.post("/game/action/market-trade", response_model=GameState)
def game_market_trade(
    action: MarketTradeAction, session: Session = Depends(game_session, scope="function")
):
    repo = GameRepository(session)
    state, markets, storages = repo.load()
    if action.revision != state["revision"]:
        raise HTTPException(409, "Spielstand geändert. Bitte eine neue Handelsvorschau anfordern.")
    state, markets, storages, event = game.apply_market_trade(
        state=state, markets=markets, private_storages=storages, action=action.model_dump()
    )
    game.record_events(state, [event])
    return persist(repo, state, markets, storages)


def execute(action_name: str, action: dict, session: Session):
    repo = GameRepository(session)
    state, markets, storages = repo.load()
    game.refresh_intel(state, markets, storages)
    if action_name == "transfer":
        state, storages, event = game.apply_transfer(
            state=state, private_storages=storages, action=action
        )
        events = [event]
    elif action_name == "set-course":
        state, event = game.set_course(state=state, routes=ROUTES, **action)
        events = [event]
    elif action_name == "ship-buy":
        state, markets, events = game.buy_ship(state=state, markets=markets, action=action)
    elif action_name == "ship-sell":
        state, events = game.sell_ship(state=state, action=action)
    elif action_name == "storage-upgrade":
        state, markets, storages, events = game.upgrade_storage(
            state=state, markets=markets, private_storages=storages, action=action
        )
    elif action_name == "storage-sell":
        state, storages, events = game.sell_storage(
            state=state, private_storages=storages, action=action
        )
    elif action_name == "select-ship":
        game._get_ship(state, action["ship_id"])
        state["active_ship_id"] = action["ship_id"]
        events = []
    else:
        function = game.advance_day if action_name == "advance-day" else game.advance_to_next_event
        state, markets, _ = function(state=state, markets=markets, private_storages=storages)
        events = []  # The calendar records events at their actual day, including month-end.
    game.record_events(state, events)
    return persist(repo, state, markets, storages)


@router.post("/game/action/transfer", response_model=GameState)
def game_transfer(
    action: TransferAction, session: Session = Depends(game_session, scope="function")
):
    return execute("transfer", action.model_dump(), session)


@router.post("/game/action/set-course", response_model=GameState)
def game_set_course(
    action: SetCourseAction, session: Session = Depends(game_session, scope="function")
):
    return execute("set-course", action.model_dump(), session)


@router.post("/game/action/select-ship", response_model=GameState)
def game_select_ship(
    action: SelectShipAction, session: Session = Depends(game_session, scope="function")
):
    return execute("select-ship", action.model_dump(), session)


@router.post("/game/action/ship-buy", response_model=GameState)
def game_ship_buy(
    action: ShipBuyAction, session: Session = Depends(game_session, scope="function")
):
    return execute("ship-buy", action.model_dump(), session)


@router.post("/game/action/ship-sell", response_model=GameState)
def game_ship_sell(
    action: ShipSellAction, session: Session = Depends(game_session, scope="function")
):
    return execute("ship-sell", action.model_dump(), session)


@router.post("/game/action/storage-upgrade", response_model=GameState)
def game_storage_upgrade(
    action: StorageUpgradeAction, session: Session = Depends(game_session, scope="function")
):
    return execute("storage-upgrade", action.model_dump(), session)


@router.post("/game/action/storage-sell", response_model=GameState)
def game_storage_sell(
    action: StorageSellAction, session: Session = Depends(game_session, scope="function")
):
    return execute("storage-sell", action.model_dump(), session)


@router.post("/game/action/advance-day", response_model=GameState)
def game_advance_day(session: Session = Depends(game_session, scope="function")):
    return execute("advance-day", {}, session)


@router.post("/game/action/advance-next-event", response_model=GameState)
def game_advance_next_event(session: Session = Depends(game_session, scope="function")):
    return execute("advance-next-event", {}, session)


@router.get("/game/saves", response_model=list[SaveSlot])
def game_saves(session: Session = Depends(game_session, scope="function")):
    return GameRepository(session).list_saves()


@router.post("/game/saves", response_model=SaveSlot)
def game_save(action: SaveRequest, session: Session = Depends(game_session, scope="function")):
    return GameRepository(session).manual_save(action.name, action.overwrite_id)


@router.post("/game/saves/{slot_id}/load", response_model=GameState)
def game_load(slot_id: str, session: Session = Depends(game_session, scope="function")):
    repo = GameRepository(session)
    state, markets, storages = repo.load(slot_id)  # Validate before touching the active state.
    if slot_id != "active":
        repo.archive_active("Vor Laden")
    return persist(repo, state, markets, storages)
