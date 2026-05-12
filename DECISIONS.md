# solarsystem — architectural decisions log

> One entry per significant decision. Never delete entries — append only.
> Format: date, decision, reason, alternatives considered.

---

## 2026-05-12 — Ephemeris: DE432 (default Astropy)

**Decision**: use Astropy default ephemeris (DE432), with option to switch to DE440.
**Reason**: DE432 covers years 1950–2050 with arcsecond accuracy. Sufficient for this project.
**Alternative**: DE440 (more accurate, larger download). Upgrade path kept open via `solar_system_ephemeris.set()`.

---

## 2026-05-12 — Coordinate system: heliocentric for rendering

**Decision**: compute positions in barycentric ICRS internally, convert to heliocentric for Plotly scene.
**Reason**: Sun at (0,0,0) is more intuitive for a solar system visualization. Barycentric offset from Sun is negligible visually.
**Implementation**: subtract Sun's barycentric position from each body's barycentric position.

---

## 2026-05-12 — Planet sizes: logarithmic scale

**Decision**: render planet sizes using `log10(radius_km)` normalized to [3, 20] px range.
**Reason**: linear scale makes Jupiter 28× larger than Mercury, which hides inner planets entirely.
**Alternative**: fixed arbitrary sizes — rejected because it breaks educational accuracy.

---

## 2026-05-12 — Output format: standalone HTML via Plotly CDN

**Decision**: export with `include_plotlyjs='cdn'` instead of `'inline'`.
**Reason**: CDN keeps file size ~500KB vs ~3MB inline. Requires internet to view, acceptable tradeoff.
**Alternative**: `include_plotlyjs='inline'` for fully offline use. Can be made a CLI flag later: `--offline`.

---

## 2026-05-12 — Interface: Rich CLI + HTML output, no web app

**Decision**: no Flask/FastAPI, no web server. Pure CLI tool that generates a static HTML file.
**Reason**: simpler stack, zero deployment complexity, output is universally shareable.
**Future option**: GitHub Pages deploy of a generated file is possible without changing the core architecture.

---

## 2026-05-12 — Time handling: astropy.time.Time only

**Decision**: no Python `datetime` objects anywhere in the codebase.
**Reason**: Astropy Time handles UTC/TDB scale conversion automatically. Mixing datetime and Time objects causes subtle bugs.
**Rule**: user input (strings like "2026-05-12") → `Time(input, scale='utc')` at CLI boundary, then pass Time objects internally.

## 2026-05-12 — Ephemeris: switched from DE432s to DE440

Decision: use DE440 instead of DE432s.
Reason: DE432s covers only through 2050. Outer planet orbits 
(Saturn 29y, Neptune 165y, Pluto 248y) exceed that range from 
a 2025 reference date. DE440 covers 1550–2650.