from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from openai import OpenAI
from openai import RateLimitError

from .config import Settings
from .utils import image_to_data_url


@dataclass
class AnalysisResult:
    title: str
    summary: str
    tasks: List[str]
    tags: List[str]
    sensitivity: bool


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "tasks": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "string"}},
        "sensitivity": {"type": "boolean"},
    },
    "required": ["title", "summary", "tasks", "tags", "sensitivity"],
    "additionalProperties": False,
}


PROMPT = (
    "You are an AI assistant that analyzes a screenshot and returns ONLY valid JSON.\n"
    "Follow this JSON schema strictly: {schema}.\n"
    "Return concise, human-meaningful fields.\n"
    "- title: 3-8 words summarizing the screenshot's purpose.\n"
    "- summary: 1-3 sentences capturing key details and context.\n"
    "- tasks: actionable next steps as short imperatives, 0-6 items.\n"
    "- tags: 2-6 short lowercase tags (e.g., 'bug', 'ui', 'finance').\n"
    "- sensitivity: true if screenshot includes private or identifying info.\n"
    "Output JSON only with no markdown or extra commentary."
)


class Analyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze_image(self, image_path: Path) -> AnalysisResult:
        data_url = image_to_data_url(image_path)
        prompt = PROMPT.format(schema=json.dumps(JSON_SCHEMA))

        # Basic retry for transient rate limits
        last_exc = None
        for _ in range(5):
            try:
                response = self.client.responses.create(
                    model=self.settings.vision_model,
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": data_url},
                            ],
                        }
                    ],
                )
                text = response.output_text or ""
                data = self._parse_json_strict(text)
                return AnalysisResult(
                    title=data.get("title", "Screenshot"),
                    summary=data.get("summary", ""),
                    tasks=[t for t in data.get("tasks", []) if isinstance(t, str)],
                    tags=[t for t in data.get("tags", []) if isinstance(t, str)],
                    sensitivity=bool(data.get("sensitivity", False)),
                )
            except RateLimitError as e:
                last_exc = e
            except Exception as e:
                last_exc = e
            import time as _t
            _t.sleep(0.4)
        raise last_exc

    @staticmethod
    def _parse_json_strict(text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            # Try to extract the first {...} block
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                snippet = match.group(0)
                try:
                    return json.loads(snippet)
                except Exception:
                    pass
        # Fallback defaults
        return {"title": "Screenshot", "summary": "", "tasks": [], "tags": [], "sensitivity": False}




