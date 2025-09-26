from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class NoteContext:
    title: str
    summary: str
    tasks: List[str]
    tags: List[str]
    sensitivity: bool
    image_path: Path
    image_rel_path: Path
    image_data_url: Optional[str] = None


def render_markdown(ctx: NoteContext) -> str:
    checkbox_lines = "\n".join([f"- [ ] {t}" for t in ctx.tasks]) if ctx.tasks else "(no tasks)"
    tags_line = ", ".join(ctx.tags) if ctx.tags else "untagged"
    sensitive = "yes" if ctx.sensitivity else "no"
    # Prefer data URL for robust rendering in Markdown previews; fallback to relative path
    if ctx.image_data_url:
        image_block = f"<img src=\"{ctx.image_data_url}\" alt=\"screenshot\" />"
    else:
        image_block = f"![screenshot]({ctx.image_rel_path})"
    return (
        f"# {ctx.title}\n\n"
        f"{ctx.summary}\n\n"
        f"{image_block}\n\n"
        f"## Tasks\n{checkbox_lines}\n\n"
        f"## Meta\n"
        f"- tags: {tags_line}\n"
        f"- sensitivity: {sensitive}\n"
        f"- captured: {datetime.now().isoformat(timespec='seconds')}\n"
    )


def write_note(notes_dir: Path, title: str, ctx: NoteContext) -> Path:
    filename = f"{ctx.image_path.stem}.md"
    note_path = notes_dir / filename
    note_path.parent.mkdir(parents=True, exist_ok=True)
    content = render_markdown(ctx)
    note_path.write_text(content, encoding="utf-8")
    return note_path




