from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class Settings:
    watch_dir: Path
    vision_model: str
    openai_api_key: Optional[str]

    def ensure_directories(self) -> None:
        # No-op: notes and triage directories are no longer managed here
        return


def expand(path_like: str) -> Path:
    return Path(os.path.expanduser(os.path.expandvars(path_like))).resolve()


def load_settings(config_path: Optional[Path] = None) -> Settings:
    load_dotenv(override=False)

    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        # Fallback to project root if running as a module
        if not config_path.exists():
            config_path = Path.cwd() / "config.yaml"

    config: dict = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    watch_dir = expand(os.getenv("WATCH_DIR", config.get("watch_dir", "~/Desktop")))
    vision_model = os.getenv("VISION_MODEL", config.get("vision_model", "gpt-4o"))
    openai_api_key = os.getenv("OPENAI_API_KEY")

    settings = Settings(
        watch_dir=watch_dir,
        vision_model=vision_model,
        openai_api_key=openai_api_key,
    )
    settings.ensure_directories()
    return settings




