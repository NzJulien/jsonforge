from jsonforge.validator import validate

SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0, "maximum": 150},
        "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
    },
    "required": ["name", "age"],
}


def test_valid_document_passes():
    doc = {"name": "Ada", "age": 30, "email": "ada@example.com"}
    assert validate(doc, SCHEMA).is_valid


def test_missing_required_field_fails():
    result = validate({"age": 30}, SCHEMA)
    assert not result.is_valid
    assert any("name" in str(e) for e in result.errors)


def test_wrong_type_fails():
    result = validate({"name": "Ada", "age": "thirty"}, SCHEMA)
    assert not result.is_valid


def test_out_of_range_fails():
    result = validate({"name": "Ada", "age": 200}, SCHEMA)
    assert not result.is_valid


def test_pattern_mismatch_fails():
    result = validate({"name": "Ada", "age": 30, "email": "not-an-email"}, SCHEMA)
    assert not result.is_valid


def test_array_items_validated():
    schema = {"type": "array", "items": {"type": "integer"}}
    assert validate([1, 2, 3], schema).is_valid
    assert not validate([1, "two", 3], schema).is_valid


def test_enum_validation():
    schema = {"type": "string", "enum": ["red", "green", "blue"]}
    assert validate("green", schema).is_valid
    assert not validate("purple", schema).is_valid


def test_any_of():
    schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    assert validate("hello", schema).is_valid
    assert validate(42, schema).is_valid
    assert not validate(3.14, schema).is_valid


def test_additional_properties_false():
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}, "additionalProperties": False}
    assert validate({"a": 1}, schema).is_valid
    assert not validate({"a": 1, "b": 2}, schema).is_valid


def test_result_is_truthy_when_valid():
    result = validate({"name": "Ada", "age": 30}, SCHEMA)
    assert result  # __bool__
    assert bool(result) is True
