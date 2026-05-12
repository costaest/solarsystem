"""CLI entry point for the solarsystem orrery."""

import argparse
from pathlib import Path
from astropy.time import Time
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import plotly.graph_objects as go
from solarsystem.config import PLANETS
from solarsystem.planets import get_positions
from solarsystem.orbits import get_orbit_paths
from solarsystem.renderer import build_figure
from solarsystem.exporter import save_html

_console = Console()


def _parse_date(date_str: str) -> Time:
    """Parse a YYYY-MM-DD string into an Astropy Time object."""
    try:
        return Time(date_str, scale="utc")
    except Exception:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def _make_frame(date_str: str, t: Time, orbits: dict) -> go.Frame:
    """Build a single animation frame for the given date."""
    positions = get_positions(t)
    # Only update planet marker traces — orbit lines are static in the base figure
    n_static = 1 + len(PLANETS)  # 1 Sun + len(PLANETS) orbit traces
    data = [
        go.Scatter3d(
            x=[positions[p["name"]][0]],
            y=[positions[p["name"]][1]],
            z=[positions[p["name"]][2]],
            mode="markers",
            marker=dict(size=p["render_size"], color=p["color"], symbol="circle"),
        )
        for p in PLANETS
    ]
    traces = list(range(n_static, n_static + len(PLANETS)))
    return go.Frame(data=data, name=date_str, traces=traces)


def _add_animation_controls(fig: go.Figure, frames: list[go.Frame]) -> None:
    """Add play/pause buttons and a date slider to the figure layout."""
    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=0, x=0.5, xanchor="center",
            buttons=[
                dict(label="Play", method="animate",
                     args=[None, {"frame": {"duration": 100}, "fromcurrent": True}]),
                dict(label="Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
            ],
        )],
        sliders=[dict(
            steps=[
                dict(method="animate", args=[[f.name], {"mode": "immediate"}], label=f.name)
                for f in frames
            ],
            transition=dict(duration=0),
            x=0.1, len=0.9, y=0,
        )],
    )


def _build_snapshot(args: argparse.Namespace) -> None:
    """Run the snapshot pipeline."""
    if args.date:
        date_str = args.date
        t = _parse_date(date_str)
    else:
        # Time.now() returns current UTC time as an Astropy Time object
        t = Time.now()
        date_str = t.iso[:10]
    _console.print(Panel(f"Generating snapshot for {date_str}..."))
    orbits = get_orbit_paths(n_points=args.points, reference_time=t)
    positions = get_positions(t)
    fig = build_figure(positions, orbits, date_str)
    save_html(fig, Path(args.output))


def _build_animate(args: argparse.Namespace) -> None:
    """Run the animation pipeline."""
    # Time.now() returns current UTC time as an Astropy Time object
    reference_time = Time.now()
    # get_orbit_paths called once outside the frame loop for performance
    orbits = get_orbit_paths(n_points=args.points, reference_time=reference_time)
    day_offsets = list(range(0, args.days + 1, args.step))
    frames = [
        _make_frame(
            Time(reference_time.jd + offset, format="jd", scale="utc").iso[:10],
            Time(reference_time.jd + offset, format="jd", scale="utc"),
            orbits,
        )
        for offset in track(day_offsets, description="Building frames...")
    ]
    first_t = _parse_date(frames[0].name)
    positions = get_positions(first_t)
    fig = build_figure(positions, orbits, frames[0].name)
    fig.frames = frames
    _add_animation_controls(fig, frames)
    save_html(fig, Path(args.output))


def main() -> None:
    """Parse CLI arguments and dispatch to the correct pipeline."""
    parser = argparse.ArgumentParser(description="Solar system orrery generator.")
    parser.set_defaults(command="snapshot", date=None, output="orrery.html", points=500)
    parser.add_argument("--date", help="Date in YYYY-MM-DD format.")
    parser.add_argument("--output", default="orrery.html", help="Output HTML file path.")
    parser.add_argument("--points", type=int, default=500, help="Orbit sample points.")

    subparsers = parser.add_subparsers(dest="command")

    now_p = subparsers.add_parser("now", help="Snapshot for the current date.")
    now_p.set_defaults(date=None, output="orrery.html", points=500)
    now_p.add_argument("--date", help="Date in YYYY-MM-DD format.")
    now_p.add_argument("--output", default="orrery.html", help="Output HTML file path.")
    now_p.add_argument("--points", type=int, default=500, help="Orbit sample points.")

    animate_p = subparsers.add_parser("animate", help="Build animated orrery.")
    animate_p.add_argument("--days", type=int, required=True, help="Total days to animate.")
    animate_p.add_argument("--step", type=int, default=1, help="Days between frames.")
    animate_p.add_argument("--output", default="orrery.html", help="Output HTML file path.")
    animate_p.add_argument("--points", type=int, default=500, help="Orbit sample points.")

    args = parser.parse_args()
    try:
        if args.command == "animate":
            _build_animate(args)
        else:
            _build_snapshot(args)
    except Exception as e:
        _console.print(Panel(f"[bold red]Error:[/bold red] {e}", title="[red]Failed[/red]"))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
