import type { TradeEvent } from "../api-client/types";

export function EventTable({ events }: { events: TradeEvent[] }) {
  return (
    <section className="panel">
      <h2>Handelsprotokoll</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tag</th>
              <th>Typ</th>
              <th>Ware</th>
              <th>Menge</th>
              <th>Von</th>
              <th>Nach</th>
              <th>Preis</th>
              <th>PnL</th>
            </tr>
          </thead>
          <tbody>
            {events.slice(0, 100).map((e, idx) => (
              <tr key={`${e.day}-${idx}`}>
                <td>{e.day}</td>
                <td>{e.side}</td>
                <td>{e.good}</td>
                <td>{e.qty}</td>
                <td>{e.city_from}</td>
                <td>{e.city_to ?? "-"}</td>
                <td>{e.price.toFixed(2)}</td>
                <td>{e.pnl_delta.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
