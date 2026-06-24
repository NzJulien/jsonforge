"""A small, dependency-free JSON Schema validator.

Supports a practical subset of JSON Schema draft-07: ``type``,
``properties``, ``required``, ``items``, ``enum``, ``minimum``/``maximum``,
``minLength``/``maxLength``, ``pattern``, ``anyOf`` and
``additionalProperties``. This is enough to validate schemas produced by
:mod:`jsonforge.inferencer`, as well as many hand-written schemas, without
pulling in an external dependency.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '$'}: {self.message}"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def __bool__(self) -> bool:
        return self.is_valid


_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "null": lambda v: v is None,
}


def _check_type(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_check_type(value, t) for t in expected)
    checker = _TYPE_CHECKS.get(expected)
    return checker(value) if checker else True


def validate(instance: Any, schema: dict, path: str = "$") -> ValidationResult:
    """Validate ``instance`` against ``schema``, returning a ValidationResult.

    The result is falsy-aware: ``if not validate(doc, schema): ...`` works
    directly thanks to ``ValidationResult.__bool__``.
    """
    result = ValidationResult()
    _validate_node(instance, schema, path, result)
    return result


def _validate_node(instance: Any, schema: dict, path: str, result: ValidationResult) -> None:
    if "anyOf" in schema:
        if not any(validate(instance, sub).is_valid for sub in schema["anyOf"]):
            result.errors.append(ValidationError(path, "does not match any schema in 'anyOf'"))
        return

    if "type" in schema and not _check_type(instance, schema["type"]):
        result.errors.append(
            ValidationError(path, f"expected type {schema['type']!r}, got {type(instance).__name__}")
        )
        return  # further structural checks aren't meaningful on a type mismatch

    if "enum" in schema and instance not in schema["enum"]:
        result.errors.append(ValidationError(path, f"value {instance!r} not in enum {schema['enum']!r}"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            result.errors.append(ValidationError(path, f"string shorter than minLength={schema['minLength']}"))
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            result.errors.append(ValidationError(path, f"string longer than maxLength={schema['maxLength']}"))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            result.errors.append(ValidationError(path, f"does not match pattern {schema['pattern']!r}"))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            result.errors.append(ValidationError(path, f"value {instance} < minimum {schema['minimum']}"))
        if "maximum" in schema and instance > schema["maximum"]:
            result.errors.append(ValidationError(path, f"value {instance} > maximum {schema['maximum']}"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for required_key in schema.get("required", []):
            if required_key not in instance:
                result.errors.append(ValidationError(path, f"missing required property {required_key!r}"))
        for key, value in instance.items():
            if key in properties:
                _validate_node(value, properties[key], f"{path}.{key}", result)
            elif schema.get("additionalProperties") is False:
                result.errors.append(ValidationError(f"{path}.{key}", "additional property not allowed"))

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                _validate_node(item, item_schema, f"{path}[{index}]", result)
