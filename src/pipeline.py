from __future__ import annotations

import shutil
from dataclasses import dataclass
import time
import os
from pathlib import Path

from .analyzer import Analyzer
from .config import Settings
from .note_writer import NoteContext, write_note
from .utils import ensure_unique_path, slugify, timestamp_for_filename, wait_for_file_stable, image_to_data_url


SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".gif"}


@dataclass
class ProcessedResult:
    moved_image_path: Path
    note_path: Path


class Pipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.analyzer = Analyzer(settings)

    def is_supported(self, path: Path) -> bool:
        return path.suffix.lower() in SUPPORTED_EXTS

    def process_image(self, image_path: Path) -> ProcessedResult:
        if not self.is_supported(image_path):
            raise ValueError(f"Unsupported image type: {image_path.suffix}")

        # Wait until the file exists and stops changing size
        if not wait_for_file_stable(image_path):
            # If the file never became stable (e.g., renamed away), raise for caller to handle
            raise FileNotFoundError(f"File not stable or missing: {image_path}")

        # Double-check existence right before operating on it
        if not image_path.exists():
            raise FileNotFoundError(f"File missing before processing: {image_path}")

        # Analyze exactly once; downstream logic must not re-trigger analysis
        analysis = self.analyzer.analyze_image(image_path)
        slug = slugify(analysis.title)
        # Rename in-place without timestamp prefix
        new_name = f"{slug}{image_path.suffix.lower()}"
        target = ensure_unique_path(image_path.parent / new_name)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Robust in-place rename with retries; if source vanishes (macOS rename race),
        # attempt to locate the most recent matching image in the same folder.
        moved = None
        last_err: Exception | None = None
        for _ in range(20):  # ~4s total
            try:
                if image_path.exists():
                    moved = shutil.move(str(image_path), str(target))
                    break
                else:
                    # Recover: find most recent non-hidden image with same extension
                    parent = target.parent
                    candidates = [
                        p for p in parent.iterdir()
                        if p.is_file() and (not p.name.startswith('.')) and p.suffix.lower() == target.suffix.lower()
                    ]
                    if candidates:
                        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                        alt = candidates[0]
                        if alt != target:
                            moved = shutil.move(str(alt), str(target))
                            break
            except FileNotFoundError as e:
                last_err = e
            except PermissionError as e:
                last_err = e
            time.sleep(0.2)
        if moved is None:
            # If still not moved, raise with context
            raise FileNotFoundError(f"Could not rename image; last error: {last_err}")
        moved_path = Path(moved)
        # Create a hidden sidecar to indicate this file has been triaged
        sidecar = moved_path.parent / f".{moved_path.name}.triaged"
        try:
            sidecar.write_text("ok", encoding="utf-8")
        except Exception:
            pass
        try:
            os.chmod(moved_path, 0o644)
        except Exception:
            pass

        # Notes directory lives under the watched screenshots folder
        notes_dir = moved_path.parent / "Screenshot Notes"
        # Compute relative path from the notes directory to the image (for markdown)
        try:
            rel_image_path = os.path.relpath(moved_path, notes_dir)
        except Exception:
            # Fallback to just the filename if relative fails
            rel_image_path = moved_path.name

        # Build note context; include data URL for robust rendering
        note_ctx = NoteContext(
            title=analysis.title,
            summary=analysis.summary,
            tasks=analysis.tasks,
            tags=analysis.tags,
            sensitivity=analysis.sensitivity,
            image_path=moved_path,
            image_rel_path=Path(rel_image_path),
            image_data_url=image_to_data_url(moved_path),
        )
        # Write note under "Screenshot Notes" named after the image filename
        note_path = write_note(notes_dir, analysis.title, note_ctx)

        return ProcessedResult(moved_image_path=moved_path, note_path=note_path)




