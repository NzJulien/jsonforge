"""Structural diff for JSON-like Python objects (dict / list / scalars).

Produces a flat list of :class:`Change` records describing what was added,
removed, or changed between two JSON documents, each addressed by a
JSONPath-like string such as ``$.user.tags[1]``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Change:
    path: str
    kind: str  # "added" | "removed" | "changed"
    old: Any = None
    new: Any = None

    def __str__(self) -> str:
        if self.kind == "added":
            return f"+ {self.path} = {self.new!r}"
        if self.kind == "removed":
            return f"- {self.path} = {self.old!r}"
        return f"~ {self.path}: {self.old!r} -> {self.new!r}"


def diff(old: Any, new: Any, path: str = "$") -> list[Change]:
    """Compute the structural diff between ``old`` and ``new``."""
    changes: list[Change] = []
    _diff_node(old, new, path, changes)
    return changes


def _both_numeric(a: Any, b: Any) -> bool:
    numeric = (int, float)
    return (
        isinstance(a, numeric)
        and isinstance(b, numeric)
        and not isinstance(a, bool)
        and not isinstance(b, bool)
    )


def _diff_node(old: Any, new: Any, path: str, changes: list[Change]) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            child_path = f"{path}.{key}"
            if key not in old:
                changes.append(Change(child_path, "added", new=new[key]))
            elif key not in new:
                changes.append(Change(child_path, "removed", old=old[key]))
            else:
                _diff_node(old[key], new[key], child_path, changes)
        return

    if isinstance(old, list) and isinstance(new, list):
        for index in range(max(len(old), len(new))):
            child_path = f"{path}[{index}]"
            if index >= len(old):
                changes.append(Change(child_path, "added", new=new[index]))
            elif index >= len(new):
                changes.append(Change(child_path, "removed", old=old[index]))
            else:
                _diff_node(old[index], new[index], child_path, changes)
        return

    if type(old) is not type(new) and not _both_numeric(old, new):
        changes.append(Change(path, "changed", old, new))
        return

    if old != new:
        changes.append(Change(path, "changed", old, new))
