import type {
  BacktestResult,
  TradeQuote,
  SaveSlot,
  BacktestRunRequest,
  AvatarCatalog,
  GameEvent,
  AssetCatalog,
  GameCityView,
  GameState,
  MarketTradeAction,
  NewGameSessionRequest,
  PaginatedRuns,
  ShipBuyAction,
  ShipSellAction,
  SetCourseAction,
  ScenarioDetail,
  ScenarioSummary,
  StorageSellAction,
  StorageUpgradeAction,
  TransferAction,
} from "./types";

const BASE_URL =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "http://127.0.0.1:18522");

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const payload = await res.json().catch(() => null);
    const detail = payload?.detail;
    throw new ApiError(
      res.status,
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? "Bitte Eingaben und Mengen prüfen."
          : `API Fehler: ${res.status}`,
    );
  }
  return (await res.json()) as T;
}

export const api = {
  gameQuote: (payload: MarketTradeAction) =>
    request<TradeQuote>("/api/v1/game/action/market-quote", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameSelectShip: (ship_id: string) =>
    request<GameState>("/api/v1/game/action/select-ship", {
      method: "POST",
      body: JSON.stringify({ ship_id }),
    }),
  listSaves: () => request<SaveSlot[]>("/api/v1/game/saves"),
  saveGame: (name: string, overwrite_id?: string) =>
    request<SaveSlot>("/api/v1/game/saves", {
      method: "POST",
      body: JSON.stringify({ name, overwrite_id }),
    }),
  loadGame: (id: string) =>
    request<GameState>(`/api/v1/game/saves/${encodeURIComponent(id)}/load`, {
      method: "POST",
    }),
  listScenarios: () => request<ScenarioSummary[]>("/api/v1/scenarios"),
  getScenario: (id: string) =>
    request<ScenarioDetail>(`/api/v1/scenarios/${id}`),
  runBacktest: (payload: BacktestRunRequest) =>
    request<BacktestResult>("/api/v1/backtests/run", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listRuns: (page = 1, pageSize = 20) =>
    request<PaginatedRuns>(
      `/api/v1/backtests?page=${page}&page_size=${pageSize}`,
    ),
  getRun: (runId: string) =>
    request<BacktestResult>(`/api/v1/backtests/${runId}`),
  newGameSession: (payload?: NewGameSessionRequest) =>
    request<GameState>("/api/v1/game/session/new", {
      method: "POST",
      body: JSON.stringify(payload ?? {}),
    }),
  gameAvatars: () => request<AvatarCatalog>("/api/v1/game/avatars"),
  getActiveGameSession: () => request<GameState>("/api/v1/game/session/active"),
  gameCityView: (city: string) =>
    request<GameCityView>(`/api/v1/game/city-view/${encodeURIComponent(city)}`),
  gameMarketTrade: (payload: MarketTradeAction) =>
    request<GameState>("/api/v1/game/action/market-trade", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameTransfer: (payload: TransferAction) =>
    request<GameState>("/api/v1/game/action/transfer", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameSetCourse: (payload: SetCourseAction) =>
    request<GameState>("/api/v1/game/action/set-course", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameAdvanceDay: () =>
    request<GameState>("/api/v1/game/action/advance-day", { method: "POST" }),
  gameAdvanceNextEvent: () =>
    request<GameState>("/api/v1/game/action/advance-next-event", {
      method: "POST",
    }),
  gameAssetsCatalog: () => request<AssetCatalog>("/api/v1/game/assets/catalog"),
  gameShipBuy: (payload: ShipBuyAction) =>
    request<GameState>("/api/v1/game/action/ship-buy", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameShipSell: (payload: ShipSellAction) =>
    request<GameState>("/api/v1/game/action/ship-sell", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameStorageUpgrade: (payload: StorageUpgradeAction) =>
    request<GameState>("/api/v1/game/action/storage-upgrade", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameStorageSell: (payload: StorageSellAction) =>
    request<GameState>("/api/v1/game/action/storage-sell", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  gameEvents: (limit = 25) =>
    request<{ items: GameEvent[] }>(`/api/v1/game/events?limit=${limit}`),
};
