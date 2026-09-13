export type ScenarioSummary = { id: string; name: string; version: string };

export type ScenarioDetail = ScenarioSummary & {
  payload: Record<string, unknown>;
};

export type BacktestRunRequest = {
  scenario_id: string;
  start_day: number;
  end_day: number;
  initial_cash: number;
  strategy: { type: "rule_based_v1"; params: Record<string, unknown> };
  risk_limits: { max_position_per_good: number; min_cash_buffer: number };
};

export type BacktestSummary = {
  roi: number;
  pnl: number;
  max_drawdown: number;
  win_rate_trades: number;
  turnover: number;
};

export type EquityPoint = { day: number; equity: number };

export type TradeEvent = {
  day: number;
  city_from: string;
  city_to?: string | null;
  good: string;
  qty: number;
  price: number;
  pnl_delta: number;
  side: "buy" | "sell";
};

export type CitySnapshot = {
  day: number;
  city: string;
  good: string;
  stock: number;
  demand: number;
  price: number;
};

export type BacktestResult = {
  run_id: string;
  status: string;
  duration_ms: number;
  summary: BacktestSummary;
  equity_curve: EquityPoint[];
  city_snapshots: CitySnapshot[];
  trade_log: TradeEvent[];
  violations: string[];
};

export type BacktestRunListItem = {
  run_id: string;
  scenario_id: string;
  created_at: string;
  duration_ms: number;
  summary: BacktestSummary;
};

export type PaginatedRuns = {
  page: number;
  page_size: number;
  total: number;
  items: BacktestRunListItem[];
};

export type GameShipState = {
  id: string;
  name: string;
  class_id?: string | null;
  buy_price?: number | null;
  current_city: string | null;
  at_sea: boolean;
  destination: string | null;
  eta_days: number;
  cargo: Record<string, number>;
  capacity_total: number;
  max_per_good: number;
  capacity?: number;
};

export type GamePrivateStorage = {
  city: string;
  level: number;
  active: boolean;
  capacity_total: number;
  max_per_good: number;
  capacity?: number;
  stock_by_good: Record<string, number>;
};

export type GameMarketItem = {
  city: string;
  good: string;
  stock: number;
  marktpreis: number;
  stadt_ankaufspreis: number;
  stadt_verkaufspreis: number;
  production_rate: number;
  consumption_rate: number;
  zero_days?: number;
};

export type GameState = {
  revision: string;
  date: string;
  format_version: number;
  world_version: string;
  rules_version: number;
  orders: ConstructionOrder[];
  reports: MonthlyReport[];
  routes: { from: string; to: string; days: number }[];
  session_id: string;
  status: string;
  current_day: number;
  cash: number;
  ships: GameShipState[];
  active_ship_id: string;
  ship: GameShipState;
  player_profile: PlayerProfile;
  cities: string[];
  city_primary_goods: Record<string, string>;
  private_storages: GamePrivateStorage[];
  markets?: GameMarketItem[] | null;
  pending_event_hint: string;
};

export type PlayerProfile = {
  avatar_id: string;
  avatar_url: string;
};

export type NewGameSessionRequest = {
  avatar_id?: string | null;
};

export type AvatarCatalogItem = {
  id: string;
  label: string;
  url: string;
};

export type AvatarCatalog = {
  items: AvatarCatalogItem[];
};

export type CityVisibilityLevel =
  | "none"
  | "stale"
  | "live_ship"
  | "live_kontor"
  | "live_both";

export type CityShipInHarbor = {
  id: string;
  name: string;
};

export type GameCityView = {
  city: string;
  primary_good: string;
  visibility_level: CityVisibilityLevel;
  has_live_visibility: boolean;
  last_seen_day: number | null;
  days_stale: number | null;
  status_hint: string;
  markets: GameMarketItem[] | null;
  ships_in_harbor: CityShipInHarbor[] | null;
  latest_city_event_hint: string | null;
};

export type MarketTradeAction = {
  revision?: string;
  type: "buy" | "sell";
  city: string;
  good: string;
  qty: number;
  counterparty: "ship" | "private_storage";
  ship_id?: string;
};

export type TransferAction = {
  city: string;
  good: string;
  qty: number;
  direction: "ship_to_private" | "private_to_ship";
  ship_id?: string;
};

export type SetCourseAction = {
  destination_city: string;
  ship_id?: string;
};

export type GameEvent = {
  id: number;
  day: number;
  event_type: string;
  payload: Record<string, unknown>;
  created_at: string;
};

export type AssetCatalogShip = {
  build_days: number;
  id: string;
  name: string;
  capacity_total: number;
  max_per_good: number;
  capacity?: number;
  buy_price: number;
  sell_price: number;
};

export type AssetCatalogStorage = {
  build_days: number;
  level: number;
  capacity_total: number;
  max_per_good: number;
  capacity?: number;
  buy_price: number;
  sell_price: number;
};

export type AssetCatalog = {
  ships: AssetCatalogShip[];
  storages: AssetCatalogStorage[];
};

export type ShipBuyAction = {
  city: string;
  ship_class_id: string;
};

export type ShipSellAction = {
  city: string;
  ship_id: string;
};

export type StorageUpgradeAction = {
  city: string;
};

export type StorageSellAction = {
  city: string;
};

export type ConstructionOrder = {
  id: number;
  kind: "ship" | "storage";
  city: string;
  class_id?: string;
  level?: number;
  due_day: number;
  price: number;
};
export type MonthlyReport = {
  month: string;
  opening_cash: number;
  closing_cash: number;
  trade_income: number;
  trade_expenses: number;
  construction_expenses: number;
  asset_income: number;
  cash_surplus: number;
};
export type TradeQuote = {
  revision: string;
  total: number;
  unit_prices: number[];
  action: MarketTradeAction;
};
export type SaveSlot = {
  id: string;
  name: string;
  date: string;
  updated_at: string;
};
