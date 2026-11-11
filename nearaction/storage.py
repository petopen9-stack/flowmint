"""Local durable storage under ~/.nearaction/"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def data_dir() -> Path:
    p = Path.home() / ".nearaction"
    p.mkdir(parents=True, exist_ok=True)
    return p


def actions_dir() -> Path:
    p = data_dir() / "actions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def receipts_dir() -> Path:
    p = data_dir() / "receipts"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
