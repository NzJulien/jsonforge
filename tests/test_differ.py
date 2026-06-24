from jsonforge.differ import diff


def test_no_changes():
    assert diff({"a": 1}, {"a": 1}) == []


def test_detects_added_key():
    changes = diff({"a": 1}, {"a": 1, "b": 2})
    assert len(changes) == 1
    assert changes[0].kind == "added"
    assert changes[0].path == "$.b"


def test_detects_removed_key():
    changes = diff({"a": 1, "b": 2}, {"a": 1})
    assert changes[0].kind == "removed"
    assert changes[0].path == "$.b"


def test_detects_changed_value():
    changes = diff({"a": 1}, {"a": 2})
    assert changes[0].kind == "changed"
    assert changes[0].old == 1
    assert changes[0].new == 2


def test_nested_diff():
    old = {"user": {"name": "Ada", "tags": ["x"]}}
    new = {"user": {"name": "Grace", "tags": ["x", "y"]}}
    changes = diff(old, new)
    paths = {c.path for c in changes}
    assert "$.user.name" in paths
    assert "$.user.tags[1]" in paths


def test_int_to_float_not_flagged_as_type_change():
    changes = diff({"score": 1}, {"score": 1.0})
    assert changes == []


def test_list_shrink_detected_as_removed():
    changes = diff([1, 2, 3], [1, 2])
    assert len(changes) == 1
    assert changes[0].kind == "removed"
    assert changes[0].path == "$[2]"


def test_change_string_repr():
    changes = diff({"a": 1}, {"a": 2})
    assert str(changes[0]) == "~ $.a: 1 -> 2"
