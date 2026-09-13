import type { GameShipState } from "../../src/api-client/types";
import {
  clampQty,
  inventoryTotal,
  resolveQty,
  shipCapacityTotal,
  shipMaxPerGood,
  storageCapacityTotal,
  storageMaxPerGood,
} from "../../src/features/game/model";

describe("game model helpers", () => {
  it("uses legacy capacity fields when new capacity fields are absent", () => {
    const ship = { capacity: 40 } as GameShipState;
    expect(shipCapacityTotal(ship)).toBe(40);
    expect(shipMaxPerGood(ship)).toBe(40);
    expect(storageCapacityTotal({ capacity: 80 })).toBe(80);
    expect(storageMaxPerGood({ capacity: 80 })).toBe(80);
  });

  it("prefers explicit total and per-good capacity fields", () => {
    const ship = {
      capacity: 40,
      capacity_total: 70,
      max_per_good: 35,
    } as GameShipState;
    expect(shipCapacityTotal(ship)).toBe(70);
    expect(shipMaxPerGood(ship)).toBe(35);
    expect(storageCapacityTotal({ capacity: 80, capacity_total: 140 })).toBe(
      140,
    );
    expect(storageMaxPerGood({ capacity_total: 140, max_per_good: 50 })).toBe(
      50,
    );
  });

  it("calculates inventory totals and clamps quantity modes", () => {
    expect(inventoryTotal({ Salz: 3, Fisch: 2, Holz: 0 })).toBe(5);
    expect(clampQty(10, 4)).toBe(4);
    expect(clampQty(2.9, 10)).toBe(2);
    expect(resolveQty("1", 20)).toBe(1);
    expect(resolveQty("10", 6)).toBe(6);
    expect(resolveQty("max", 17)).toBe(17);
    expect(resolveQty("10", 0)).toBe(0);
  });
});

import { money, label, dateAt } from "../../src/features/game/display";
it("formats integer money, technical labels and Gregorian dates", () => {
  expect(money(10985)).toBe("109,85 M");
  expect(label("Pelze")).toBe("Felle");
  expect(label("Luebeck")).toBe("Lübeck");
  expect(dateAt(31)).toBe("01. April 1400");
});
