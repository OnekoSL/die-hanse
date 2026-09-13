import { useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "../../api-client/client";
import type { GameState } from "../../api-client/types";
export function useGameController() {
  const cache = useQueryClient();
  const [mode, setMode] = useState<"menu" | "game">("menu");
  const [city, setCity] = useState("Luebeck");
  const [tab, setTab] = useState("Handel");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const locked = useRef(false);
  const stateQuery = useQuery({
    queryKey: ["game-state"],
    queryFn: api.getActiveGameSession,
    retry: false,
  });
  const state = stateQuery.data;
  const saves = useQuery({ queryKey: ["game-saves"], queryFn: api.listSaves });
  const catalog = useQuery({
    queryKey: ["game-catalog"],
    queryFn: api.gameAssetsCatalog,
  });
  const cityQuery = useQuery({
    queryKey: ["game-city", city, state?.revision],
    queryFn: () => api.gameCityView(city),
    enabled: !!state && mode === "game",
    retry: false,
  });
  const events = useQuery({
    queryKey: ["game-events", state?.revision],
    queryFn: () => api.gameEvents(10000),
    enabled: !!state && mode === "game",
  });
  async function run<T>(
    operation: () => Promise<T>,
    done?: (value: T) => void,
  ) {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const value = await operation();
      done?.(value);
      await cache.invalidateQueries({ queryKey: ["game-saves"] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Aktion fehlgeschlagen.");
      if (e instanceof ApiError && e.status === 409)
        await cache.invalidateQueries({ queryKey: ["game-state"] });
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  function accept(value: GameState) {
    cache.setQueryData(["game-state"], value);
    setNotice("Automatisch gespeichert");
  }
  function command(operation: () => Promise<GameState>) {
    return run(operation, accept);
  }
  function enter(value: GameState) {
    accept(value);
    setCity(value.ship.current_city ?? value.ship.destination ?? "Luebeck");
    setTab("Handel");
    setMode("game");
  }
  return {
    state,
    saves: saves.data ?? [],
    catalog: catalog.data,
    cityView: cityQuery.data,
    events: events.data?.items ?? [],
    city,
    setCity,
    tab,
    setTab,
    mode,
    setMode,
    busy,
    error:
      error ||
      (cityQuery.error instanceof Error && mode === "game"
        ? cityQuery.error.message
        : "") ||
      (stateQuery.error instanceof ApiError && stateQuery.error.status !== 404
        ? stateQuery.error.message
        : "") ||
      (stateQuery.error && !(stateQuery.error instanceof ApiError)
        ? "Das Spiel ist nicht erreichbar. Bitte erneut versuchen."
        : "") ||
      (saves.error ? "Speicherplätze konnten nicht geladen werden." : "") ||
      (catalog.error ? "Ausbaukatalog konnte nicht geladen werden." : ""),
    loading: stateQuery.isLoading,
    notice,
    run,
    command,
    enter,
    newGame: () => run(api.newGameSession, enter),
    loadGame: (id: string) => run(() => api.loadGame(id), enter),
    saveGame: (name: string, id?: string) =>
      run(
        () => api.saveGame(name, id),
        () => setNotice("Spielstand gespeichert"),
      ),
    refresh: () => cache.invalidateQueries({ queryKey: ["game-state"] }),
  };
}
export type GameController = ReturnType<typeof useGameController>;
