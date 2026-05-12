"""Planet metadata and rendering constants for the solarsystem orrery."""

import math

# Tuned for visual clarity — not log-scaled, not scientifically accurate
_RENDER_SIZES: dict[str, int] = {
    "Mercury": 4, "Venus": 7, "Earth": 8, "Moon": 3,
    "Mars": 5, "Jupiter": 14, "Saturn": 12,
    "Uranus": 9, "Neptune": 9, "Pluto": 3,
}


def _compute_render_size(radius_km: int) -> int:
    # Kept for API compatibility; lookup by radius is resolved via PLANETS construction
    log_min = math.log10(2439)
    log_max = math.log10(69911)
    normalized = (math.log10(max(radius_km, 1)) - log_min) / (log_max - log_min)
    return int(round(max(3, min(20, 3 + normalized * 17))))


PLANETS: list[dict] = [
    {
        "name": "Mercury",
        "body_name": "mercury",  # astropy get_body_barycentric identifier
        "color": "#b5b5b5",
        "radius_km": 2439,
        "period_days": 87.97,
        "render_size": _RENDER_SIZES["Mercury"],
    },
    {
        "name": "Venus",
        "body_name": "venus",
        "color": "#e8cda0",
        "radius_km": 6051,
        "period_days": 224.70,
        "render_size": _RENDER_SIZES["Venus"],
    },
    {
        "name": "Earth",
        "body_name": "earth",
        "color": "#4fa3e0",
        "radius_km": 6371,
        "period_days": 365.25,
        "render_size": _RENDER_SIZES["Earth"],
    },
    {
        "name": "Moon",
        "body_name": "moon",
        "color": "#d0d0d0",
        "radius_km": 1737,
        "period_days": 27.32,  # sidereal period relative to Earth, not the Sun
        "render_size": _RENDER_SIZES["Moon"],
    },
    {
        "name": "Mars",
        "body_name": "mars",
        "color": "#c1440e",
        "radius_km": 3389,
        "period_days": 686.97,
        "render_size": _RENDER_SIZES["Mars"],
    },
    {
        "name": "Jupiter",
        "body_name": "jupiter",
        "color": "#c88b3a",
        "radius_km": 69911,
        "period_days": 4332.59,
        "render_size": _RENDER_SIZES["Jupiter"],
    },
    {
        "name": "Saturn",
        "body_name": "saturn",
        "color": "#e4d191",
        "radius_km": 58232,
        "period_days": 10759.22,
        "render_size": _RENDER_SIZES["Saturn"],
    },
    {
        "name": "Uranus",
        "body_name": "uranus",
        "color": "#7de8e8",
        "radius_km": 25362,
        "period_days": 30688.50,
        "render_size": _RENDER_SIZES["Uranus"],
    },
    {
        "name": "Neptune",
        "body_name": "neptune",
        "color": "#3f54ba",
        "radius_km": 24622,
        "period_days": 60182.00,
        "render_size": _RENDER_SIZES["Neptune"],
    },
    {
        "name": "Pluto",
        "body_name": "pluto",  # recognized by astropy via DE432 ephemeris
        "color": "#a89070",
        "radius_km": 1188,
        "period_days": 90560.00,
        "render_size": _RENDER_SIZES["Pluto"],
    },
]

SUN_COLOR: str = "#FFF176"
SUN_RENDER_SIZE: int = 10
BACKGROUND_COLOR: str = "#000000"
SATURN_RING_COLOR: str = "#c2a869"
SATURN_RING_SCALE: float = 2.3  # ring semi-major axis = 2.3 × planet render_size
