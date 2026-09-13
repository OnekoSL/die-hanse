# Szenarioformat (JSON)

Pfad: `data/scenarios/*.json`

Pflichtfelder:
- `id`, `name`, `version`, `max_day`
- `goods: string[]`
- `ship: { start_city, capacity_total, max_per_good }`
  - Legacy-Fallback: `capacity` wird weiterhin akzeptiert (`capacity_total = capacity`).
  - Wenn `max_per_good` fehlt, gilt `max_per_good = capacity_total`.
- `cities[]` mit `goods`-Map je Ware:
  - `initial_stock`, `target_stock`, `base_price`, `demand_per_day`
  - optional: `production_per_day` (Default: `demand_per_day`)
- `routes[]`: `{ from, to, days }`

Hinweise:
- Tagesdynamik Backtest: `stock = max(0, stock + production_per_day - demand_per_day)`.
- Wenn `production_per_day` fehlt, wird intern `production_per_day = demand_per_day` gesetzt.
- Negative `production_per_day` Werte werden auf `0` geklemmt und als `violation` protokolliert.
