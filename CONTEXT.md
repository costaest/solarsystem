# solarsystem — project context for Claude

> Paste this file at the start of every new Claude session.
> Keep it updated as architectural decisions evolve.

---

## Developer profile

- **Name**: Alessandro Oliverio
- **Python level**: intermediate (learning by building)
- **OS**: macOS, MacBook Pro M1 (arm64)
- **Shell**: zsh
- **Editor**: to be decided
- **GitHub**: github.com/YOURUSERNAME/solarsystem

---

## Project goal

Build an interactive 3D orrery of the solar system that:
- Calculates **real planetary positions** using NASA JPL ephemerides via Astropy
- Renders a **standalone `orrery.html`** file (no server, no install for the viewer)
- Exposes a **Rich CLI** to generate snapshots, pick dates, and animate

The project is open source, intended for GitHub with a strong README and demo gif.

---

## Final interface decision

| Layer | Technology | Why |
|---|---|---|
| Computation | Astropy + NumPy | Real ephemerides, no approximations |
| Visualization | Plotly (go.Figure) | 3D interactive, exports to self-contained HTML |
| CLI | argparse + Rich | Clean terminal UX, progress bars, colored output |
| Output | Single `.html` file | Sharable with one double-click, no dependencies |

No web app. No Flask. No server. The HTML file contains everything inline.

---

## Astronomy & coordinate system — technical notes

### Ephemerides
- Using **NASA JPL DE432** (default in Astropy >= 5.0)
- More accurate alternative: DE440 — use `astropy.coordinates.solar_system_ephemeris.set('de440')` if needed
- Accuracy: arcsecond-level for all 8 planets over centuries

### Coordinate systems
- **Barycentric ICRS**: origin at solar system barycenter, aligned with ICRS (International Celestial Reference System). Used for internal calculations.
- **Heliocentric**: origin at Sun center. Used for rendering (Plotly scene has Sun at 0,0,0).
- Conversion: subtract Sun's barycentric position from each planet's barycentric position.
- All positions in **Astronomical Units (AU)**. 1 AU = 1.496 × 10¹¹ m = Earth–Sun mean distance.

### Key Astropy functions
```python
from astropy.coordinates import get_body_barycentric
from astropy.time import Time
import astropy.units as u

t = Time('2026-05-12', scale='utc')
pos = get_body_barycentric('mars', t)       # returns CartesianRepresentation in AU
x = pos.x.to(u.au).value                   # float in AU
```

### Time handling
- Always use `astropy.time.Time` objects, never raw datetime
- Scale: `utc` for user input, `tdb` internally (Barycentric Dynamical Time) for ephemeris queries
- Astropy converts automatically: `Time('2026-05-12', scale='utc')` is safe

### Orbital periods (days) — used for orbit path sampling
```
Mercury:    87.97    Venus:   224.70    Earth:   365.25    Mars:    686.97
Jupiter:  4332.59    Saturn: 10759.22   Uranus: 30688.50   Neptune: 60182.00
Moon:       27.32
```

### Planet sizes (relative, for rendering)
Actual radii in km → scaled logarithmically for visibility:
```
Sun: 695700   Mercury: 2439   Venus: 6051    Earth: 6371
Mars: 3389    Jupiter: 69911  Saturn: 58232  Uranus: 25362  Neptune: 24622
```
Use `log10(radius)` normalized to a render range of [3, 20] px.
Saturn's rings: ellipse with semi-major axis ~2.3× planet radius, opacity 0.4.

---

## Stack & dependencies

```
astropy >= 6.0       planetary positions, time handling, units
numpy >= 1.26        vector math, linspace for orbit sampling
plotly >= 5.20       3D scene, animation frames, HTML export
rich >= 13.0         CLI output (progress, panels, colored text)
```

No other dependencies. Do not add libraries without explicit discussion.
Python version: **3.11+** (uses match/case and tomllib if needed later).

---

## Project structure

```
solarsystem/
├── solarsystem/
│   ├── __init__.py
│   ├── config.py        planet metadata (name, color, radius, period, body_name)
│   ├── planets.py       get_positions(time) → dict[str, tuple[float,float,float]]
│   ├── orbits.py        get_orbit_paths(n_points) → dict[str, list[tuple]]
│   ├── renderer.py      build_figure(positions, orbits, date) → go.Figure
│   └── exporter.py      save_html(fig, path) → None
├── tests/
│   ├── __init__.py
│   ├── test_planets.py
│   └── test_orbits.py
├── assets/
│   └── (future: textures, screenshots)
├── docs/
│   └── (future: extended docs)
├── main.py              CLI entry point
├── requirements.txt
├── CONTEXT.md           ← this file
├── DECISIONS.md         architectural decisions log
├── README.md
└── LICENSE
```

---

## Module contracts

### `config.py`
```python
PLANETS: list[dict] = [
    {
        "name": "Mercury",
        "body_name": "mercury",   # name used in get_body_barycentric()
        "color": "#b0b0b0",
        "radius_km": 2439,
        "period_days": 87.97,
        "render_size": 4,         # computed via log scale
    },
    ...
]
SUN_COLOR = "#FFF176"
SUN_RENDER_SIZE = 18
BACKGROUND_COLOR = "#000000"
```

### `planets.py`
```python
def get_positions(time: Time) -> dict[str, tuple[float, float, float]]:
    """Return heliocentric X/Y/Z in AU for all planets at given time."""
```

### `orbits.py`
```python
def get_orbit_paths(n_points: int = 500) -> dict[str, list[tuple[float, float, float]]]:
    """Return heliocentric orbit path samples for all planets."""
```

### `renderer.py`
```python
def build_figure(
    positions: dict[str, tuple[float, float, float]],
    orbits: dict[str, list[tuple[float, float, float]]],
    date: str,
) -> go.Figure:
    """Build Plotly 3D figure. Sun at origin. Dark background."""
```

### `exporter.py`
```python
def save_html(fig: go.Figure, path: Path = Path("orrery.html")) -> None:
    """Export figure to self-contained HTML (include_plotlyjs='cdn')."""
```

### `main.py` CLI
```
python main.py now                        → snapshot of today → orrery.html
python main.py --date 2030-06-21          → snapshot of specific date
python main.py animate --days 365         → animated HTML with time slider
python main.py animate --days 365 --step 7  → 1 frame per week (faster)
```

---

## Rendering decisions

- **Coordinate system in Plotly**: X = ecliptic longitude direction, Y = perpendicular, Z = ecliptic north. Sun at (0, 0, 0).
- **Camera default**: slightly above the ecliptic plane (`eye = dict(x=0.5, y=0.5, z=1.8)`) to show orbital tilt
- **Orbit lines**: `go.Scatter3d` with `mode='lines'`, opacity 0.25, same color as planet
- **Planets**: `go.Scatter3d` with `mode='markers'`, marker size from config log scale
- **Tooltips**: name + distance from Sun in AU (2 decimal places) + current date
- **Animation**: `go.Figure(frames=[...])` with `updatemenus` play/pause button + `sliders` for date
- **HTML export**: `fig.write_html(path, include_plotlyjs='cdn')` — uses CDN to keep file small (~500KB vs 3MB)

---

## Code style — always follow these

- Type hints on every function signature
- One-line docstring on every function
- Functions max ~30 lines — split if longer
- No classes where plain functions suffice
- No `print()` anywhere — use `rich.console.Console` for all output
- No silent failures — raise descriptive exceptions
- All file paths as `pathlib.Path`, never raw strings
- Constants in `config.py`, never hardcoded in other modules

---

## Session management with Claude

### How to start a new session
Paste this at the top of every new Claude conversation:

```
Read CONTEXT.md below and continue development of the solarsystem project.
Current status: [describe what's done and what you want to build next]
Last working state: [which modules are complete and tested]

[paste full CONTEXT.md here]
```

### After each session, update this file:
- Move completed modules to the "Status" section below
- Add any new decisions to DECISIONS.md
- Note any bugs found but not yet fixed

### Module status
| Module | Status | Notes |
|---|---|---|
| config.py | not started | |
| planets.py | not started | |
| orbits.py | not started | |
| renderer.py | not started | |
| exporter.py | not started | |
| main.py | not started | |

### Known issues / open questions
- none yet

---

## What NOT to do (common LLM pitfalls to avoid)

- Do not use `ephem` or `skyfield` — we use Astropy only
- Do not use `matplotlib` for 3D — we use Plotly only
- Do not hardcode planet data outside `config.py`
- Do not use `datetime` module — use `astropy.time.Time` everywhere
- Do not add `flask`, `fastapi`, or any web framework
- Do not generate `orrery.html` paths with string concatenation — use `pathlib.Path`
- Do not approximate orbital positions with Kepler equations — use `get_body_barycentric`