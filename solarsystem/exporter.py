"""HTML export of the Plotly orrery figure."""

from pathlib import Path
import plotly.graph_objects as go
from rich.console import Console
from rich.panel import Panel

_console = Console()


def save_html(
    fig: go.Figure,
    path: Path = Path("orrery.html"),
) -> None:
    """Export the Plotly figure to a self-contained HTML file."""
    if not isinstance(path, Path):
        raise TypeError(f"path must be a pathlib.Path, got {type(path)}")

    try:
        # 'cdn' keeps file small (~20 KB) vs 'inline' which embeds ~3 MB of Plotly JS
        fig.write_html(path, include_plotlyjs="cdn")
    except Exception as e:
        raise IOError(f"Failed to write HTML to {path}: {e}")

    size_kb = path.stat().st_size / 1024
    _console.print(Panel(
        f"[bold]{path.resolve()}[/bold]\n"
        f"Size: {size_kb:.1f} KB\n"
        "Open in any browser — no install needed",
        title="[bold green]Orrery exported[/bold green]",
    ))
