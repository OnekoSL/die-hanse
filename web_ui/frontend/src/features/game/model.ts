import type { GameShipState } from "../../api-client/types";
type QuantityMode = "1" | "10" | "max";

export function shipCapacityTotal(ship: GameShipState): number {
  return ship.capacity_total ?? ship.capacity ?? 0;
}

export function shipMaxPerGood(ship: GameShipState): number {
  return ship.max_per_good ?? shipCapacityTotal(ship);
}

export function storageCapacityTotal(storage: {
  capacity_total?: number;
  capacity?: number;
}): number {
  return storage.capacity_total ?? storage.capacity ?? 0;
}

export function storageMaxPerGood(storage: {
  max_per_good?: number;
  capacity_total?: number;
  capacity?: number;
}): number {
  return storage.max_per_good ?? storageCapacityTotal(storage);
}

export function inventoryTotal(inventory: Record<string, number>): number {
  return Object.values(inventory).reduce((sum, qty) => sum + qty, 0);
}

export function clampQty(desiredQty: number, maxQty: number): number {
  if (maxQty <= 0) return 0;
  return Math.max(0, Math.min(maxQty, Math.floor(desiredQty)));
}

export function resolveQty(mode: QuantityMode, maxQty: number): number {
  if (mode === "max") return maxQty;
  return clampQty(mode === "10" ? 10 : 1, maxQty);
}
