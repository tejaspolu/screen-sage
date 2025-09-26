from __future__ import annotations

import time
from pathlib import Path

import typer
from rich import print

from .config import load_settings
from .pipeline import Pipeline
from .watcher import Watcher

app = typer.Typer(add_completion=False)


@app.command()
def analyze(path: str) -> None:
    """Analyze and triage a single image file."""
    settings = load_settings()
    pipeline = Pipeline(settings)
    result = pipeline.process_image(Path(path).expanduser().resolve())
    print({
        "moved_image_path": str(result.moved_image_path),
        "note_path": str(result.note_path),
    })


@app.command()
def watch(folder: str) -> None:
    """Watch the given folder for new screenshots and auto-triage them."""
    settings = load_settings()
    # Override watch_dir with user-provided folder
    settings.watch_dir = Path(folder).expanduser().resolve()
    watcher = Watcher(settings)
    watcher.start()
    print("[bold green]Watcher started.[/bold green] Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


def main() -> None:
    app()


if __name__ == "__main__":
    main()




