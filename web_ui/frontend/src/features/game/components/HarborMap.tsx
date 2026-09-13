import { label } from "../display";
const points: Record<string, [number, number]> = {
  London: [11, 79],
  Bruegge: [23, 86],
  Hamburg: [40, 71],
  Luebeck: [49, 63],
  Rostock: [59, 73],
  Danzig: [72, 78],
  Riga: [83, 49],
  Visby: [67, 42],
  Stockholm: [65, 21],
  Bergen: [31, 17],
  Nowgorod: [92, 30],
};
export function HarborMap({
  cities,
  selected,
  onSelect,
  disabled,
}: {
  cities: string[];
  selected: string;
  onSelect: (city: string) => void;
  disabled: boolean;
}) {
  return (
    <section className="chart" aria-label="Hafenkarte">
      <svg viewBox="0 0 800 420" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M40 0H0V40"
              fill="none"
              stroke="#43696b"
              strokeWidth=".5"
            />
          </pattern>
        </defs>
        <rect width="800" height="420" fill="url(#grid)" />
        <path
          d="M0 250L30 190L76 200L95 270L79 335L20 365L0 350Z M140 420L178 356L266 336L321 310L372 319L450 350L556 370L650 303L690 235L744 208L800 220V420Z M210 0L220 82L260 147L322 198L377 171L396 123L450 156L480 96L525 55L543 0Z M800 0H612L620 60L683 143L735 143L800 184Z"
          fill="#35534e"
          stroke="#91a991"
          strokeWidth="1.5"
        />
        <path
          d="M392 265Q405 163 520 89M392 265Q260 260 88 332M520 89Q577 122 664 206"
          stroke="#b7a471"
          opacity=".5"
          strokeDasharray="5 7"
          fill="none"
        />
        <text x="160" y="245" fill="#a8c0bc" letterSpacing="8" fontSize="16">
          NORDSEE
        </text>
        <text x="489" y="257" fill="#a8c0bc" letterSpacing="8" fontSize="16">
          OSTSEE
        </text>
        <text x="730" y="390" fill="#c6b585" fontSize="26">
          ✧ N
        </text>
      </svg>
      {cities.map((city) => (
        <button
          key={city}
          className={`port ${selected === city ? "selected" : ""}`}
          style={{ left: `${points[city][0]}%`, top: `${points[city][1]}%` }}
          aria-pressed={selected === city}
          onClick={() => onSelect(city)}
          disabled={disabled}
        >
          {label(city)}
        </button>
      ))}
      <span className="map-caption">
        Handelsgebiet · schematische Darstellung
      </span>
    </section>
  );
}
