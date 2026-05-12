"""Heliocentric planetary position queries using Astropy + JPL ephemerides."""

from astropy.coordinates import get_body_barycentric
from astropy.time import Time
import astropy.units as u
from solarsystem.config import PLANETS

# de440 covers 1550–2650, needed for outer planets whose full periods exceed de432s's 2050 limit
_EPHEMERIS = "de440"


def _barycentric_to_au_tuple(pos) -> tuple[float, float, float]:
    # Plain float (not numpy scalar) for JSON/Plotly compatibility
    return (
        float(pos.x.to(u.au).value),
        float(pos.y.to(u.au).value),
        float(pos.z.to(u.au).value),
    )


def get_positions(time: Time) -> dict[str, tuple[float, float, float]]:
    # time.scale is expected to be 'utc' for consistent ephemeris queries
    if not isinstance(time, Time):
        raise TypeError(f"time must be an astropy.time.Time object, got {type(time)}")

    # Subtract Sun's barycentric position to convert to heliocentric frame
    sun_pos = get_body_barycentric("sun", time, ephemeris=_EPHEMERIS)

    result: dict[str, tuple[float, float, float]] = {"Sun": (0.0, 0.0, 0.0)}

    for planet in PLANETS:
        try:
            bary_pos = get_body_barycentric(planet["body_name"], time, ephemeris=_EPHEMERIS)
        except Exception as e:
            raise RuntimeError(f"Failed to get position for {planet['name']}: {e}")

        helio = bary_pos - sun_pos
        result[planet["name"]] = _barycentric_to_au_tuple(helio)

    return result
