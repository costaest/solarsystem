"""Orbital path sampling for all solar system bodies."""

from astropy.time import Time
import numpy as np
from rich.progress import track
from solarsystem.config import PLANETS
from solarsystem.planets import get_positions


def _sample_orbit(
    body_name: str,
    period_days: float,
    reference_time: Time,
    n_points: int,
) -> list[tuple[float, float, float]]:
    path: list[tuple[float, float, float]] = []
    # JD arithmetic avoids calendar edge cases (month boundaries, leap years, etc.)
    for offset in np.linspace(0, period_days, n_points):
        t = Time(reference_time.jd + offset, format="jd", scale="utc")
        positions = get_positions(t)
        path.append(positions[body_name])
    return path


def get_orbit_paths(
    n_points: int = 500,
    reference_time: Time | None = None,
) -> dict[str, list[tuple[float, float, float]]]:
    # reference_time is the start of the orbit sample window
    if reference_time is None:
        reference_time = Time.now()

    result: dict[str, list[tuple[float, float, float]]] = {}

    # Wrap outer (per-body) loop so each progress step represents one full orbit sampled
    for planet in track(PLANETS, description="Sampling orbits..."):
        result[planet["name"]] = _sample_orbit(
            body_name=planet["name"],
            period_days=planet["period_days"],
            reference_time=reference_time,
            n_points=n_points,
        )

    return result
