from jsonforge.inferencer import infer_schema


def test_infers_basic_types():
    schema = infer_schema({"name": "Ada", "age": 30, "active": True})
    props = schema["properties"]
    assert props["name"]["type"] == "string"
    assert props["age"]["type"] == "integer"
    assert props["active"]["type"] == "boolean"


def test_detects_optional_fields_across_samples():
    samples = [
        {"name": "Ada", "nickname": "Lovelace"},
        {"name": "Grace"},
    ]
    schema = infer_schema(samples)
    assert "name" in schema["required"]
    assert "nickname" not in schema.get("required", [])


def test_infers_nested_objects_and_arrays():
    sample = {"user": {"id": 1, "tags": ["a", "b"]}}
    schema = infer_schema(sample)
    user_schema = schema["properties"]["user"]
    assert user_schema["type"] == "object"
    assert user_schema["properties"]["tags"]["type"] == "array"
    assert user_schema["properties"]["tags"]["items"]["type"] == "string"


def test_merges_int_and_float_into_number():
    samples = [{"score": 1}, {"score": 2.5}]
    schema = infer_schema(samples)
    assert schema["properties"]["score"]["type"] == "number"


def test_detects_type_union():
    samples = [{"id": 1}, {"id": "abc-123"}]
    schema = infer_schema(samples)
    assert sorted(schema["properties"]["id"]["type"]) == ["integer", "string"]


def test_requires_at_least_one_sample():
    try:
        infer_schema([])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_top_level_metadata_present():
    schema = infer_schema({"a": 1}, title="My Schema")
    assert schema["title"] == "My Schema"
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
