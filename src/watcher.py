from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileMovedEvent,
    FileModifiedEvent,
)
from watchdog.observers import Observer

from .config import Settings
from .pipeline import Pipeline


class ScreenshotEventHandler(FileSystemEventHandler):
    def __init__(self, settings: Settings, pipeline: Pipeline) -> None:
        super().__init__()
        self.settings = settings
        self.pipeline = pipeline
        self._inflight: set[str] = set()
        self._processed: set[str] = set()

    @staticmethod
    def _is_temp_dotfile(path: Path) -> bool:
        # macOS may create a temporary hidden file (name starts with '.') before renaming
        return path.name.startswith('.')

    @staticmethod
    def _has_sidecar_triaged(path: Path) -> bool:
        sidecar = path.parent / f".{path.name}.triaged"
        return sidecar.exists()

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._is_temp_dotfile(path):
            # Ignore temp hidden files; the final file will arrive via moved/modified
            return
        if str(path) in self._processed:
            return
        if self._has_sidecar_triaged(path):
            return
        if not self.pipeline.is_supported(path):
            return
        # Only log creates; macOS screenshots commonly finalize via a move
        print(f"[watcher] created: {path}")

    def on_moved(self, event: FileMovedEvent) -> None:
        if event.is_directory:
            return
        dest = Path(event.dest_path)
        if self._is_temp_dotfile(dest):
            return
        if str(dest) in self._processed:
            return
        if self._has_sidecar_triaged(dest):
            return
        if not self.pipeline.is_supported(dest):
            return
        print(f"[watcher] moved: {event.src_path} -> {event.dest_path}")
        self._spawn(dest)

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if self._is_temp_dotfile(path):
            return
        if str(path) in self._processed:
            return
        if self._has_sidecar_triaged(path):
            return
        if not self.pipeline.is_supported(path):
            return
        # Modified fires multiple times; rely on stability check inside pipeline
        print(f"[watcher] modified: {path}")

    def _spawn(self, path: Path) -> None:
        key = str(path)
        if key in self._inflight:
            return
        self._inflight.add(key)
        # Process in a thread so the handler returns quickly
        threading.Thread(target=self._process_safe, args=(path,), daemon=True).start()

    def _process_safe(self, path: Path) -> None:
        try:
            result = self.pipeline.process_image(path)
            # Mark processed by both original and final paths
            self._processed.add(str(path))
            self._processed.add(str(result.moved_image_path))
            print(f"[watcher] processed: {path}")
        except Exception as e:
            import traceback
            print(f"[watcher] error processing {path}: {e}")
            traceback.print_exc()
        finally:
            self._inflight.discard(str(path))


class Watcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pipeline = Pipeline(settings)
        self.observer: Optional[Observer] = None

    def start(self) -> None:
        handler = ScreenshotEventHandler(self.settings, self.pipeline)
        observer = Observer()
        observer.schedule(handler, str(self.settings.watch_dir), recursive=False)
        observer.start()
        self.observer = observer
        print(f"[watcher] watching: {self.settings.watch_dir}")

    def stop(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        


