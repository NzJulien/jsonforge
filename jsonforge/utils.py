"""Shared helpers: JSON file IO and terminal color output."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(data: Any, path: str, indent: int = 2) -> None:
    Path(path).write_text(json.dumps(data, indent=indent) + "\n", encoding="utf-8")


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2))
