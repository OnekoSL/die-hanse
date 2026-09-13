import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import App from "../../src/App";
import { api, ApiError } from "../../src/api-client/client";
import type {
  AssetCatalog,
  GameCityView,
  GameState,
} from "../../src/api-client/types";
import fixture from "../fixtures/game.json";

let state: GameState;
function renderApp() {
  const cache = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={cache}>
      <MemoryRouter>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}
async function enter() {
  renderApp();
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Fortsetzen" })).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Fortsetzen" }));
  await screen.findByRole("heading", { name: "Waren handeln" });
}
beforeEach(() => {
  state = structuredClone(fixture.state) as GameState;
  vi.spyOn(api, "getActiveGameSession").mockImplementation(async () => state);
  vi.spyOn(api, "newGameSession").mockImplementation(async () => state);
  vi.spyOn(api, "listSaves").mockResolvedValue([]);
  vi.spyOn(api, "gameAssetsCatalog").mockResolvedValue(
    fixture.catalog as AssetCatalog,
  );
  vi.spyOn(api, "gameCityView").mockImplementation(async (city) =>
    city === "Luebeck"
      ? (fixture.city as GameCityView)
      : {
          city,
          primary_good: state.city_primary_goods[city],
          visibility_level: "none",
          has_live_visibility: false,
          last_seen_day: null,
          days_stale: null,
          status_hint: "Unbekannt",
          markets: null,
          ships_in_harbor: null,
          latest_city_event_hint: null,
        },
  );
  vi.spyOn(api, "gameEvents").mockResolvedValue({ items: [] });
});
afterEach(() => vi.restoreAllMocks());

it("opens the game menu and starts a new game with eleven accessible ports", async () => {
  vi.mocked(api.getActiveGameSession).mockRejectedValue(
    new ApiError(404, "Kein Spielstand"),
  );
  renderApp();
  expect(
    screen.getByRole("heading", { name: "Die Hanse" }),
  ).toBeInTheDocument();
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Neues Spiel" })).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Neues Spiel" }));
  await screen.findByRole("heading", { name: "Waren handeln" });
  expect(
    within(screen.getByRole("region", { name: "Hafenkarte" })).getAllByRole(
      "button",
    ),
  ).toHaveLength(11);
  expect(screen.getByText("1.000,00 M")).toBeInTheDocument();
  expect(screen.getByText("01. März 1400")).toBeInTheDocument();
});

it("quotes before executing and sends the reviewed amount and revision", async () => {
  const quote = vi
    .spyOn(api, "gameQuote")
    .mockImplementation(async (action) => ({
      action,
      revision: state.revision,
      total: 10985,
      unit_prices: [10985],
    }));
  const trade = vi
    .spyOn(api, "gameMarketTrade")
    .mockImplementation(async () => ({
      ...state,
      cash: 89015,
      revision: "next",
    }));
  await enter();
  fireEvent.change(screen.getByLabelText("Menge"), { target: { value: "10" } });
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Handelsvorschau" }),
    ).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Handelsvorschau" }));
  await screen.findByText("109,85 M");
  expect(trade).not.toHaveBeenCalled();
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Handel bestätigen" }),
    ).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Handel bestätigen" }));
  await screen.findByText("890,15 M");
  expect(quote.mock.calls[0][0].qty).toBe(10);
  expect(trade.mock.calls[0][0]).toMatchObject({
    qty: 10,
    revision: state.revision,
    city: "Luebeck",
    good: "Salz",
  });
});

it("discards a quote after changing quantity", async () => {
  vi.spyOn(api, "gameQuote").mockImplementation(async (action) => ({
    action,
    revision: state.revision,
    total: 1061,
    unit_prices: [1061],
  }));
  await enter();
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Handelsvorschau" }),
    ).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Handelsvorschau" }));
  await screen.findByRole("button", { name: "Handel bestätigen" });
  fireEvent.change(screen.getByLabelText("Menge"), { target: { value: "2" } });
  await waitFor(() =>
    expect(
      screen.queryByRole("button", { name: "Handel bestätigen" }),
    ).not.toBeInTheDocument(),
  );
});

it("keeps map and harbor list synchronized and blocks remote ship trade", async () => {
  await enter();
  fireEvent.click(
    within(screen.getByRole("region", { name: "Hafenkarte" })).getByRole(
      "button",
      { name: "Riga" },
    ),
  );
  expect(screen.getByLabelText("Hafen ansehen")).toHaveValue("Riga");
  await screen.findByText("Keine aktuelle Marktpräsenz in diesem Hafen.");
  expect(
    screen.getByRole("button", { name: "Handelsvorschau" }),
  ).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Hafen ansehen"), {
    target: { value: "Luebeck" },
  });
  expect(
    within(screen.getByRole("region", { name: "Hafenkarte" })).getByRole(
      "button",
      { name: "Lübeck" },
    ),
  ).toHaveAttribute("aria-pressed", "true");
});

it("shows a rejected trade in German without changing the balance", async () => {
  vi.spyOn(api, "gameQuote").mockRejectedValue(
    new ApiError(422, "Nicht genug Mark"),
  );
  await enter();
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Handelsvorschau" }),
    ).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole("button", { name: "Handelsvorschau" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Nicht genug Mark",
  );
  expect(screen.getByText("1.000,00 M")).toBeInTheDocument();
});

it("creates named saves without implicitly overwriting slots", async () => {
  const save = vi.spyOn(api, "saveGame").mockResolvedValue({
    id: "s1",
    name: "Meine Flotte",
    date: state.date,
    updated_at: "2026-09-13T00:00:00",
  });
  await enter();
  fireEvent.click(screen.getByRole("button", { name: "Spielstände" }));
  fireEvent.change(screen.getByLabelText("Name des Spielstands"), {
    target: { value: "Meine Flotte" },
  });
  fireEvent.click(
    screen.getByRole("button", { name: "Neuen Speicherplatz anlegen" }),
  );
  await waitFor(() =>
    expect(save).toHaveBeenCalledWith("Meine Flotte", undefined),
  );
});

it("shows arrival and ship construction dates", async () => {
  await enter();
  expect(
    screen.getByText("5 Tage · Ankunft 06. März 1400"),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Flotte" }));
  await screen.findByText("Verfügbar am 08. März 1400");
  expect(
    screen.getByRole("button", { name: "Kostenpflichtig bestellen" }),
  ).toBeEnabled();
  expect(screen.getByRole("button", { name: /Verkaufen ·/ })).toBeDisabled();
});

it("shows connection errors instead of treating them as a missing save", async () => {
  vi.mocked(api.getActiveGameSession).mockRejectedValue(
    new TypeError("fetch failed"),
  );
  renderApp();
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Das Spiel ist nicht erreichbar",
  );
});

it("selects a market row and shows its prices and inventory beside the complete cargo", async () => {
  state.ship.cargo.Salz = 20;
  await enter();
  const manifest = screen.getByRole("region", { name: "Schiffsladung" });
  expect(
    within(manifest).getByRole("button", { name: "Salz 20 Last" }),
  ).toBeInTheDocument();
  expect(
    within(manifest).queryByRole("button", { name: /Holz/ }),
  ).not.toBeInTheDocument();
  const wood = await screen.findByRole("row", { name: /^Holz / });
  fireEvent.click(within(wood).getAllByRole("cell")[0]);
  const details = screen.getByRole("region", { name: "Warendetails" });
  expect(
    within(details).getByRole("heading", { name: "Holz" }),
  ).toBeInTheDocument();
  expect(within(details).getByLabelText("Ware")).toHaveValue("Holz");
  expect(details).toHaveTextContent("An Bord · Kogge I0 Last");
  const woodMarket = fixture.city.markets.find((m) => m.good === "Holz")!;
  const price = new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(woodMarket.stadt_verkaufspreis / 100);
  expect(details).toHaveTextContent(price);
  fireEvent.click(
    within(manifest).getByRole("button", { name: "Salz 20 Last" }),
  );
  expect(
    within(details).getByRole("heading", { name: "Salz" }),
  ).toBeInTheDocument();
  expect(details).toHaveTextContent("An Bord · Kogge I20 Last");
});

it("explains an empty hold and prevents a sale of absent goods", async () => {
  await enter();
  expect(
    screen.getByRole("region", { name: "Schiffsladung" }),
  ).toHaveTextContent("Das Schiff ist leer");
  fireEvent.change(screen.getByLabelText("Aktion"), {
    target: { value: "sell" },
  });
  await screen.findByText("Nur 0 Last Salz an Bord verfügbar.");
  expect(
    screen.getByRole("button", { name: "Handelsvorschau" }),
  ).toBeDisabled();
});

it("marks old prices in the selected commodity overview", async () => {
  vi.mocked(api.gameCityView).mockResolvedValue({
    ...fixture.city,
    visibility_level: "stale",
    has_live_visibility: false,
    days_stale: 5,
  } as GameCityView);
  await enter();
  await waitFor(() =>
    expect(
      screen.getByRole("region", { name: "Warendetails" }),
    ).toHaveTextContent("Letzter Marktbericht · vor 5 Tagen"),
  );
  expect(
    screen.getByRole("button", { name: "Handelsvorschau" }),
  ).toBeDisabled();
});
