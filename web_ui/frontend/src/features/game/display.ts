export function money(value: number): string {
  return (
    (value / 100).toLocaleString("de-DE", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + " M"
  );
}
export function label(value: string): string {
  return (
    (
      {
        Luebeck: "Lübeck",
        Bruegge: "Brügge",
        Pelze: "Felle",
        grosse_kogge: "Große Kogge",
        kogge_standard: "Standardkogge",
        fernhaendler: "Fernhändler",
      } as Record<string, string>
    )[value] ?? value
  );
}
export function dateAt(day: number): string {
  const d = new Date(Date.UTC(1400, 2, 1 + day));
  return d.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}
