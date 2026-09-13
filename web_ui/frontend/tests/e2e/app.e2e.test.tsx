import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";
import { vi } from "vitest";

import App from "../../src/App";

function wrap(ui: ReactNode) {
  window.history.replaceState({}, "", "/backtest");
  const qc = new QueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  );
}

const ok = (body: unknown) =>
  Promise.resolve(new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } }));

const err = (status: number, text: string) => Promise.resolve(new Response(text, { status }));


describe("E2E Kernpfade (UI-Integration)", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("Happy Path: Szenario waehlen, Run starten, KPI sichtbar", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/scenarios")) {
        return ok([{ id: "hanse_seed_v1", name: "Hanse", version: "1.0.0" }]);
      }
      if (url.includes("/api/v1/backtests?page=")) {
        return ok({ page: 1, page_size: 10, total: 0, items: [] });
      }
      if (url.includes("/api/v1/backtests/run")) {
        return ok({
          run_id: "r1",
          status: "completed",
          duration_ms: 10,
          summary: { roi: 0.1, pnl: 100, max_drawdown: 0.05, win_rate_trades: 0.6, turnover: 500 },
          equity_curve: [{ day: 1, equity: 10000 }],
          city_snapshots: [],
          trade_log: [],
          violations: [],
        });
      }
      return ok({});
    });

    wrap(<App />);
    expect(screen.queryByLabelText("Spielmodus Uebersicht")).not.toBeInTheDocument();
    await screen.findByRole("option", { name: /Hanse/ });
    fireEvent.click(screen.getByText("Backtest starten"));
    await screen.findByText("ROI");
    expect(fetchMock).toHaveBeenCalled();
  });

  it("Invalid Config: UI zeigt Validierungsfehler", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/scenarios")) {
        return ok([{ id: "hanse_seed_v1", name: "Hanse", version: "1.0.0" }]);
      }
      if (url.includes("/api/v1/backtests?page=")) {
        return ok({ page: 1, page_size: 10, total: 0, items: [] });
      }
      return ok({});
    });

    wrap(<App />);
    await screen.findByRole("option", { name: /Hanse/ });

    const start = screen.getByLabelText("Start Tag") as HTMLInputElement;
    const end = screen.getByLabelText("End Tag") as HTMLInputElement;
    fireEvent.change(start, { target: { value: "10" } });
    fireEvent.change(end, { target: { value: "9" } });
    fireEvent.click(screen.getByText("Backtest starten"));

    await screen.findByText(/End Tag muss groesser/);
  });

  it("Run-Historie: Detail-Link sichtbar und konsistent", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/scenarios")) {
        return ok([{ id: "hanse_seed_v1", name: "Hanse", version: "1.0.0" }]);
      }
      if (url.includes("/api/v1/backtests?page=")) {
        return ok({
          page: 1,
          page_size: 10,
          total: 1,
          items: [
            {
              run_id: "abc12345",
              scenario_id: "hanse_seed_v1",
              created_at: "2026-01-01T00:00:00Z",
              duration_ms: 12,
              summary: { roi: 0.1, pnl: 100, max_drawdown: 0.05, win_rate_trades: 0.6, turnover: 500 },
            },
          ],
        });
      }
      return err(404, "not found");
    });

    wrap(<App />);
    await waitFor(() => expect(screen.getByText("Einzelansicht")).toBeInTheDocument());
    expect(screen.getByText(/abc12345/)).toBeInTheDocument();
  });
});
