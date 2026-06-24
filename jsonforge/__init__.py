"""jsonforge — infer JSON Schemas, validate JSON documents, and diff JSON data.

A small, dependency-free toolkit for working with JSON structurally:

- ``infer_schema``: derive a JSON Schema (draft-07) from one or more sample
  documents, correctly detecting optional fields and type unions.
- ``validate``: validate a JSON document against a JSON Schema using a
  compact, zero-dependency validator.
- ``diff``: compute a structural, path-addressed diff between two JSON
  documents.
"""
from .inferencer import infer_schema
from .validator import validate, ValidationResult, ValidationError
from .differ import diff, Change

__version__ = "1.0.0"
__all__ = [
    "infer_schema",
    "validate",
    "ValidationResult",
    "ValidationError",
    "diff",
    "Change",
]
