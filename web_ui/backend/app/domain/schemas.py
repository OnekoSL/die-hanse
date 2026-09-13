from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class RiskLimits(BaseModel):
    max_position_per_good: int = Field(gt=0, default=100)
    min_cash_buffer: float = Field(ge=0, default=100.0)


class StrategyConfig(BaseModel):
    type: str = "rule_based_v1"
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value != "rule_based_v1":
            raise ValueError("Nur strategy type 'rule_based_v1' ist erlaubt")
        return value


class BacktestRunRequest(BaseModel):
    scenario_id: str
    start_day: int = Field(ge=0)
    end_day: int = Field(gt=0)
    initial_cash: float = Field(gt=0)
    strategy: StrategyConfig = Field(default_factory=StrategyConfig)
    risk_limits: RiskLimits = Field(default_factory=RiskLimits)

    @field_validator("end_day")
    @classmethod
    def validate_range(cls, value: int, info):
        start_day = info.data.get("start_day", 0)
        if value <= start_day:
            raise ValueError("end_day muss groesser als start_day sein")
        return value


class ScenarioSummary(BaseModel):
    id: str
    name: str
    version: str


class ScenarioDetail(ScenarioSummary):
    payload: dict[str, Any]


class EquityPoint(BaseModel):
    day: int
    equity: float


class TradeEventOut(BaseModel):
    day: int
    city_from: str
    city_to: str | None = None
    good: str
    qty: int
    price: float
    pnl_delta: float
    side: str


class MarketSnapshotOut(BaseModel):
    day: int
    city: str
    good: str
    stock: int
    demand: int
    price: float


class BacktestSummary(BaseModel):
    roi: float
    pnl: float
    max_drawdown: float
    win_rate_trades: float
    turnover: float


class BacktestResult(BaseModel):
    run_id: str
    status: str
    duration_ms: int
    summary: BacktestSummary
    equity_curve: list[EquityPoint]
    city_snapshots: list[MarketSnapshotOut]
    trade_log: list[TradeEventOut]
    violations: list[str]


class BacktestRunListItem(BaseModel):
    run_id: str
    scenario_id: str
    created_at: datetime
    duration_ms: int
    summary: BacktestSummary


class PaginatedRuns(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[BacktestRunListItem]


class GameShipState(BaseModel):
    id: str
    name: str
    class_id: str | None = None
    buy_price: int | None = None
    current_city: str | None = None
    at_sea: bool
    destination: str | None = None
    eta_days: int = Field(ge=0, default=0)
    cargo: dict[str, int] = Field(default_factory=dict)
    capacity_total: int = Field(gt=0)
    max_per_good: int = Field(ge=0)
    capacity: int | None = Field(default=None, gt=0)


class GamePrivateStorage(BaseModel):
    city: str
    level: int = Field(ge=0, le=4, default=0)
    active: bool = False
    capacity_total: int = Field(ge=0)
    max_per_good: int = Field(ge=0)
    capacity: int | None = Field(default=None, ge=0)
    stock_by_good: dict[str, int] = Field(default_factory=dict)


class GameMarketItem(BaseModel):
    city: str
    good: str
    stock: int = Field(ge=0)
    marktpreis: int = Field(gt=0)
    stadt_ankaufspreis: int = Field(gt=0)
    stadt_verkaufspreis: int = Field(gt=0)
    production_rate: int = Field(ge=0)
    consumption_rate: int = Field(ge=0)
    zero_days: int = Field(ge=0, default=0)


class GameEventOut(BaseModel):
    id: int
    day: int
    event_type: str
    payload: dict[str, Any]
    created_at: datetime


class ConstructionOrder(BaseModel):
    id: int
    kind: Literal["ship", "storage"]
    city: str
    class_id: str | None = None
    level: int | None = None
    due_day: int = Field(ge=0)
    price: int = Field(ge=0)


class MonthlyReport(BaseModel):
    month: str
    opening_cash: int
    closing_cash: int
    trade_income: int
    trade_expenses: int
    construction_expenses: int
    asset_income: int
    cash_surplus: int


class TravelRoute(BaseModel):
    from_city: str = Field(alias="from")
    to: str
    days: int = Field(gt=0)


class GameState(BaseModel):
    revision: str
    date: str
    format_version: int
    world_version: str
    rules_version: int
    orders: list[ConstructionOrder]
    reports: list[MonthlyReport]
    routes: list[TravelRoute]

    session_id: str
    status: str
    current_day: int = Field(ge=0)
    cash: int = Field(ge=0)
    ships: list[GameShipState]
    active_ship_id: str
    ship: GameShipState
    cities: list[str] = Field(default_factory=list)
    city_primary_goods: dict[str, str] = Field(default_factory=dict)
    travel_mode: str = "normal"
    player_profile: PlayerProfile
    private_storages: list[GamePrivateStorage]
    markets: list[GameMarketItem] | None = None
    pending_event_hint: str


CityVisibilityLevel = Literal["none", "stale", "live_ship", "live_kontor", "live_both"]


class CityShipInHarbor(BaseModel):
    id: str
    name: str


class GameCityView(BaseModel):
    city: str
    primary_good: str
    visibility_level: CityVisibilityLevel
    has_live_visibility: bool
    last_seen_day: int | None = None
    days_stale: int | None = None
    status_hint: str
    markets: list[GameMarketItem] | None = None
    ships_in_harbor: list[CityShipInHarbor] | None = None
    latest_city_event_hint: str | None = None


class MarketTradeAction(BaseModel):
    revision: str | None = None
    type: str
    city: str
    good: str
    qty: int = Field(gt=0, le=200, strict=True)
    counterparty: str
    ship_id: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in {"buy", "sell"}:
            raise ValueError("type muss 'buy' oder 'sell' sein")
        return value

    @field_validator("counterparty")
    @classmethod
    def validate_counterparty(cls, value: str) -> str:
        if value not in {"ship", "private_storage"}:
            raise ValueError("counterparty muss ship oder private_storage sein")
        return value


class TransferAction(BaseModel):
    city: str
    good: str
    qty: int = Field(gt=0, le=200, strict=True)
    direction: str
    ship_id: str | None = None

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str) -> str:
        if value not in {"ship_to_private", "private_to_ship"}:
            raise ValueError("direction muss ship_to_private oder private_to_ship sein")
        return value


class SetCourseAction(BaseModel):
    destination_city: str
    ship_id: str | None = None


class NewGameSessionRequest(BaseModel):
    avatar_id: str | None = None


class PlayerProfile(BaseModel):
    avatar_id: str
    avatar_url: str


class AvatarCatalogItem(BaseModel):
    id: str
    label: str
    url: str


class AvatarCatalogResponse(BaseModel):
    items: list[AvatarCatalogItem]


class ShipBuyAction(BaseModel):
    city: str
    ship_class_id: str


class ShipSellAction(BaseModel):
    city: str
    ship_id: str


class StorageUpgradeAction(BaseModel):
    city: str


class StorageSellAction(BaseModel):
    city: str


class AssetCatalogShip(BaseModel):
    build_days: int
    id: str
    name: str
    capacity_total: int
    max_per_good: int
    capacity: int | None = None
    buy_price: int
    sell_price: int


class AssetCatalogStorageLevel(BaseModel):
    build_days: int
    level: int
    capacity_total: int
    max_per_good: int
    capacity: int | None = None
    buy_price: int
    sell_price: int


class AssetCatalogResponse(BaseModel):
    ships: list[AssetCatalogShip]
    storages: list[AssetCatalogStorageLevel]


class GameEventsResponse(BaseModel):
    items: list[GameEventOut]


class TradeQuote(BaseModel):
    revision: str
    total: int
    unit_prices: list[int]
    action: MarketTradeAction


class SaveRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    overwrite_id: str | None = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(c) < 32 for c in value):
            raise ValueError("Bitte einen lesbaren Namen angeben")
        return value


class SaveSlot(BaseModel):
    id: str
    name: str
    updated_at: datetime
    date: str


class SelectShipAction(BaseModel):
    ship_id: str
