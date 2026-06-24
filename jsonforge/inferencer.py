"""Schema inference engine.

Derives a JSON Schema (draft-07 compatible) from one or more sample JSON
documents. When given multiple samples, fields that are not present in
every sample are correctly marked as optional, and fields whose values
vary in type across samples are represented as a type union.
"""
from __future__ import annotations

from typing import Any, Iterable


def _infer_type(value: Any) -> str:
    """Map a Python value to its JSON Schema primitive type name."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _merge_types(types_seen: Iterable[str]) -> Any:
    """Collapse a set of observed type names into a schema 'type' value.

    ``integer`` is absorbed into ``number`` when both appear, since JSON
    Schema treats integers as a subset of numbers. A single remaining type
    is returned as a plain string; multiple types are returned as a sorted
    list (a type union).
    """
    types = set(types_seen)
    if "integer" in types and "number" in types:
        types.discard("integer")
    if len(types) == 1:
        return next(iter(types))
    return sorted(types)


def _infer_node(values: list[Any]) -> dict:
    """Infer a schema node from every sample value seen at one JSON path."""
    types_seen = {_infer_type(v) for v in values}
    schema: dict[str, Any] = {"type": _merge_types(types_seen)}

    object_samples = [v for v in values if isinstance(v, dict)]
    array_samples = [v for v in values if isinstance(v, list)]

    if object_samples:
        schema.update(_infer_object(object_samples))
    if array_samples:
        schema.update(_infer_array(array_samples))

    return schema


def _infer_object(samples: list[dict]) -> dict:
    all_keys: set[str] = set()
    for sample in samples:
        all_keys.update(sample.keys())

    properties: dict[str, Any] = {}
    required: list[str] = []

    for key in sorted(all_keys):
        values_for_key = [s[key] for s in samples if key in s]
        properties[key] = _infer_node(values_for_key)
        if all(key in s for s in samples):
            required.append(key)

    result: dict[str, Any] = {"properties": properties}
    if required:
        result["required"] = required
    return result


def _infer_array(samples: list[list]) -> dict:
    all_items: list[Any] = []
    for arr in samples:
        all_items.extend(arr)
    if not all_items:
        return {"items": {}}
    return {"items": _infer_node(all_items)}


def infer_schema(*documents: Any, title: str = "Inferred Schema") -> dict:
    """Infer a JSON Schema (draft-07) describing one or more sample documents.

    Accepts either several positional documents, or a single list of
    documents, e.g.::

        infer_schema(doc1, doc2, doc3)
        infer_schema([doc1, doc2, doc3])

    Multiple samples are merged so that fields missing from some samples
    are correctly omitted from ``required``, and fields whose type varies
    across samples are represented as a type union.
    """
    if len(documents) == 1 and isinstance(documents[0], list):
        samples = documents[0]
    else:
        samples = list(documents)

    if not samples:
        raise ValueError("infer_schema requires at least one sample document")

    schema = _infer_node(samples)
    ordered: dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": title,
    }
    ordered.update(schema)
    return ordered
